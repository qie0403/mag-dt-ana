"""
可视化工具模块
"""
import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from config import OUTPUT_DIR, PLOT_DPI, PLOT_FIGSIZE, CHART_FORMAT
from utils.helpers import safe_filename, timestamp_str

# 微软雅黑同时带 Regular(msyh.ttc) 与 Bold(msyhbd.ttc)，
# 能正确匹配 fontweight="bold"，避免 SimHei 无 bold 字重触发的 findfont 警告。
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
# 双保险：压掉 findfont 在缺字重时往 stderr 打的冗余日志
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)


class VisualizationTools:
    """可视化工具集合"""

    @staticmethod
    def _save(fig, name):
        fp = OUTPUT_DIR / f"{safe_filename(name)}_{timestamp_str()}.{CHART_FORMAT}"
        fig.savefig(fp, dpi=PLOT_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return str(fp)

    @staticmethod
    def histogram(df, column, title=None):
        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
        data = df[column].dropna()
        ax.hist(data, bins=min(30, max(10, len(data)//10)), edgecolor="black", alpha=0.7, color="#3498db")
        ax.axvline(data.mean(), color="red", linestyle="--", linewidth=2, label=f"均值: {data.mean():.2f}")
        ax.axvline(data.median(), color="green", linestyle="--", linewidth=2, label=f"中位数: {data.median():.2f}")
        ax.set_title(title or f"{column} 分布直方图", fontsize=14, fontweight="bold")
        ax.set_xlabel(column); ax.set_ylabel("频数"); ax.legend(); ax.grid(axis="y", alpha=0.3)
        return {"path": VisualizationTools._save(fig, f"histogram_{column}"), "type": "histogram", "column": column, "title": title or f"{column} 分布直方图"}

    @staticmethod
    def boxplot(df, column, group_col=None, title=None):
        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
        if group_col and group_col in df.columns and df[group_col].nunique() <= 15:
            groups = df[group_col].unique()
            data_by_group = [df[df[group_col]==g][column].dropna() for g in groups]
            bp = ax.boxplot(data_by_group, tick_labels=groups, patch_artist=True)
            for p in bp["boxes"]: p.set_facecolor("#3498db"); p.set_alpha(0.7)
            ax.set_xlabel(group_col); plt.xticks(rotation=45, ha="right")
        else:
            ax.boxplot(df[column].dropna(), patch_artist=True, boxprops=dict(facecolor="#3498db", alpha=0.7))
        ax.set_title(title or f"{column} 箱线图", fontsize=14, fontweight="bold")
        ax.set_ylabel(column); ax.grid(axis="y", alpha=0.3)
        return {"path": VisualizationTools._save(fig, f"boxplot_{column}"), "type": "boxplot", "column": column, "title": title or f"{column} 箱线图"}

    @staticmethod
    def correlation_heatmap(df, title=None):
        nc = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(nc) < 2: return {"error": "数值型列不足"}
        fig, ax = plt.subplots(figsize=(max(8,len(nc)*0.8), max(6,len(nc)*0.7)))
        sns.heatmap(df[nc].corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0, square=True, ax=ax, cbar_kws={"shrink":0.8})
        ax.set_title(title or "变量相关性热力图", fontsize=14, fontweight="bold")
        plt.xticks(rotation=45, ha="right"); plt.yticks(rotation=0)
        return {"path": VisualizationTools._save(fig, "correlation_heatmap"), "type": "heatmap", "title": title or "变量相关性热力图"}

    @staticmethod
    def bar_chart(df, category_col, value_col, title=None, top_n=15):
        grouped = df.groupby(category_col)[value_col].mean().sort_values(ascending=False).head(top_n)
        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(grouped)))
        bars = ax.bar(range(len(grouped)), grouped.values, color=colors, edgecolor="black", alpha=0.8)
        ax.set_xticks(range(len(grouped))); ax.set_xticklabels(grouped.index, rotation=45, ha="right")
        ax.set_ylabel(f"{value_col} (均值)"); ax.set_title(title or f"{category_col} vs {value_col} 柱状图", fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        for b, v in zip(bars, grouped.values):
            ax.text(b.get_x()+b.get_width()/2., b.get_height(), f"{v:.1f}", ha="center", va="bottom", fontsize=9)
        return {"path": VisualizationTools._save(fig, f"barchart_{category_col}_{value_col}"), "type": "bar_chart", "title": title or f"{category_col} vs {value_col} 柱状图"}

    @staticmethod
    def scatter_plot(df, x_col, y_col, hue_col=None, title=None):
        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
        if hue_col and hue_col in df.columns and df[hue_col].nunique() <= 10:
            for name, group in df.groupby(hue_col):
                ax.scatter(group[x_col], group[y_col], label=name, alpha=0.6, s=50)
            ax.legend(title=hue_col)
        else:
            ax.scatter(df[x_col], df[y_col], alpha=0.6, s=50, color="#e67e22")
        valid = df[[x_col,y_col]].dropna()
        if len(valid) >= 2:
            z = np.polyfit(valid[x_col], valid[y_col], 1)
            p = np.poly1d(z)
            xr = np.linspace(valid[x_col].min(), valid[x_col].max(), 100)
            r = np.corrcoef(valid[x_col], valid[y_col])[0,1]
            ax.plot(xr, p(xr), "r--", alpha=0.8, linewidth=2, label=f"趋势线 (R={r:.2f})")
            ax.legend()
        ax.set_xlabel(x_col); ax.set_ylabel(y_col)
        ax.set_title(title or f"{x_col} vs {y_col} 散点图", fontsize=14, fontweight="bold"); ax.grid(alpha=0.3)
        return {"path": VisualizationTools._save(fig, f"scatter_{x_col}_{y_col}"), "type": "scatter", "title": title or f"{x_col} vs {y_col} 散点图"}

    @staticmethod
    def pie_chart(df, column, title=None, top_n=8):
        vc = df[column].value_counts()
        if len(vc) > top_n:
            vc = pd.concat([vc.head(top_n), pd.Series({"其他": vc.iloc[top_n:].sum()})])
        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
        colors = plt.cm.Set3(np.linspace(0, 1, len(vc)))
        ax.pie(vc.values, labels=vc.index, autopct="%1.1f%%", colors=colors, startangle=90, pctdistance=0.85)
        ax.add_artist(plt.Circle((0,0), 0.70, fc="white"))
        ax.set_title(title or f"{column} 占比分布", fontsize=14, fontweight="bold")
        return {"path": VisualizationTools._save(fig, f"piechart_{column}"), "type": "pie_chart", "title": title or f"{column} 占比分布"}

    @staticmethod
    def missing_value_heatmap(df, title=None):
        if df.isna().sum().sum() == 0: return {"note": "数据无缺失值"}
        fig, ax = plt.subplots(figsize=(max(10,len(df.columns)*0.5), 6))
        sns.heatmap(df.isna().astype(int), cbar=False, cmap=["#2ecc71","#e74c3c"], yticklabels=False, ax=ax)
        ax.set_title(title or "缺失值分布热力图 (红色=缺失)", fontsize=14, fontweight="bold")
        plt.xticks(rotation=45, ha="right")
        return {"path": VisualizationTools._save(fig, "missing_value_heatmap"), "type": "missing_heatmap", "title": title or "缺失值分布热力图"}
