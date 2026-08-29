"""
辅助工具函数模块
"""
import json
import re
from datetime import datetime
from pathlib import Path
import pandas as pd


def safe_filename(name):
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    return safe.strip().replace(' ', '_')[:200]

def timestamp_str():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def detect_file_type(file_path):
    ext = Path(file_path).suffix.lower()
    return {'.csv':'csv','.tsv':'tsv','.txt':'txt','.xlsx':'excel','.xls':'excel','.json':'json'}.get(ext, 'unknown')

def detect_column_types(df):
    col_types = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            col_types[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_types[col] = "datetime"
        elif pd.api.types.is_bool_dtype(dtype):
            col_types[col] = "boolean"
        else:
            unique_ratio = df[col].nunique() / max(len(df), 1)
            col_types[col] = "categorical" if unique_ratio < 0.05 and df[col].nunique() < 50 else "text"
    return col_types

def format_number(num, decimals=2):
    if pd.isna(num): return "N/A"
    if abs(num) >= 1_000_000: return f"{num/1_000_000:.{decimals}f}M"
    if abs(num) >= 1_000: return f"{num/1_000:.{decimals}f}K"
    return f"{num:.{decimals}f}"

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
