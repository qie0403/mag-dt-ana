"""数据分析 Agent"""
import numpy as np
import pandas as pd
from agents.base_agent import BaseAgent
from tools.analysis_tools import AnalysisTools


class DataAnalystAgent(BaseAgent):
    def __init__(self, logger=None, run_mode="auto"):
        super().__init__("DataAnalystAgent", "数据分析专家", "负责统计分析、相关性分析、分组聚合和趋势洞察", logger, run_mode)
        self.register_tool("descriptive_statistics", AnalysisTools.descriptive_statistics)
        self.register_tool("correlation_analysis", AnalysisTools.correlation_analysis)
        self.register_tool("groupby_analysis", AnalysisTools.groupby_analysis)
        self.register_tool("trend_analysis", AnalysisTools.trend_analysis)

    def _run(self, context):
        df = context.get("cleaned_df")
        if df is None: df = context.get("raw_df")
        if df is None: return {"status": "error", "message": "上下文中未找到数据"}
        results = {}
        self.logger.log_agent_action(self.name, "执行描述性统计分析...", "info")
        desc = self.use_tool("descriptive_statistics", df=df)
        results["descriptive_statistics"] = desc
        self.logger.log_agent_action(self.name, f"描述性统计完成: {len(desc['numeric_summary'])}个数值列", "success")

        self.logger.log_agent_action(self.name, "执行相关性分析...", "info")
        corr = self.use_tool("correlation_analysis", df=df)
        results["correlation_analysis"] = corr
        self.logger.log_agent_action(self.name, f"相关性分析完成: 发现{len(corr.get('strong_correlations',[]))}对显著相关变量", "success")

        nc = df.select_dtypes(include=[np.number]).columns.tolist()
        cc = [c for c in df.columns if c not in nc and df[c].nunique() <= 20]
        if cc and nc:
            self.logger.log_agent_action(self.name, "执行分组聚合分析...", "info")
            gr = []
            for cat in cc[:3]:
                r = self.use_tool("groupby_analysis", df=df, group_col=cat, agg_col=nc[0])
                if "error" not in r: gr.append(r)
            results["groupby_analysis"] = gr
            self.logger.log_agent_action(self.name, f"分组聚合完成: {len(gr)}个维度", "success")

        date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
        if not date_cols:
            for c in df.columns:
                if df[c].dtype == "object":
                    try: pd.to_datetime(df[c].head(100)); date_cols.append(c)
                    except (ValueError, TypeError): pass
        if date_cols and nc:
            self.logger.log_agent_action(self.name, "执行时间趋势分析...", "info")
            tr = self.use_tool("trend_analysis", df=df, date_col=date_cols[0], value_col=nc[0])
            if "error" not in tr:
                results["trend_analysis"] = tr
                self.logger.log_agent_action(self.name, f"趋势分析完成: {tr['trend']['direction']}, R2={tr['trend']['r_squared']}", "success")

        insights = list(desc.get("key_insights", []))
        for sc in corr.get("strong_correlations", [])[:5]:
            insights.append(f"'{sc['var1']}' 与 '{sc['var2']}' 呈{sc['strength']}{sc['direction']} (r={sc['correlation']})")
        insights.append(f"数据集包含 {len(df)} 条记录、{len(df.columns)} 个字段")
        results["key_insights"] = insights
        context["analysis_results"] = results
        return {"status": "success", "message": f"数据分析完成，生成{len(insights)}条关键洞察", "data": results}
