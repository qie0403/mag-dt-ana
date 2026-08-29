"""可视化 Agent"""
import numpy as np
from agents.base_agent import BaseAgent
from tools.visualization_tools import VisualizationTools


class VisualizerAgent(BaseAgent):
    def __init__(self, logger=None, run_mode="auto"):
        super().__init__("VisualizerAgent", "可视化专家", "负责根据数据特征自动生成各类可视化图表", logger, run_mode)
        for n, f in [("histogram",VisualizationTools.histogram),("boxplot",VisualizationTools.boxplot),
                     ("correlation_heatmap",VisualizationTools.correlation_heatmap),("bar_chart",VisualizationTools.bar_chart),
                     ("scatter_plot",VisualizationTools.scatter_plot),("line_chart",getattr(VisualizationTools,"line_chart",None)),
                     ("pie_chart",VisualizationTools.pie_chart),("missing_value_heatmap",VisualizationTools.missing_value_heatmap)]:
            if f: self.register_tool(n, f)

    def _run(self, context):
        df = context.get("cleaned_df")
        if df is None: df = context.get("raw_df")
        if df is None: return {"status": "error", "message": "上下文中未找到数据"}
        charts = []
        nc = df.select_dtypes(include=[np.number]).columns.tolist()
        cc = [c for c in df.columns if c not in nc and df[c].nunique() <= 20]
        self.logger.log_agent_action(self.name, f"开始生成图表: {len(nc)}个数值列, {len(cc)}个类别列", "info")
        for col in nc[:3]:
            try:
                r = self.use_tool("histogram", df=df, column=col)
                if "path" in r: charts.append(r); self.logger.log_agent_action(self.name, f"生成直方图: {col}", "success")
            except Exception as e: self.logger.log_agent_action(self.name, f"直方图失败 {col}: {e}", "warning")
        if len(nc) >= 2:
            try:
                r = self.use_tool("correlation_heatmap", df=df)
                if "path" in r: charts.append(r); self.logger.log_agent_action(self.name, "生成相关性热力图", "success")
            except Exception as e: self.logger.log_agent_action(self.name, f"热力图失败: {e}", "warning")
        for col in nc[:2]:
            try:
                r = self.use_tool("boxplot", df=df, column=col, group_col=cc[0] if cc else None)
                if "path" in r: charts.append(r); self.logger.log_agent_action(self.name, f"生成箱线图: {col}", "success")
            except Exception as e: self.logger.log_agent_action(self.name, f"箱线图失败 {col}: {e}", "warning")
        if cc and nc:
            try:
                r = self.use_tool("bar_chart", df=df, category_col=cc[0], value_col=nc[0])
                if "path" in r: charts.append(r); self.logger.log_agent_action(self.name, f"生成柱状图: {cc[0]} vs {nc[0]}", "success")
            except Exception as e: self.logger.log_agent_action(self.name, f"柱状图失败: {e}", "warning")
        for sc in context.get("analysis_results",{}).get("correlation_analysis",{}).get("strong_correlations",[])[:2]:
            try:
                r = self.use_tool("scatter_plot", df=df, x_col=sc["var1"], y_col=sc["var2"])
                if "path" in r: charts.append(r); self.logger.log_agent_action(self.name, f"生成散点图: {sc['var1']} vs {sc['var2']}", "success")
            except Exception as e: self.logger.log_agent_action(self.name, f"散点图失败: {e}", "warning")
        if cc:
            try:
                r = self.use_tool("pie_chart", df=df, column=cc[0])
                if "path" in r: charts.append(r); self.logger.log_agent_action(self.name, f"生成饼图: {cc[0]}", "success")
            except Exception as e: self.logger.log_agent_action(self.name, f"饼图失败: {e}", "warning")
        self.logger.log_agent_action(self.name, f"可视化完成: 共生成{len(charts)}张图表", "success")
        context["charts"] = charts
        return {"status": "success", "message": f"可视化完成，生成{len(charts)}张图表", "data": {"charts": charts, "chart_count": len(charts)}}
