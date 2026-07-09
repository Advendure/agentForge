#!/usr/bin/env python3
"""
Modular Integration Test Script
验证所有模块能否正常导入和协作
"""

import sys
import os
import traceback
from pathlib import Path

TEST_DIR = Path(__file__).parent
sys.path.insert(0, str(TEST_DIR))

PASS = 0
FAIL = 0
ERRORS = []


def test_import(module_name, description=""):
    """测试单个模块的导入"""
    global PASS, FAIL, ERRORS
    try:
        __import__(module_name)
        PASS += 1
        print(f"  ✓ {description or module_name}")
        return True
    except Exception as e:
        FAIL += 1
        err_msg = f"{description or module_name}: {type(e).__name__}: {e}"
        ERRORS.append(err_msg)
        print(f"  ✗ {description or module_name}")
        print(f"    错误: {type(e).__name__}: {e}")
        return False


def test_function(func, args=None, description=""):
    """测试单个函数调用"""
    global PASS, FAIL, ERRORS
    try:
        if args is None:
            result = func()
        else:
            result = func(**args)
        PASS += 1
        print(f"  ✓ {description or func.__name__}")
        return result
    except Exception as e:
        FAIL += 1
        err_msg = f"{description or func.__name__}: {type(e).__name__}: {e}"
        ERRORS.append(err_msg)
        print(f"  ✗ {description or func.__name__}")
        print(f"    错误: {type(e).__name__}: {e}")
        return None


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    print("\n" + "="*60)
    print("  模块化代码集成测试")
    print("="*60)

    section("1. 基础模块导入测试")

    test_import("src.config", "config (配置模块)")
    test_import("src.utils", "utils (工具函数)")

    section("2. 核心功能模块导入测试")

    test_import("src.task_system", "task_system (任务系统)")
    test_import("src.worktree", "worktree (工作树系统)")
    test_import("src.skills", "skills (技能系统)")
    test_import("src.prompts", "prompts (提示词组装)")

    section("3. 工具模块导入测试")

    test_import("src.tools", "tools (工具包)")
    test_import("src.tools.bash_tool", "tools.bash_tool")
    test_import("src.tools.file_tools", "tools.file_tools")
    test_import("src.tools.todo_tool", "tools.todo_tool")

    section("4. 协作模块导入测试")

    test_import("src.message_bus", "message_bus (消息总线)")
    test_import("src.protocol", "protocol (协议系统)")
    test_import("src.subagent", "subagent (子代理)")
    test_import("src.teammate", "teammate (队友系统)")

    section("5. 系统模块导入测试")

    test_import("src.hooks", "hooks (钩子系统)")
    test_import("src.compaction", "compaction (上下文压缩)")
    test_import("src.error_recovery", "error_recovery (错误恢复)")
    test_import("src.background", "background (后台任务)")
    test_import("src.cron_scheduler", "cron_scheduler (Cron调度)")
    test_import("src.mcp", "mcp (MCP系统)")

    section("6. 主入口模块导入测试")

    test_import("src.tool_defs", "tool_defs (工具定义)")
    test_import("src.agent_loop", "agent_loop (代理循环)")
    test_import("src", "src (包入口)")

    section("7. 任务系统功能测试")

    from src.task_system import create_task, list_tasks, claim_task, complete_task

    test_function(
        lambda: create_task("测试任务", "这是一个测试任务"),
        description="创建任务"
    )
    test_function(list_tasks, description="列出任务")

    section("8. 文件工具功能测试")

    from src.tools.file_tools import run_read, run_write, run_edit, run_glob, safe_path

    test_file = ".test_temp.txt"
    test_function(
        lambda: run_write(test_file, "Hello, World!"),
        description="写入文件"
    )
    test_function(
        lambda: run_read(test_file),
        description="读取文件"
    )
    test_function(
        lambda: run_edit(test_file, "Hello", "Hi"),
        description="编辑文件"
    )
    test_function(
        lambda: run_glob(".test_*.txt"),
        description="文件匹配(glob)"
    )
    try:
        Path(test_file).unlink()
    except:
        pass

    section("9. Bash 工具功能测试")

    from src.tools.bash_tool import run_bash

    test_function(
        lambda: run_bash("echo hello"),
        description="执行简单命令"
    )

    section("10. Todo 工具功能测试")

    from src.tools.todo_tool import run_todo_write

    test_function(
        lambda: run_todo_write([
            {"content": "任务1", "status": "pending"},
            {"content": "任务2", "status": "in_progress"}
        ]),
        description="更新 Todo 列表"
    )

    section("11. 消息总线功能测试")

    from src.message_bus import MessageBus, BUS

    test_function(
        lambda: BUS.send("test_a", "test_b", "hello"),
        description="发送消息"
    )
    test_function(
        lambda: BUS.read_inbox("test_b"),
        description="读取收件箱"
    )

    section("12. Cron 调度器功能测试")

    from src.cron_scheduler import (
        validate_cron, schedule_job, cancel_job, run_list_crons
    )

    test_function(
        lambda: validate_cron("* * * * *"),
        description="验证有效 cron 表达式"
    )
    test_function(
        lambda: validate_cron("invalid"),
        description="验证无效 cron 表达式"
    )
    test_function(
        lambda: schedule_job("*/5 * * * *", "test cron", durable=False),
        description="调度 cron 任务"
    )
    test_function(run_list_crons, description="列出 cron 任务")

    from src.cron_scheduler import scheduled_jobs
    for job_id in list(scheduled_jobs.keys()):
        cancel_job(job_id)

    section("13. MCP 系统功能测试")

    from src.mcp import (
        connect_mcp, mcp_clients, assemble_tool_pool,
        normalize_mcp_name, mcp_manager, load_mcp_config
    )

    test_function(
        lambda: normalize_mcp_name("test-server"),
        description="MCP 名称规范化"
    )
    test_function(load_mcp_config, description="加载 MCP 配置文件")
    test_function(
        lambda: mcp_manager.get_server_names(),
        description="获取已连接服务器列表"
    )
    test_function(
        lambda: connect_mcp("test-missing-server"),
        description="连接不存在的服务器（错误处理）"
    )
    test_function(assemble_tool_pool, description="组装工具池（无 MCP 时）")

    section("14. 技能系统功能测试")

    from src.skills import list_skills, load_skill, scan_skills

    test_function(scan_skills, description="扫描技能")
    test_function(list_skills, description="列出技能")

    section("15. 上下文压缩功能测试")

    from src.compaction import (
        estimate_size, message_has_tool_use, is_tool_result_message,
        micro_compact, snip_compact
    )

    test_messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    test_function(
        lambda: estimate_size(test_messages),
        description="估算消息大小"
    )
    test_function(
        lambda: message_has_tool_use(test_messages[1]),
        description="检测工具使用"
    )
    test_function(
        lambda: is_tool_result_message(test_messages[0]),
        description="检测工具结果消息"
    )
    test_function(
        lambda: micro_compact(test_messages.copy()),
        description="微型压缩"
    )
    test_function(
        lambda: snip_compact(test_messages.copy(), 10),
        description="裁剪压缩"
    )

    section("16. 错误恢复功能测试")

    from src.error_recovery import RecoveryState, is_prompt_too_long_error

    test_function(
        lambda: RecoveryState(),
        description="创建恢复状态"
    )
    test_function(
        lambda: is_prompt_too_long_error(ValueError("prompt is too long")),
        description="检测 prompt 过长错误"
    )

    section("17. 后台任务功能测试")

    from src.background import is_slow_operation, should_run_background

    test_function(
        lambda: is_slow_operation("bash", {"command": "npm install"}),
        description="检测慢操作"
    )
    test_function(
        lambda: should_run_background("bash", {"command": "echo hi", "run_in_background": True}),
        description="判断是否后台运行"
    )

    section("18. 钩子系统功能测试")

    from src.hooks import register_hook, trigger_hooks, HOOKS

    def test_hook(*args):
        return None

    test_function(
        lambda: register_hook("UserPromptSubmit", test_hook),
        description="注册钩子"
    )
    test_function(
        lambda: trigger_hooks("UserPromptSubmit", "test"),
        description="触发钩子"
    )

    section("19. 模块协作集成测试")

    from src.task_system import create_task
    from src.message_bus import BUS

    def test_task_message_integration():
        task = create_task("集成测试任务", "测试模块协作")
        BUS.send("system", "user", f"任务已创建: {task.id}")
        msgs = BUS.read_inbox("user")
        return len(msgs) == 1 and task.id in msgs[0]["content"]

    test_function(test_task_message_integration, description="任务系统 + 消息总线 协作")

    from src.mcp import assemble_tool_pool, normalize_mcp_name

    def test_mcp_tool_integration():
        tools, handlers = assemble_tool_pool()
        mcp_tools = [t for t in tools if t["name"].startswith("mcp__")]
        name_ok = normalize_mcp_name("test-server-name") == "test-server-name"
        return name_ok and isinstance(mcp_tools, list)

    test_function(test_mcp_tool_integration, description="MCP + 工具池 协作")

    from src.cron_scheduler import schedule_job, cancel_job
    from src.compaction import estimate_size

    def test_cron_compaction_integration():
        job = schedule_job("* * * * *", "test", durable=False)
        if isinstance(job, str):
            return False
        size = estimate_size([{"role": "user", "content": job.id}])
        cancel_job(job.id)
        return size > 0

    test_function(test_cron_compaction_integration, description="Cron + 压缩 协作")

    section("测试结果汇总")

    total = PASS + FAIL
    print(f"\n  总计: {total} 项测试")
    print(f"  通过: {PASS} 项")
    print(f"  失败: {FAIL} 项")
    print(f"  通过率: {PASS/total*100:.1f}%" if total > 0 else "  无测试")

    if ERRORS:
        print(f"\n  错误详情:")
        for i, err in enumerate(ERRORS, 1):
            print(f"    {i}. {err}")

    print(f"\n{'='*60}\n")

    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)