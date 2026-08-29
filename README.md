# 🤖 多 Agent 协作自动化数据分析系统

> 基于多 Agent 协作架构的端到端自动化数据分析平台，支持从数据读取到报告生成的全流程自动化。

## 核心功能

1. **多角色 Agent 协作**：数据读取→数据清洗→数据分析→可视化→报告生成，5个专业Agent流水线协作
2. **任务自动拆解**：自然语言描述自动识别所需Agent，智能编排执行顺序
3. **可视化界面**：Streamlit Web界面，支持任务提交、过程监控、结果导出
4. **双模式运行**：LLM智能模式（需API Key）+ 全自动规则模式（零依赖可运行）

## 快速开始

\\ash
# 安装依赖
pip install -r requirements.txt

# 启动Web界面
streamlit run main.py

# 或命令行运行
python run.py samples/sample_sales_data.csv
\
## 系统架构

\用户交互层 (Streamlit Web UI)
       ↓
编排引擎层 (TaskDecomposer → Coordinator → ResultAggregator)
       ↓ 共享上下文 Context
Agent 执行层 (5个专业Agent 流水线协作)
       ↓
工具层 (DataTools / AnalysisTools / VisualizationTools)
\
## Agent 设计

| Agent | 职责 | 核心工具 |
|-------|------|----------|
| DataReaderAgent | 智能读取CSV/Excel/JSON | read_file, get_data_overview |
| DataCleanerAgent | 去重、缺失值填充、异常值检测 | clean_data |
| DataAnalystAgent | 统计分析、相关性、分组聚合、趋势 | descriptive_statistics, correlation_analysis等 |
| VisualizerAgent | 自动生成9种图表 | histogram, boxplot, heatmap, scatter等 |
| ReportGeneratorAgent | 汇总生成Markdown+JSON报告 | 内置模板引擎 |

## 项目结构

\multi-agent-data-analyzer/
├── main.py              # Streamlit Web界面
├── run.py               # 命令行入口
├── config.py            # 全局配置
├── requirements.txt     # 依赖清单
├── agents/              # Agent层（5个专业Agent+基类）
├── orchestrator/        # 编排引擎（任务拆解+协调器+结果汇总）
├── tools/               # 工具层（数据/分析/可视化工具）
├── utils/               # 工具函数（日志+辅助函数）
├── samples/             # 示例数据
└── output/              # 输出目录
\
## 技术选型

- **核心语言**: Python 3.10+
- **数据处理**: pandas, numpy, scipy
- **可视化**: matplotlib, seaborn
- **Web框架**: Streamlit
- **设计模式**: 模板方法+中介者+管道+策略模式

## 扩展开发

新增Agent：继承BaseAgent，实现_run()方法，注册到Coordinator.AGENT_CLASSES即可。

## License

MIT
