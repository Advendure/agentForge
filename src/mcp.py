import asyncio
import json
import re
import os
import threading
from pathlib import Path
from typing import Optional

from mcp import StdioServerParameters, ClientSession
from mcp import stdio_client as mcp_stdio_client

from src.config import WORKDIR

_DISALLOWED_CHARS = re.compile(r'[^a-zA-Z0-9_-]')


def normalize_mcp_name(name: str) -> str:
    return _DISALLOWED_CHARS.sub('_', name)


class MCPManager:
    def __init__(self):
        self.clients: dict[str, dict] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ensure_loop()

    def _ensure_loop(self):
        if self._loop is not None and self._loop.is_running():
            return
        self._loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def _run_async(self, coro):
        if not self._loop or not self._loop.is_running():
            self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=120)

    def _parse_command(self, command_config) -> tuple[str, list[str]]:
        if isinstance(command_config, list):
            return command_config[0], command_config[1:] if len(command_config) > 1 else []
        elif isinstance(command_config, dict):
            return command_config["command"], command_config.get("args", [])
        return str(command_config), []

    def connect(self, name: str, command_config, env: dict = None) -> str:
        if name in self.clients:
            return f"MCP server '{name}' already connected"

        try:
            command, args = self._parse_command(command_config)
            params = StdioServerParameters(
                command=command,
                args=args,
                env=env or os.environ.copy(),
                cwd=str(WORKDIR),
                encoding="utf-8",
            )
            result = self._run_async(self._connect_async(name, params))
            return result
        except Exception as e:
            return f"Error connecting MCP server '{name}': {type(e).__name__}: {e}"

    async def _connect_async(self, name: str, params: StdioServerParameters) -> str:
        read, write, proc = await mcp_stdio_client(params)
        session = ClientSession(read, write)
        await session.initialize()
        tools_result = await session.list_tools()
        tools = tools_result.tools

        self.clients[name] = {
            "session": session,
            "proc": proc,
            "tools": tools,
            "tool_names": [t.name for t in tools],
        }

        tool_names = [t.name for t in tools]
        print(f"  \033[31m[mcp] connected: {name} → {tool_names}\033[0m")
        return (f"Connected to MCP server '{name}'. "
                f"Discovered {len(tools)} tools: {', '.join(tool_names)}")

    def list_tools(self, name: str) -> list:
        if name not in self.clients:
            return []
        return self.clients[name]["tools"]

    def call_tool(self, server_name: str, tool_name: str, args: dict) -> str:
        if server_name not in self.clients:
            return f"Error: MCP server '{server_name}' not connected"
        try:
            return self._run_async(
                self._call_tool_async(server_name, tool_name, args))
        except Exception as e:
            return f"Error calling {server_name}.{tool_name}: {type(e).__name__}: {e}"

    async def _call_tool_async(self, server_name: str, tool_name: str,
                               args: dict) -> str:
        session = self.clients[server_name]["session"]
        result = await session.call_tool(tool_name, arguments=args)
        return self._format_result(result)

    def _format_result(self, result) -> str:
        if hasattr(result, 'content'):
            parts = []
            for item in result.content:
                if hasattr(item, 'text'):
                    parts.append(item.text)
                elif isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    else:
                        parts.append(json.dumps(item, indent=2))
                else:
                    parts.append(str(item))
            text = "\n".join(parts) if parts else "(empty result)"
            if hasattr(result, 'isError') and result.isError:
                return f"[MCP Error] {text}"
            return text
        return str(result)

    def disconnect(self, name: str) -> str:
        if name not in self.clients:
            return f"MCP server '{name}' not connected"
        try:
            info = self.clients.pop(name)
            proc = info.get("proc")
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass
            return f"Disconnected MCP server '{name}'"
        except Exception as e:
            return f"Error disconnecting: {e}"

    def get_server_names(self) -> list[str]:
        return list(self.clients.keys())


mcp_manager = MCPManager()
mcp_clients = mcp_manager.clients

CONFIG_PATH = WORKDIR / "mcp_config.json"


def load_mcp_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception:
        return {}


def connect_mcp_by_config(name: str) -> str:
    config = load_mcp_config()
    servers = config.get("servers", {})
    server_config = servers.get(name)
    if not server_config:
        return f"Server '{name}' not found in mcp_config.json"
    command = server_config.get("command")
    if not command:
        return f"Server '{name}' has no command configured"
    env = server_config.get("env", {}) or {}
    merged_env = os.environ.copy()
    if env:
        for k, v in env.items():
            if v and "your-" not in str(v).lower():
                merged_env[k] = v
    return mcp_manager.connect(name, command, merged_env)


def auto_connect_mcp() -> list[str]:
    config = load_mcp_config()
    if not config.get("auto_connect"):
        return []
    results = []
    for name, server_config in config.get("servers", {}).items():
        if server_config.get("enabled") and server_config.get("command"):
            result = connect_mcp_by_config(name)
            results.append(result)
    return results


def connect_mcp(name: str, command: list | str = None, env: dict = None) -> str:
    if command is None:
        if CONFIG_PATH.exists():
            return connect_mcp_by_config(name)
        return f"Error: command is required. Example: connect_mcp('github', ['npx', '-y', '@modelcontextprotocol/server-github'])"
    return mcp_manager.connect(name, command, env)


def assemble_tool_pool() -> tuple[list[dict], dict]:
    from src.tool_defs import BUILTIN_TOOLS, BUILTIN_HANDLERS
    tools = list(BUILTIN_TOOLS)
    handlers = dict(BUILTIN_HANDLERS)

    for server_name in mcp_manager.get_server_names():
        safe_server = normalize_mcp_name(server_name)
        mcp_tools = mcp_manager.list_tools(server_name)
        for tool_obj in mcp_tools:
            tool_name = tool_obj.name
            safe_tool = normalize_mcp_name(tool_name)
            prefixed = f"mcp__{safe_server}__{safe_tool}"
            input_schema = getattr(tool_obj, 'inputSchema', {}) or {}
            description = getattr(tool_obj, 'description', '') or ''
            tools.append({
                "name": prefixed,
                "description": description,
                "input_schema": input_schema,
            })
            handlers[prefixed] = (
                lambda *, s=server_name, t=tool_name, **kw:
                    mcp_manager.call_tool(s, t, kw))
    return tools, handlers
