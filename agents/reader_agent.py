"""数据读取 Agent"""
from agents.base_agent import BaseAgent
from tools.data_tools import DataTools


class DataReaderAgent(BaseAgent):
    def __init__(self, logger=None, run_mode="auto"):
        super().__init__("DataReaderAgent", "数据读取专家", "负责读取和解析各类数据源文件", logger, run_mode)
        self.register_tool("read_file", DataTools.read_file)
        self.register_tool("get_data_overview", DataTools.get_data_overview)

    def _run(self, context):
        fp = context.get("file_path")
        if not fp: return {"status": "error", "message": "未提供文件路径"}
        self.logger.log_agent_action(self.name, f"正在读取文件: {fp}", "info")
        r = self.use_tool("read_file", file_path=fp)
        if not r["success"]: return {"status": "error", "message": f"文件读取失败: {r['error']}"}
        df, fi = r["df"], r["file_info"]
        self.logger.log_agent_action(self.name, f"读取成功: {fi['rows']}行 x {fi['columns']}列", "success")
        overview = self.use_tool("get_data_overview", df=df)
        context["raw_df"] = df; context["file_info"] = fi; context["data_overview"] = overview
        return {"status": "success", "message": f"数据读取完成: {fi['rows']}行 x {fi['columns']}列",
                "data": {"file_info": fi, "overview": overview, "preview": df.head(10).to_dict(orient="records")}}
