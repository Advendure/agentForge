"""
Subagent Pattern - How to implement Task tool for context isolation.

The key insight: spawn child agents with ISOLATED context to prevent
"context pollution" where exploration details fill up the main conversation.
"""

import time
import sys


# =============================================================================
# AGENT TYPE REGISTRY
# =============================================================================

AGENT_TYPES = {
    "explore": {
        "description": "Read-only agent for exploring code, finding files, searching",
        "tools": ["bash", "read_file"],
        "prompt": "You are an exploration agent. Search and analyze, but NEVER modify files. Return a concise summary of what you found.",
    },

    "code": {
        "description": "Full agent for implementing features and fixing bugs",
        "tools": "*",
        "prompt": "You are a coding agent. Implement the requested changes efficiently. Return a summary of what you changed.",
    },

    "plan": {
        "description": "Planning agent for designing implementation strategies",
        "tools": ["bash", "read_file"],
        "prompt": "You are a planning agent. Analyze the codebase and output a numbered implementation plan. Do NOT make any changes.",
    },
}


def get_agent_descriptions() -> str:
    """Generate descriptions for Task tool schema."""
    return "\n".join(
        f"- {name}: {cfg['description']}"
        for name, cfg in AGENT_TYPES.items()
    )


def get_tools_for_agent(agent_type: str, base_tools: list) -> list:
    """
    Filter tools based on agent type.

    '*' means all base tools.
    Otherwise, whitelist specific tool names.

    Note: Subagents don't get Task tool to prevent infinite recursion.
    """
    allowed = AGENT_TYPES.get(agent_type, {}).get("tools", "*")

    if allowed == "*":
        return base_tools

    return [t for t in base_tools if t["name"] in allowed]


# =============================================================================
# TASK TOOL DEFINITION
# =============================================================================

TASK_TOOL = {
    "name": "Task",
    "description": f"""Spawn a subagent for a focused subtask.

Subagents run in ISOLATED context - they don't see parent's history.
Use this to keep the main conversation clean.

Agent types:
{get_agent_descriptions()}

Example uses:
- Task(explore): "Find all files using the auth module"
- Task(plan): "Design a migration strategy for the database"
- Task(code): "Implement the user registration form"
""",
    "input_schema": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Short task name (3-5 words) for progress display"
            },
            "prompt": {
                "type": "string",
                "description": "Detailed instructions for the subagent"
            },
            "agent_type": {
                "type": "string",
                "enum": list(AGENT_TYPES.keys()),
                "description": "Type of agent to spawn"
            },
        },
        "required": ["description", "prompt", "agent_type"],
    },
}


# =============================================================================
# SUBAGENT EXECUTION
# =============================================================================

def run_task(description: str, prompt: str, agent_type: str,
             client, model: str, workdir, base_tools: list, execute_tool) -> str:
    """
    Execute a subagent task with isolated context.

    Key concepts:
    1. ISOLATED HISTORY - subagent starts fresh, no parent context
    2. FILTERED TOOLS - based on agent type permissions
    3. AGENT-SPECIFIC PROMPT - specialized behavior
    4. RETURNS SUMMARY ONLY - parent sees just the final result

    Args:
        description: Short name for progress display
        prompt: Detailed instructions for subagent
        agent_type: Key from AGENT_TYPES
        client: Anthropic client
        model: Model to use
        workdir: Working directory
        base_tools: List of tool definitions
        execute_tool: Function to execute tools

    Returns:
        Final text output from subagent
    """
    if agent_type not in AGENT_TYPES:
        return f"Error: Unknown agent type '{agent_type}'"

    config = AGENT_TYPES[agent_type]

    sub_system = f"""You are a {agent_type} subagent at {workdir}.

{config["prompt"]}

Complete the task and return a clear, concise summary."""

    sub_tools = get_tools_for_agent(agent_type, base_tools)

    sub_messages = [{"role": "user", "content": prompt}]

    print(f"  [{agent_type}] {description}")
    start = time.time()
    tool_count = 0

    while True:
        response = client.messages.create(
            model=model,
            system=sub_system,
            messages=sub_messages,
            tools=sub_tools,
            max_tokens=8000,
        )

        if response.stop_reason != "tool_use":
            break

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        results = []

        for tc in tool_calls:
            tool_count += 1
            output = execute_tool(tc.name, tc.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": output
            })

            elapsed = time.time() - start
            sys.stdout.write(
                f"\r  [{agent_type}] {description} ... {tool_count} tools, {elapsed:.1f}s"
            )
            sys.stdout.flush()

        sub_messages.append({"role": "assistant", "content": response.content})
        sub_messages.append({"role": "user", "content": results})

    elapsed = time.time() - start
    sys.stdout.write(
        f"\r  [{agent_type}] {description} - done ({tool_count} tools, {elapsed:.1f}s)\n"
    )

    for block in response.content:
        if hasattr(block, "text"):
            return block.text

    return "(subagent returned no text)"


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

"""
# In your main agent's execute_tool function:

def execute_tool(name: str, args: dict) -> str:
    if name == "Task":
        return run_task(
            description=args["description"],
            prompt=args["prompt"],
            agent_type=args["agent_type"],
            client=client,
            model=MODEL,
            workdir=WORKDIR,
            base_tools=BASE_TOOLS,
            execute_tool=execute_tool
        )

# In your TOOLS list:
TOOLS = BASE_TOOLS + [TASK_TOOL]
"""