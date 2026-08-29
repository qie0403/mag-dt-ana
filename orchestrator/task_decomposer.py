"""任务拆解模块"""
from typing import List, Dict


class TaskDecomposer:
    KEYWORD_AGENT_MAP = {
        "读取":"DataReaderAgent","加载":"DataReaderAgent","导入":"DataReaderAgent","read":"DataReaderAgent",
        "清洗":"DataCleanerAgent","预处理":"DataCleanerAgent","缺失值":"DataCleanerAgent","去重":"DataCleanerAgent","clean":"DataCleanerAgent",
        "分析":"DataAnalystAgent","统计":"DataAnalystAgent","相关性":"DataAnalystAgent","趋势":"DataAnalystAgent",
        "分组":"DataAnalystAgent","聚合":"DataAnalystAgent","analyze":"DataAnalystAgent",
        "可视化":"VisualizerAgent","图表":"VisualizerAgent","画图":"VisualizerAgent","绘图":"VisualizerAgent","visualize":"VisualizerAgent",
        "报告":"ReportGeneratorAgent","报表":"ReportGeneratorAgent","总结":"ReportGeneratorAgent","导出":"ReportGeneratorAgent","report":"ReportGeneratorAgent",
    }
    DEFAULT_PIPELINE = ["DataReaderAgent","DataCleanerAgent","DataAnalystAgent","VisualizerAgent","ReportGeneratorAgent"]

    def __init__(self, run_mode="auto"): self.run_mode = run_mode

    def decompose(self, task_description, file_path=None):
        full_kws = ["完整","全部","全流程","综合分析","full","all","complete","端到端"]
        is_full = any(k.lower() in task_description.lower() for k in full_kws)
        detected = self._detect(task_description)
        if is_full or not detected:
            detected = self.DEFAULT_PIPELINE.copy()
        else:
            downstream = {"DataAnalystAgent","VisualizerAgent","ReportGeneratorAgent"}
            if any(a in detected for a in downstream):
                detected.add("DataReaderAgent"); detected.add("DataCleanerAgent")
            detected = list(detected)
        ordered = [a for a in self.DEFAULT_PIPELINE if a in detected]
        subtasks = self._gen_subtasks(ordered, file_path)
        return {"original_task": task_description, "detected_agents": ordered,
                "subtasks": subtasks, "total_steps": len(subtasks),
                "pipeline_type": "full" if len(ordered)==5 else "custom"}

    def _detect(self, desc):
        d = set()
        for kw, agent in self.KEYWORD_AGENT_MAP.items():
            if kw.lower() in desc.lower(): d.add(agent)
        return d

    def _gen_subtasks(self, agents, file_path):
        tpl = {
            "DataReaderAgent": {"name":"数据读取","description":"读取数据文件并生成概览","agent":"DataReaderAgent","inputs":["file_path"],"outputs":["raw_df","file_info","data_overview"]},
            "DataCleanerAgent": {"name":"数据清洗","description":"去重、填充缺失值、检测异常值","agent":"DataCleanerAgent","inputs":["raw_df"],"outputs":["cleaned_df","clean_report"]},
            "DataAnalystAgent": {"name":"数据分析","description":"统计分析、相关性、分组聚合、趋势分析","agent":"DataAnalystAgent","inputs":["cleaned_df"],"outputs":["analysis_results"]},
            "VisualizerAgent": {"name":"可视化","description":"生成各类可视化图表","agent":"VisualizerAgent","inputs":["cleaned_df","analysis_results"],"outputs":["charts"]},
            "ReportGeneratorAgent": {"name":"报告生成","description":"汇总结果生成报告","agent":"ReportGeneratorAgent","inputs":["file_info","data_overview","clean_report","analysis_results","charts"],"outputs":["report_path","json_path"]},
        }
        st = []
        for i, a in enumerate(agents, 1):
            if a in tpl:
                t = tpl[a].copy(); t["id"] = i; t["status"] = "pending"
                if file_path and "file_path" in t["inputs"]: t["file_path"] = file_path
                st.append(t)
        return st
