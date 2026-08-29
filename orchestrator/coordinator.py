"""
协作协调器模块 - 多 Agent 协作核心引擎
"""
import time
from typing import Dict, List
from utils.logger import AgentLogger
from agents import DataReaderAgent, DataCleanerAgent, DataAnalystAgent, VisualizerAgent, ReportGeneratorAgent
from orchestrator.task_decomposer import TaskDecomposer
from orchestrator.result_aggregator import ResultAggregator


class Coordinator:
    """多 Agent 协作协调器 - 中介者模式 + 管道模式"""

    AGENT_CLASSES = {
        "DataReaderAgent": DataReaderAgent, "DataCleanerAgent": DataCleanerAgent,
        "DataAnalystAgent": DataAnalystAgent, "VisualizerAgent": VisualizerAgent,
        "ReportGeneratorAgent": ReportGeneratorAgent,
    }

    def __init__(self, run_mode="auto", logger=None, progress_callback=None):
        self.run_mode = run_mode
        self.logger = logger or AgentLogger("Coordinator")
        self.progress_callback = progress_callback
        self.task_decomposer = TaskDecomposer(run_mode=run_mode)
        self.result_aggregator = ResultAggregator(logger=self.logger)
        self.agents = {}
        self._init_agents()
        self.context = {}
        self.execution_results = []
        self.is_running = False

    def _init_agents(self):
        for name, cls in self.AGENT_CLASSES.items():
            self.agents[name] = cls(logger=self.logger, run_mode=self.run_mode)
        self.logger.info(f"初始化完成: {len(self.agents)} 个 Agent")

    def run(self, file_path, task_description="完整数据分析"):
        start = time.time()
        self.is_running = True
        self.context = {"file_path": file_path}
        self.execution_results = []
        self.logger.info("="*60)
        self.logger.info(f"开始多 Agent 协作任务: {task_description}")
        self.logger.info(f"数据文件: {file_path}")
        self.logger.info(f"运行模式: {self.run_mode}")
        self.logger.info("="*60)
        try:
            self.logger.info("步骤1: 任务拆解...")
            plan = self.task_decomposer.decompose(task_description, file_path)
            subtasks = plan["subtasks"]
            self.logger.info(f"任务拆解完成: {len(subtasks)} 个子任务")
            for st in subtasks:
                self.logger.info(f"  - [{st['id']}] {st['name']} -> {st['agent']}")
            for i, st in enumerate(subtasks, 1):
                if not self.is_running: break
                if self.progress_callback: self.progress_callback(i, len(subtasks), f"正在执行: {st['name']}")
                result = self._execute_agent(st["agent"], st)
                self.execution_results.append(result)
                if result["status"] == "error":
                    self.logger.error(f"子任务失败: {st['name']} - {result.get('message','')}")
                    if st["agent"] in ["DataReaderAgent","DataCleanerAgent"]:
                        self.logger.error("关键步骤失败，中止后续任务"); break
            final = self.result_aggregator.aggregate(self.context, self.execution_results, plan)
            final["total_time"] = round(time.time()-start, 2)
            final["run_mode"] = self.run_mode
            self.logger.success(f"任务完成! 总耗时: {final['total_time']}s")
        except Exception as e:
            self.logger.error(f"协调器执行异常: {str(e)}")
            final = {"status":"error","message":f"系统异常: {str(e)}","total_time":round(time.time()-start,2)}
        finally:
            self.is_running = False
        return final

    def _execute_agent(self, agent_name, subtask):
        if agent_name not in self.agents:
            return {"status":"error","agent_name":agent_name,"message":f"未知的 Agent: {agent_name}"}
        agent = self.agents[agent_name]
        self.logger.info(f"\\n--- 执行 Agent: {agent.name} ({agent.role}) ---")
        result = agent.execute(self.context)
        result["subtask_id"] = subtask["id"]
        result["subtask_name"] = subtask["name"]
        return result

    def stop(self): self.is_running = False; self.logger.warning("收到中止信号")
    def get_agent_info(self): return [a.get_info() for a in self.agents.values()]
    def get_execution_log(self): return self.logger.get_task_logs()
