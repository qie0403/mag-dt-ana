# 更新日志

本项目所有重要变更都会记录在本文件中。

## [Unreleased]

### Changed - 2026-10-24
- 重写 README：新增徽章、功能截图位、Mermaid 架构图、完整启动步骤（Web/CLI/Docker）、双模式说明、输出产物、常见问题与项目结构。
- 清理 `requirements.txt`：移除代码未使用的 plotly、langchain、langchain-openai、openai、jinja2 五个冗余依赖，并为核心依赖补充版本上界。
- 新增 MIT `LICENSE` 文件。

### Fixed - 2026-10-24
- `config.py` 启动时自动加载 `.env`（`python-dotenv`），修复配置了 `.env` 但 `OPENAI_API_KEY` 实际不生效的问题；未安装该库时静默跳过。

## [2026-10-19]

### Added
- Streamlit 界面品牌升级为 DataPilot，主题配色改为青绿科技风。
- 结果页新增「一键导出完整分析包」按钮，将 Markdown 报告、JSON 数据、全部图表与执行日志打包为单个 zip。

### Changed
- 相关性分析阈值由硬编码的 `0.5` 改为可配置参数 `threshold`（默认 `0.3`）。
  在示例销售数据上，检出的显著相关变量对从 **1 对提升到 3 对**，关键洞察由 7 条增加到 9 条。

### Fixed
- 可视化首选中文字体由 SimHei（无粗体）改为 Microsoft YaHei（含粗体），并抑制 findfont 冗余日志，
  消除运行时字体告警，CLI 退出码恢复为 0。

## [2026-08-31]

### Fixed
- 报告中的图表改为 base64 内嵌，解决 Streamlit 无法显示本地相对路径图片的问题。
- 修复报告内容中换行符被双重转义为字面 `\n` 的问题。

## [2026-08-29]

### Added
- 首个版本：5 个专业 Agent 流水线（数据读取 → 清洗 → 分析 → 可视化 → 报告）。
- 任务自动拆解与编排引擎（TaskDecomposer / Coordinator / ResultAggregator）。
- Streamlit Web 界面，支持任务提交、过程监控、结果导出。
- 全自动规则模式（无需 API Key）与 LLM 智能模式双模式运行。
- 命令行入口 `run.py` 与 Docker 部署文件。
