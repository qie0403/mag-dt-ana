"""
数据处理工具模块
"""
import pandas as pd
import numpy as np
from pathlib import Path
from utils.helpers import detect_file_type, detect_column_types


class DataTools:
    """数据处理工具集合"""

    @staticmethod
    def read_file(file_path, **kwargs):
        file_path = Path(file_path)
        file_type = detect_file_type(file_path)
        result = {"success": False, "df": None, "file_info": {}, "error": None}
        try:
            if file_type == "csv":
                for enc in ["utf-8", "gbk", "gb2312", "latin1"]:
                    try:
                        df = pd.read_csv(file_path, encoding=enc, **kwargs)
                        result["file_info"]["encoding"] = enc
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                else:
                    df = pd.read_csv(file_path, encoding="utf-8", errors="replace", **kwargs)
            elif file_type == "tsv":
                df = pd.read_csv(file_path, sep="\\t", encoding="utf-8", **kwargs)
            elif file_type == "excel":
                df = pd.read_excel(file_path, **kwargs)
            elif file_type == "json":
                df = pd.read_json(file_path, **kwargs)
            elif file_type == "txt":
                df = pd.read_csv(file_path, sep=None, engine="python", **kwargs)
            else:
                result["error"] = f"不支持的文件格式: {file_type}"
                return result

            result["df"] = df
            result["success"] = True
            result["file_info"].update({
                "filename": file_path.name, "file_type": file_type,
                "rows": len(df), "columns": len(df.columns),
                "column_names": list(df.columns),
                "column_types": detect_column_types(df),
                "memory_usage": f"{df.memory_usage(deep=True).sum()/1024:.1f} KB",
            })
        except Exception as e:
            result["error"] = str(e)
        return result

    @staticmethod
    def get_data_overview(df):
        overview = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": [], "missing_summary": {},
            "duplicate_count": int(df.duplicated().sum()),
        }
        for col in df.columns:
            ci = {
                "name": col, "dtype": str(df[col].dtype),
                "non_null": int(df[col].notna().sum()),
                "missing": int(df[col].isna().sum()),
                "missing_rate": f"{df[col].isna().mean()*100:.1f}%",
                "unique": int(df[col].nunique()),
            }
            if pd.api.types.is_numeric_dtype(df[col]):
                ci["min"] = float(df[col].min()) if df[col].notna().any() else None
                ci["max"] = float(df[col].max()) if df[col].notna().any() else None
                ci["mean"] = float(df[col].mean()) if df[col].notna().any() else None
            overview["columns"].append(ci)
        missing = df.isna().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        overview["missing_summary"] = {
            col: {"count": int(c), "rate": f"{c/len(df)*100:.1f}%"}
            for col, c in missing.items()
        }
        return overview

    @staticmethod
    def clean_data(df, strategies=None):
        if strategies is None:
            strategies = {"missing_numeric": "median", "missing_categorical": "mode",
                          "duplicates": "remove", "outlier_method": "iqr"}
        report = {"original_rows": len(df), "original_columns": len(df.columns), "steps": []}
        cleaned = df.copy()

        if strategies.get("duplicates") == "remove":
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            report["steps"].append({"step": "去除重复行", "removed": before - len(cleaned), "remaining": len(cleaned)})

        missing_before = cleaned.isna().sum().sum()
        for col in cleaned.columns:
            if cleaned[col].isna().sum() == 0:
                continue
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                m = strategies.get("missing_numeric", "median")
                fill = cleaned[col].median() if m == "median" else cleaned[col].mean() if m == "mean" else 0
                if m == "drop":
                    cleaned = cleaned.dropna(subset=[col]); continue
                cleaned[col] = cleaned[col].fillna(fill)
            else:
                m = strategies.get("missing_categorical", "mode")
                if m == "drop":
                    cleaned = cleaned.dropna(subset=[col]); continue
                mode_val = cleaned[col].mode()
                fill = mode_val.iloc[0] if len(mode_val) > 0 else "Unknown"
                cleaned[col] = cleaned[col].fillna(fill)
        missing_after = cleaned.isna().sum().sum()
        report["steps"].append({"step": "处理缺失值", "filled": int(missing_before - missing_after), "remaining_missing": int(missing_after)})

        outlier_info = {}
        if strategies.get("outlier_method") in ["iqr", "zscore"]:
            for col in cleaned.select_dtypes(include=[np.number]).columns:
                if strategies["outlier_method"] == "iqr":
                    Q1, Q3 = cleaned[col].quantile(0.25), cleaned[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = cleaned[(cleaned[col] < Q1-1.5*IQR) | (cleaned[col] > Q3+1.5*IQR)]
                else:
                    z = np.abs((cleaned[col]-cleaned[col].mean())/cleaned[col].std())
                    outliers = cleaned[z > 3]
                if len(outliers) > 0:
                    outlier_info[col] = {"count": len(outliers), "rate": f"{len(outliers)/len(cleaned)*100:.1f}%"}
        report["steps"].append({"step": "异常值检测", "method": strategies.get("outlier_method","none"), "outliers": outlier_info})

        for col in cleaned.columns:
            if cleaned[col].dtype == "object":
                try: cleaned[col] = pd.to_datetime(cleaned[col])
                except (ValueError, TypeError): pass

        report["final_rows"] = len(cleaned)
        report["final_columns"] = len(cleaned.columns)
        report["rows_removed"] = report["original_rows"] - len(cleaned)
        return {"df": cleaned, "report": report}
