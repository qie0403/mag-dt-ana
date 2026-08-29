"""
Agent 基类模块
"""
import time
from abc import ABC, abstractmethod
from utils.logger import AgentLogger


class BaseAgent(ABC):
    """Agent 抽象基类 - 模板方法模式"""

    def __init__(self, name, role, description, logger=None, run_mode="auto"):
        self.name = name
        self.role = role
        self.description = description
        self.logger = logger or AgentLogger(name)
        self.run_mode = run_mode
        self.tools = {}
        self.execution_history = []

    def register_tool(self, tool_name, tool_func):
        self.tools[tool_name] = tool_func

    def use_tool(self, tool_name, **kwargs):
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 未在 Agent '{self.name}' 中注册")
        self.logger.log_agent_action(self.name, f"调用工具: {tool_name}", "info")
        return self.tools[tool_name](**kwargs)

    @abstractmethod
    def _run(self, context):
        pass

    def execute(self, context):
        start = time.time()
        self.logger.log_agent_action(self.name, f"开始执行 - {self.role}", "info")
        try:
            result = self._run(context)
            elapsed = time.time() - start
            if not isinstance(result, dict): result = {"status": "success", "data": result}
            result.setdefault("status", "success")
            result.setdefault("message", f"{self.name} 执行完成")
            result["elapsed_time"] = round(elapsed, 3)
            result["agent_name"] = self.name
            self.logger.log_agent_action(self.name, f"执行完成，耗时 {elapsed:.2f}s", "success")
        except Exception as e:
            elapsed = time.time() - start
            result = {"status": "error", "agent_name": self.name,
                      "message": f"{self.name} 执行失败: {str(e)}", "error": str(e),
                      "elapsed_time": round(elapsed, 3)}
            self.logger.log_agent_action(self.name, f"执行失败: {str(e)}", "error")
        self.execution_history.append(result)
        return result

    def get_info(self):
        return {"name": self.name, "role": self.role, "description": self.description,
                "tools": list(self.tools.keys()), "run_mode": self.run_mode}
