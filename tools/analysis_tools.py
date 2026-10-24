"""
数据分析工具模块
"""
import pandas as pd
import numpy as np
from scipy import stats


class AnalysisTools:
    """数据分析工具集合"""

    @staticmethod
    def descriptive_statistics(df):
        result = {"numeric_summary": {}, "categorical_summary": {}, "key_insights": []}
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) == 0: continue
            s = {"count": int(len(data)), "mean": round(float(data.mean()),4), "std": round(float(data.std()),4),
                 "min": round(float(data.min()),4), "25%": round(float(data.quantile(0.25)),4),
                 "50%": round(float(data.median()),4), "75%": round(float(data.quantile(0.75)),4),
                 "max": round(float(data.max()),4), "skewness": round(float(data.skew()),4),
                 "kurtosis": round(float(data.kurtosis()),4)}
            result["numeric_summary"][col] = s
            if abs(s["skewness"]) > 1:
                d = "正偏（右偏）" if s["skewness"] > 0 else "负偏（左偏）"
                result["key_insights"].append(f"列 '{col}' 呈{d}分布，偏度={s['skewness']}")
            if s["std"] > 0 and s["mean"] > 0 and s["std"]/abs(s["mean"]) > 1:
                result["key_insights"].append(f"列 '{col}' 变异系数={s['std']/abs(s['mean']):.2f}，数据离散程度较高")
        cat_cols = [c for c in df.columns if c not in numeric_cols]
        for col in cat_cols:
            if df[col].nunique() <= 50:
                vc = df[col].value_counts().head(10)
                result["categorical_summary"][col] = {"unique_count": int(df[col].nunique()),
                    "top_values": vc.to_dict(), "top_value": str(vc.index[0]) if len(vc)>0 else None,
                    "top_value_pct": round(float(vc.iloc[0]/len(df)*100),1) if len(vc)>0 else 0}
        return result

    @staticmethod
    def correlation_analysis(df, threshold=0.3):
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return {"correlation_matrix": {}, "strong_correlations": [], "note": "数值型列不足2列"}
        corr = df[numeric_cols].corr()
        strong = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                v = corr.iloc[i,j]
                if not np.isnan(v) and abs(v) >= threshold:
                    strong.append({"var1": numeric_cols[i], "var2": numeric_cols[j],
                        "correlation": round(float(v),4), "strength": "强" if abs(v)>=0.8 else "中等",
                        "direction": "正相关" if v>0 else "负相关"})
        strong.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        return {"correlation_matrix": corr.round(4).to_dict(), "strong_correlations": strong[:15], "columns": numeric_cols}

    @staticmethod
    def groupby_analysis(df, group_col, agg_col=None, agg_funcs=None):
        if agg_funcs is None: agg_funcs = ["count","mean","sum","min","max"]
        if group_col not in df.columns: return {"error": f"列 '{group_col}' 不存在"}
        if agg_col is None:
            nc = df.select_dtypes(include=[np.number]).columns.tolist()
            agg_col = nc[0] if nc else None
        if agg_col is None or agg_col not in df.columns: return {"error": "没有可聚合的数值列"}
        grouped = df.groupby(group_col)[agg_col].agg(agg_funcs)
        grouped = grouped.sort_values("mean" if "mean" in agg_funcs else agg_funcs[0], ascending=False)
        return {"group_column": group_col, "agg_column": agg_col,
                "results": grouped.round(4).reset_index().to_dict(orient="records"), "group_count": len(grouped)}

    @staticmethod
    def trend_analysis(df, date_col, value_col):
        if date_col not in df.columns or value_col not in df.columns: return {"error": "指定的列不存在"}
        t = df.copy()
        t[date_col] = pd.to_datetime(t[date_col], errors="coerce")
        t = t.dropna(subset=[date_col, value_col]).sort_values(date_col)
        if len(t) < 2: return {"error": "有效数据点不足"}
        x = np.arange(len(t)); y = t[value_col].values.astype(float)
        slope, intercept, r_value, p_value, _ = stats.linregress(x, y)
        pct = t[value_col].pct_change().dropna()
        return {"date_column": date_col, "value_column": value_col, "data_points": len(t),
            "trend": {"slope": round(float(slope),4), "intercept": round(float(intercept),4),
                "r_squared": round(float(r_value**2),4), "p_value": round(float(p_value),4),
                "direction": "上升" if slope>0 else "下降" if slope<0 else "平稳", "significant": p_value<0.05},
            "overall_change": {"start_value": round(float(y[0]),4), "end_value": round(float(y[-1]),4),
                "change_pct": round(float((y[-1]-y[0])/y[0]*100),2) if y[0]!=0 else None},
            "volatility": round(float(np.std(pct)*100),2) if len(pct)>0 else None,
            "time_series": t[[date_col,value_col]].to_dict(orient="records")[-100:]}
