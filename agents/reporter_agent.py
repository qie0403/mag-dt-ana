"""报告生成 Agent"""
import base64
import json
import os
from datetime import datetime
from pathlib import Path
from agents.base_agent import BaseAgent
from config import OUTPUT_DIR
from utils.helpers import timestamp_str, save_json


class ReportGeneratorAgent(BaseAgent):
    def __init__(self, logger=None, run_mode="auto"):
        super().__init__("ReportGeneratorAgent", "报告生成专家", "负责汇总所有分析结果并生成完整报告", logger, run_mode)

    def _run(self, context):
        self.logger.log_agent_action(self.name, "开始生成分析报告...", "info")
        fi = context.get("file_info", {})
        ov = context.get("data_overview", {})
        cr = context.get("clean_report", {})
        ar = context.get("analysis_results", {})
        charts = context.get("charts", [])
        report = self._gen_md(fi, ov, cr, ar, charts)
        rp = OUTPUT_DIR / f"analysis_report_{timestamp_str()}.md"
        with open(rp, "w", encoding="utf-8") as f: f.write(report)
        jp = OUTPUT_DIR / f"analysis_data_{timestamp_str()}.json"
        save_json({"report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "file_info": fi,
                   "data_overview": ov, "clean_report": cr, "analysis_results": ar,
                   "charts": [{"type": c.get("type"), "title": c.get("title"), "path": c.get("path")} for c in charts]}, jp)
        self.logger.log_agent_action(self.name, f"报告生成完成: {rp.name}", "success")
        context["report_path"] = str(rp); context["json_path"] = str(jp); context["report_content"] = report
        return {"status": "success", "message": f"报告生成完成: {rp.name}",
                "data": {"report_path": str(rp), "json_path": str(jp), "report_content": report, "chart_count": len(charts)}}

    def _gen_md(self, fi, ov, cr, ar, charts):
        L = ["# 数据分析报告", f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             f"**数据文件**: {fi.get('filename','N/A')}", f"**数据规模**: {fi.get('rows','N/A')} 行 x {fi.get('columns','N/A')} 列", ""]
        L += ["## 一、数据概览", "", f"- **数据维度**: {ov.get('shape',{}).get('rows','N/A')} 行 x {ov.get('shape',{}).get('columns','N/A')} 列",
              f"- **重复行数**: {ov.get('duplicate_count',0)}", f"- **内存占用**: {fi.get('memory_usage','N/A')}", "",
              "### 字段详情", "", "| 字段名 | 类型 | 非空数 | 缺失数 | 缺失率 | 唯一值 |", "|---|---|---|---|---|---|"]
        for c in ov.get("columns", []):
            L.append(f"| {c['name']} | {c['dtype']} | {c['non_null']} | {c['missing']} | {c['missing_rate']} | {c['unique']} |")
        L += ["", "## 二、数据清洗", ""]
        if cr:
            L += [f"- **原始数据**: {cr.get('original_rows','N/A')} 行", f"- **清洗后**: {cr.get('final_rows','N/A')} 行",
                  f"- **移除行数**: {cr.get('rows_removed',0)}", "", "### 清洗步骤", ""]
            for s in cr.get("steps", []):
                L.append(f"1. **{s.get('step','')}**")
                if "removed" in s: L.append(f"   - 移除重复行: {s['removed']} 行")
                if "filled" in s: L.append(f"   - 填充缺失值: {s['filled']} 个")
                if s.get("outliers"): L.append(f"   - 异常值列: {', '.join(s['outliers'].keys())}")
        L += ["", "## 三、统计分析", ""]
        desc = ar.get("descriptive_statistics", {})
        if desc.get("numeric_summary"):
            L += ["### 3.1 描述性统计", "", "| 字段 | 均值 | 标准差 | 最小值 | 中位数 | 最大值 | 偏度 |", "|---|---|---|---|---|---|---|"]
            for col, s in desc["numeric_summary"].items():
                L.append(f"| {col} | {s.get('mean','N/A')} | {s.get('std','N/A')} | {s.get('min','N/A')} | {s.get('50%','N/A')} | {s.get('max','N/A')} | {s.get('skewness','N/A')} |")
        corr = ar.get("correlation_analysis", {})
        if corr.get("strong_correlations"):
            L += ["", "### 3.2 相关性分析", "", "| 变量1 | 变量2 | 相关系数 | 强度 | 方向 |", "|---|---|---|---|---|"]
            for sc in corr["strong_correlations"]:
                L.append(f"| {sc['var1']} | {sc['var2']} | {sc['correlation']} | {sc['strength']} | {sc['direction']} |")
        L += ["", "## 四、关键洞察", ""]
        for i, ins in enumerate(ar.get("key_insights", []), 1): L.append(f"{i}. {ins}")
        if charts:
            L += ["", "## 五、可视化图表", ""]
            for i, ch in enumerate(charts, 1):
                L += [f"### {i}. {ch.get('title',f'图表{i}')}", ""]
                if ch.get("path") and os.path.exists(ch["path"]):
                    with open(ch["path"], "rb") as img_f:
                        img_b64 = base64.b64encode(img_f.read()).decode()
                    L.append(f"![{ch.get('title','')}](data:image/png;base64,{img_b64})")
                elif ch.get("path"):
                    L.append(f"![{ch.get('title','')}](./{Path(ch['path']).name})")
                L.append("")
        L += ["---", "*本报告由多 Agent 协作自动化数据分析系统自动生成*"]
        return "\n".join(L)
