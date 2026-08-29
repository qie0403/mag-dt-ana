"""结果汇总模块"""
from typing import Dict, List
from utils.logger import AgentLogger


class ResultAggregator:
    def __init__(self, logger=None): self.logger = logger or AgentLogger("ResultAggregator")

    def aggregate(self, context, results, task_plan):
        sc = sum(1 for r in results if r.get("status")=="success")
        ec = sum(1 for r in results if r.get("status")=="error")
        tt = sum(r.get("elapsed_time",0) for r in results)
        details = [{"agent":r.get("agent_name",""),"subtask":r.get("subtask_name",""),
                    "status":r.get("status",""),"message":r.get("message",""),
                    "elapsed_time":r.get("elapsed_time",0)} for r in results]
        return {
            "status": "success" if ec==0 else "partial",
            "summary": {"total_tasks":len(results),"success_count":sc,"error_count":ec,
                        "success_rate":f"{sc/max(len(results),1)*100:.1f}%","total_agent_time":round(tt,2)},
            "agent_details": details,
            "task_plan": {"original_task":task_plan.get("original_task",""),
                          "pipeline_type":task_plan.get("pipeline_type",""),
                          "detected_agents":task_plan.get("detected_agents",[])},
            "outputs": {"report_path":context.get("report_path"),"json_path":context.get("json_path"),
                       "report_content":context.get("report_content"),
                       "chart_count":len(context.get("charts",[])),"charts":context.get("charts",[])},
            "data_info": {"file_info":context.get("file_info",{}),
                          "rows":context.get("file_info",{}).get("rows",0),
                          "columns":context.get("file_info",{}).get("columns",0)},
            "key_insights": context.get("analysis_results",{}).get("key_insights",[]),
        }
