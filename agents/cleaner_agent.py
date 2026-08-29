"""数据清洗 Agent"""
from agents.base_agent import BaseAgent
from tools.data_tools import DataTools


class DataCleanerAgent(BaseAgent):
    def __init__(self, logger=None, run_mode="auto"):
        super().__init__("DataCleanerAgent", "数据清洗专家", "负责数据清洗、缺失值处理、异常值检测", logger, run_mode)
        self.register_tool("clean_data", DataTools.clean_data)

    def _run(self, context):
        raw = context.get("raw_df")
        if raw is None: return {"status": "error", "message": "上下文中未找到原始数据"}
        r = self.use_tool("clean_data", df=raw)
        cleaned, report = r["df"], r["report"]
        for s in report["steps"]:
            d = f"移除{s.get('removed',0)}行" if "removed" in s else f"填充{s.get('filled',0)}个缺失值" if "filled" in s else f"检测到{len(s.get('outliers',{}))}列异常值"
            self.logger.log_agent_action(self.name, f"步骤: {s['step']} - {d}", "info")
        self.logger.log_agent_action(self.name, f"清洗完成: {report['original_rows']}行 -> {report['final_rows']}行", "success")
        context["cleaned_df"] = cleaned; context["clean_report"] = report
        return {"status": "success", "message": f"数据清洗完成，移除{report['rows_removed']}行",
                "data": {"clean_report": report, "before_shape": [report['original_rows'],report['original_columns']],
                          "after_shape": [report['final_rows'],report['final_columns']]}}
