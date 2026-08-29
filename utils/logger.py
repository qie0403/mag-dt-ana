"""
日志工具模块
统一的日志记录器，支持控制台输出和文件存储
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR


class AgentLogger:
    """多 Agent 系统专用日志记录器"""

    def __init__(self, name="MultiAgentSystem", log_to_file=True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
        self.logger.addHandler(console_handler)

        if log_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = OUTPUT_DIR / f"run_{timestamp}.log"
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            self.logger.addHandler(fh)
            self.log_file = str(log_file)
        else:
            self.log_file = None

        self.task_logs = []

    def log_agent_action(self, agent_name, action, status="info", details=""):
        message = f"[{agent_name}] {action}"
        if details:
            message += f" - {details}"
        method = getattr(self.logger, status if status != "success" else "info", self.logger.info)
        method(message)
        self.task_logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent_name, "action": action,
            "status": status, "details": details,
        })

    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def debug(self, msg): self.logger.debug(msg)
    def success(self, msg): self.logger.info(f"[SUCCESS] {msg}")
    def get_task_logs(self): return self.task_logs.copy()
    def clear_task_logs(self): self.task_logs = []
