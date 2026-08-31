"""命令行入口"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from config import RUN_MODE
from orchestrator.coordinator import Coordinator

def main():
    if len(sys.argv) < 2:
        print("用法: python run.py <数据文件路径> [任务描述]")
        print("示例: python run.py samples/sample_sales_data.csv '完整数据分析'")
        sys.exit(1)
    fp = sys.argv[1]
    desc = sys.argv[2] if len(sys.argv) > 2 else "完整数据分析"
    if not Path(fp).exists():
        print(f"错误: 文件不存在 - {fp}"); sys.exit(1)
    print("="*60)
    print("  多 Agent 协作自动化数据分析系统")
    print("="*60)
    print(f"  数据文件: {fp}"); print(f"  任务描述: {desc}"); print(f"  运行模式: {RUN_MODE}")
    print("="*60 + "\n")
    coord = Coordinator(run_mode=RUN_MODE)
    result = coord.run(fp, desc)
    print("\n" + "="*60)
    print("  执行结果摘要"); print("="*60)
    print(f"  状态: {result.get('status','unknown')}")
    print(f"  总耗时: {result.get('total_time',0)}s")
    s = result.get('summary',{})
    print(f"  任务数: {s.get('total_tasks',0)} | 成功: {s.get('success_count',0)} | 失败: {s.get('error_count',0)} | 成功率: {s.get('success_rate','0%')}")
    print("\n  关键洞察:")
    for i, ins in enumerate(result.get('key_insights',[]), 1): print(f"    {i}. {ins}")
    o = result.get('outputs',{})
    print(f"\n  生成图表: {o.get('chart_count',0)} 张")
    if o.get('report_path'): print(f"  报告路径: {o['report_path']}")
    if o.get('json_path'): print(f"  数据路径: {o['json_path']}")
    print("="*60)

if __name__ == "__main__": main()
