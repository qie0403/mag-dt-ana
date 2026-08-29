"""
全局配置模块
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
SAMPLES_DIR = BASE_DIR / "samples"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR.mkdir(exist_ok=True)

LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2000

AGENT_CONFIG = {
    "DataReaderAgent": {"name": "数据读取专家", "role": "负责读取和解析各类数据源文件", "color": "#3498db"},
    "DataCleanerAgent": {"name": "数据清洗专家", "role": "负责数据清洗、缺失值处理、异常值检测", "color": "#2ecc71"},
    "DataAnalystAgent": {"name": "数据分析专家", "role": "负责统计分析、相关性分析、趋势洞察", "color": "#e67e22"},
    "VisualizerAgent": {"name": "可视化专家", "role": "负责生成各类图表和可视化报告", "color": "#9b59b6"},
    "ReportGeneratorAgent": {"name": "报告生成专家", "role": "负责汇总分析结果并生成最终报告", "color": "#e74c3c"},
}

PLOT_STYLE = "seaborn-v0_8"
PLOT_DPI = 150
PLOT_FIGSIZE = (10, 6)
CHART_FORMAT = "png"

def get_run_mode():
    return "llm" if LLM_API_KEY else "auto"

RUN_MODE = get_run_mode()
