"""
多 Agent 协作自动化数据分析系统 - Streamlit 可视化界面
"""
import sys, os, time, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))
import streamlit as st
from config import RUN_MODE, SAMPLES_DIR, OUTPUT_DIR, AGENT_CONFIG
from orchestrator.coordinator import Coordinator
from utils.logger import AgentLogger

st.set_page_config(page_title="DataPilot · 多Agent智能分析平台", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.main-header{font-size:2rem;font-weight:bold;background:linear-gradient(135deg,#0ea5e9 0%,#14b8a6 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.agent-card{background:#f0fdfa;border-radius:10px;padding:12px;margin:5px 0;border-left:4px solid #0ea5e9}
.status-success{color:#2ecc71;font-weight:bold}.status-error{color:#e74c3c;font-weight:bold}
.log-entry{font-family:monospace;font-size:0.85rem;padding:4px 8px;border-bottom:1px solid #eee}
</style>""", unsafe_allow_html=True)

for k in ["coordinator","result","is_running","progress_logs"]:
    if k not in st.session_state: st.session_state[k] = None if k!="is_running" else False
if "progress_logs" not in st.session_state: st.session_state.progress_logs = []

with st.sidebar:
    st.markdown("### 🤖 系统信息")
    st.info(f"**运行模式**: {'LLM智能模式' if RUN_MODE=='llm' else '全自动规则模式'}")
    st.caption("无API Key时自动使用规则模式，确保零依赖运行")
    st.markdown("---"); st.markdown("### 👥 Agent 团队")
    colors = {"DataReaderAgent":"#3498db","DataCleanerAgent":"#2ecc71","DataAnalystAgent":"#e67e22","VisualizerAgent":"#9b59b6","ReportGeneratorAgent":"#e74c3c"}
    for aid, info in AGENT_CONFIG.items():
        c = colors.get(aid,"#666")
        st.markdown(f'<div class="agent-card" style="border-left-color:{c}"><div style="font-weight:bold;color:{c}">{info["name"]}</div><div style="font-size:0.8rem;color:#666">{info["role"]}</div></div>', unsafe_allow_html=True)
    st.markdown("---"); st.caption("数据读取 → 数据清洗 → 数据分析 → 可视化 → 报告生成")
    if st.button("🔄 重置系统", width='stretch'):
        for k in ["coordinator","result","is_running","progress_logs"]: st.session_state[k] = None if k!="is_running" else False
        st.session_state.progress_logs = []; st.rerun()

st.markdown('<p class="main-header">🤖 DataPilot · 多 Agent 智能分析平台</p>', unsafe_allow_html=True)
st.caption("上传数据文件，多 Agent 团队将自动完成 读取→清洗→分析→可视化→报告 全流程")
tab1, tab2, tab3 = st.tabs(["📤 任务提交", "⚙️ 执行过程", "📊 分析结果"])

with tab1:
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown("### 1. 上传数据文件")
        uf = st.file_uploader("选择 CSV / Excel / JSON 文件", type=["csv","xlsx","xls","json","tsv","txt"])
        use_sample = st.checkbox("使用示例数据（销售数据）", value=False)
        st.markdown("### 2. 任务描述")
        task_desc = st.text_area("描述你想要的分析（可选）", value="完整数据分析", height=80)
        st.markdown("### 3. 开始执行")
        run_btn = st.button("🚀 启动分析", type="primary", width='stretch', disabled=st.session_state.is_running)
    with c2:
        st.markdown("### 执行流程预览")
        for icon,name,agent,color in [("📂","数据读取","DataReaderAgent","#3498db"),("🧹","数据清洗","DataCleanerAgent","#2ecc71"),("📈","数据分析","DataAnalystAgent","#e67e22"),("📊","可视化","VisualizerAgent","#9b59b6"),("📝","报告生成","ReportGeneratorAgent","#e74c3c")]:
            st.markdown(f'<div style="display:flex;align-items:center;margin:8px 0"><span style="font-size:1.5rem;margin-right:10px">{icon}</span><div><div style="font-weight:bold;color:{color}">{name}</div><div style="font-size:0.75rem;color:#999">{agent}</div></div></div>', unsafe_allow_html=True)
    if run_btn:
        if use_sample: fp = str(SAMPLES_DIR / "sample_sales_data.csv"); st.success(f"使用示例数据")
        elif uf is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uf.name).suffix) as tmp:
                tmp.write(uf.getvalue()); fp = tmp.name
            st.success(f"文件已上传: {uf.name}")
        else: st.error("请上传文件或选择使用示例数据"); st.stop()
        st.session_state.is_running = True; st.session_state.progress_logs = []
        logger = AgentLogger("WebUI", log_to_file=True)
        def pcb(step,total,msg): st.session_state.progress_logs.append({"step":step,"total":total,"message":msg,"time":time.strftime("%H:%M:%S")})
        coord = Coordinator(run_mode=RUN_MODE, logger=logger, progress_callback=pcb)
        st.session_state.coordinator = coord
        with st.spinner("多 Agent 协作分析进行中..."):
            result = coord.run(fp, task_desc); st.session_state.result = result
        st.session_state.is_running = False
        st.success(f"分析完成! 总耗时: {result.get('total_time',0)}s"); st.rerun()

with tab2:
    if st.session_state.result is None: st.info("暂无执行记录，请先在「任务提交」页面启动分析")
    else:
        r = st.session_state.result; s = r.get("summary",{})
        st.markdown("### 📋 执行摘要")
        a,b,c,d = st.columns(4)
        a.metric("总任务数",s.get("total_tasks",0)); b.metric("成功",s.get("success_count",0))
        c.metric("失败",s.get("error_count",0)); d.metric("成功率",s.get("success_rate","0%"))
        st.markdown(f"**总耗时**: {r.get('total_time',0)}s | **运行模式**: {r.get('run_mode','auto')}")
        st.markdown("---"); st.markdown("### 👥 Agent 执行详情")
        for det in r.get("agent_details",[]):
            stt = det.get("status",""); icon = "✅" if stt=="success" else "❌" if stt=="error" else "⏳"
            with st.expander(f"{icon} {det.get('subtask','')} - {det.get('agent','')}", expanded=(stt=="error")):
                st.markdown(f"**状态**: <span class='status-{stt}'>{stt}</span>", unsafe_allow_html=True)
                st.markdown(f"**消息**: {det.get('message','')}"); st.markdown(f"**耗时**: {det.get('elapsed_time',0)}s")
        st.markdown("---"); st.markdown("### 📝 执行日志")
        if st.session_state.coordinator:
            logs = st.session_state.coordinator.get_execution_log()
            for log in logs[-50:]:
                sc = {"success":"#2ecc71","error":"#e74c3c","warning":"#f39c12","info":"#3498db"}.get(log.get("status","info"),"#666")
                st.markdown(f'<div class="log-entry"><span style="color:#999">[{log.get("timestamp","")}]</span> <span style="color:{sc};font-weight:bold">[{log.get("agent","")}]</span> {log.get("action","")} <span style="color:#999">{log.get("details","")}</span></div>', unsafe_allow_html=True)

with tab3:
    if st.session_state.result is None: st.info("暂无分析结果")
    else:
        r = st.session_state.result; o = r.get("outputs",{}); di = r.get("data_info",{})
        st.markdown("### 📂 数据概览")
        a,b,c = st.columns(3); a.metric("数据行数",di.get("rows",0)); b.metric("数据列数",di.get("columns",0)); c.metric("生成图表",o.get("chart_count",0))
        st.markdown("---"); st.markdown("### 💡 关键洞察")
        for i, ins in enumerate(r.get("key_insights",[]),1): st.markdown(f"{i}. {ins}")
        st.markdown("---"); st.markdown("### 📊 可视化图表")
        charts = o.get("charts",[])
        if charts:
            cc = st.columns(2)
            for i, ch in enumerate(charts):
                with cc[i%2]:
                    cp = ch.get("path","")
                    if cp and os.path.exists(cp): st.image(cp, caption=ch.get("title",f"图表{i+1}"), width='stretch')
                    else: st.caption(f"图表 {i+1}: {ch.get('title','')}")
        st.markdown("---"); st.markdown("### 📝 分析报告")
        rc = o.get("report_content","")
        if rc:
            with st.expander("查看完整报告内容", expanded=False): st.markdown(rc)
        st.markdown("### 📥 结果导出")
        e1,e2,e3 = st.columns(3)
        with e1:
            rp = o.get("report_path","")
            if rp and os.path.exists(rp):
                with open(rp,"r",encoding="utf-8") as f: st.download_button("📄 下载Markdown报告",f.read(),file_name=os.path.basename(rp),mime="text/markdown",width='stretch')
        with e2:
            jp = o.get("json_path","")
            if jp and os.path.exists(jp):
                with open(jp,"r",encoding="utf-8") as f: st.download_button("📦 下载JSON数据",f.read(),file_name=os.path.basename(jp),mime="application/json",width='stretch')
        with e3:
            if charts:
                zp = OUTPUT_DIR / "charts_bundle.zip"
                with zipfile.ZipFile(zp,"w") as zf:
                    for ch in charts:
                        cp = ch.get("path","")
                        if cp and os.path.exists(cp): zf.write(cp, os.path.basename(cp))
                with open(zp,"rb") as f: st.download_button("🗂️ 下载图表打包",f.read(),file_name="charts_bundle.zip",mime="application/zip",width='stretch')

        # === 新增：一键导出完整分析包（报告+JSON数据+全部图表+执行日志） ===
        st.markdown("---"); st.markdown("### 📦 一键导出完整分析包")
        st.caption("将 Markdown 报告、结构化 JSON 数据、全部图表与 Agent 执行日志打包为一个 zip")
        bundle_path = OUTPUT_DIR / "latest_analysis_bundle.zip"
        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
            rp = o.get("report_path","")
            if rp and os.path.exists(rp): zf.write(rp, f"report/{os.path.basename(rp)}")
            jp = o.get("json_path","")
            if jp and os.path.exists(jp): zf.write(jp, f"data/{os.path.basename(jp)}")
            for ch in charts:
                cp = ch.get("path","")
                if cp and os.path.exists(cp): zf.write(cp, f"charts/{os.path.basename(cp)}")
            if st.session_state.coordinator:
                logs = st.session_state.coordinator.get_execution_log()
                log_txt = "\n".join(
                    f"[{l.get('timestamp','')}] [{l.get('status','info')}] [{l.get('agent','')}] {l.get('action','')} {l.get('details','')}"
                    for l in logs)
                zf.writestr("execution_log.txt", log_txt)
        with open(bundle_path,"rb") as f:
            st.download_button("📦 一键下载完整分析包", f.read(),
                               file_name="analysis_bundle.zip", mime="application/zip",
                               type="primary", width='stretch')

st.markdown("---"); st.caption("多 Agent 协作自动化数据分析系统 | 数据读取→清洗→分析→可视化→报告 全流程自动化")
