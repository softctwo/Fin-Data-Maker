"""
大规模数据生成示例 - Fin-Data-Maker v2.1.0

本示例展示如何生成和处理大规模数据（10万+记录）:
1. 批量生成策略 - 分批生成避免内存溢出
2. 性能优化 - 关闭实时验证提升速度
3. 进度监控 - 实时显示大数据生成进度
4. 增量导出 - 边生成边导出减少内存占用
5. 性能统计 - 记录生成速度和资源使用

适用场景:
- 性能测试数据准备
- 大规模数据库填充
- 压力测试数据集
- 数据迁移模拟
"""

import sys
import os
import time
import psutil
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_customer_table,
    create_account_table,
    create_transaction_table,
)
from src.analysis.dependency_analyzer import DependencyAnalyzer
from src.core.progress_monitor import ProgressMonitor, ProgressEventType


class PerformanceTracker:
    """性能跟踪器"""

    def __init__(self):
        self.start_time = None
        self.metrics = []
        self.process = psutil.Process()

    def start(self):
        """开始跟踪"""
        self.start_time = time.time()
        self.metrics = []

    def record(self, table_name, record_count):
        """记录生成指标"""
        elapsed = time.time() - self.start_time
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()

        self.metrics.append({
            'table': table_name,
            'records': record_count,
            'elapsed': elapsed,
            'memory_mb': memory_mb,
            'cpu_percent': cpu_percent,
            'records_per_sec': record_count / elapsed if elapsed > 0 else 0
        })

    def get_summary(self):
        """获取性能摘要"""
        if not self.metrics:
            return "无数据"

        total_records = sum(m['records'] for m in self.metrics)
        total_time = time.time() - self.start_time
        avg_speed = total_records / total_time if total_time > 0 else 0
        max_memory = max(m['memory_mb'] for m in self.metrics)

        return f"""
性能统计:
  - 总记录数: {total_records:,}
  - 总用时: {total_time:.2f} 秒
  - 平均速度: {avg_speed:.0f} 条/秒
  - 峰值内存: {max_memory:.1f} MB
"""


def large_scale_generation_demo():
    """大规模数据生成演示"""

    print("=" * 80)
    print("  🚀 大规模数据生成示例")
    print("=" * 80)

    # 配置
    config = {
        'customer': {'total': 100000, 'batch': 5000},    # 10万客户
        'account': {'total': 200000, 'batch': 10000},    # 20万账户
        'transaction': {'total': 500000, 'batch': 50000} # 50万交易
    }

    print("\n生成计划:")
    for table, conf in config.items():
        print(f"  {table:15s}: {conf['total']:7,} 条 (批大小: {conf['batch']:,})")

    total_records = sum(c['total'] for c in config.values())
    print(f"\n  总计: {total_records:,} 条记录")

    # 估算时间（基于经验值：约1000条/秒）
    estimated_time = total_records / 1000
    print(f"  预计耗时: {estimated_time:.0f} 秒 ({estimated_time/60:.1f} 分钟)")

    print("\n按Enter键开始生成...")
    input()

    # 创建输出目录
    output_dir = "output/large_scale"
    os.makedirs(output_dir, exist_ok=True)

    # ============================================================
    # 准备环境
    # ============================================================
    print("\n" + "=" * 80)
    print("  准备生成环境")
    print("=" * 80)

    # 创建表定义
    tables = [
        create_customer_table(),
        create_account_table(),
        create_transaction_table(),
    ]

    # 分析依赖关系
    analyzer = DependencyAnalyzer(tables)
    generation_order = analyzer.get_generation_order()
    print(f"\n✓ 生成顺序: {' → '.join(generation_order)}")

    # 创建应用
    app = DataMakerApp(seed=None)  # 不使用固定种子，生成随机数据
    for table in tables:
        app.add_table(table)

    # 创建进度监控
    monitor = ProgressMonitor()

    # 进度条回调
    def progress_callback(event):
        if event.event_type == ProgressEventType.PROGRESS:
            bar_length = 40
            filled = int(bar_length * event.percentage / 100)
            bar = '█' * filled + '-' * (bar_length - filled)
            eta_str = f"ETA: {event.eta:.0f}s" if event.eta > 0 else ""
            print(f"\r  进度: |{bar}| {event.percentage:5.1f}% | {event.current:,}/{event.total:,} | {eta_str}",
                  end='', flush=True)
        elif event.event_type in (ProgressEventType.TABLE_COMPLETED, ProgressEventType.ERROR):
            print()  # 换行

    monitor.add_callback(progress_callback)

    # 性能跟踪
    perf_tracker = PerformanceTracker()
    perf_tracker.start()

    print("✓ 环境准备完成\n")

    # ============================================================
    # 生成数据
    # ============================================================
    print("=" * 80)
    print("  开始生成数据")
    print("=" * 80)

    generated_ids = {}  # 存储生成的ID供后续引用

    for table_name in generation_order:
        if table_name not in config:
            continue

        total_count = config[table_name]['total']
        batch_size = config[table_name]['batch']

        print(f"\n【{table_name}】- 总计 {total_count:,} 条，批大小 {batch_size:,}")

        monitor.table_started(table_name, total_count)

        # 准备关联数据
        related_data = None
        dependencies = analyzer.graph.get_dependencies(table_name)
        if dependencies:
            related_data = {}
            for dep in dependencies:
                if dep in generated_ids:
                    related_data[dep] = generated_ids[dep]
            print(f"  依赖: {', '.join(dependencies)}")

        # 分批生成
        all_ids = []
        batch_num = 0

        for start_idx in range(0, total_count, batch_size):
            batch_num += 1
            current_batch_size = min(batch_size, total_count - start_idx)

            # 生成数据（不验证以提高速度）
            if related_data:
                batch_data, _ = app.generate_with_relations(
                    table_name,
                    count=current_batch_size,
                    related_data=related_data,
                    validate=False
                )
            else:
                batch_data, _ = app.generate_data(
                    table_name,
                    count=current_batch_size,
                    validate=False
                )

            # 提取ID
            id_field = f"{table_name}_id"
            batch_ids = [item[id_field] for item in batch_data if id_field in item]
            all_ids.extend(batch_ids)

            # 增量导出（边生成边写入，减少内存占用）
            csv_file = f"{output_dir}/{table_name}.csv"
            app.export_to_csv(
                batch_data,
                table_name,
                csv_file,
                mode='a' if batch_num > 1 else 'w'  # 追加模式
            )

            # 更新进度
            completed = start_idx + current_batch_size
            monitor.update(completed, f"批次 #{batch_num}")

        # 存储ID供后续使用
        generated_ids[table_name] = all_ids

        monitor.table_completed(table_name, total_count)
        perf_tracker.record(table_name, total_count)

        # 显示批次完成状态
        print(f"  ✓ 完成 {batch_num} 个批次，共 {total_count:,} 条记录")
        print(f"  ✓ 已导出到: {csv_file}")

    monitor.complete("大规模数据生成完成！")

    # ============================================================
    # 性能报告
    # ============================================================
    print("\n" + "=" * 80)
    print("  📊 性能报告")
    print("=" * 80)

    print(perf_tracker.get_summary())

    # 详细指标
    print("详细指标:")
    print(f"  {'表名':<15s} | {'记录数':>10s} | {'用时(秒)':>10s} | {'速度(条/秒)':>12s} | {'内存(MB)':>10s}")
    print("  " + "-" * 72)

    for metric in perf_tracker.metrics:
        print(f"  {metric['table']:<15s} | {metric['records']:>10,} | "
              f"{metric['elapsed']:>10.1f} | {metric['records_per_sec']:>12.0f} | "
              f"{metric['memory_mb']:>10.1f}")

    # 生成性能报告文件
    perf_file = f"{output_dir}/performance_report.txt"
    with open(perf_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("大规模数据生成性能报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(perf_tracker.get_summary())

        f.write("\n详细指标:\n")
        f.write("-" * 80 + "\n")
        for metric in perf_tracker.metrics:
            f.write(f"{metric['table']:15s} | "
                   f"{metric['records']:10,} 条 | "
                   f"{metric['elapsed']:8.1f} 秒 | "
                   f"{metric['records_per_sec']:10.0f} 条/秒 | "
                   f"{metric['memory_mb']:8.1f} MB\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\n✓ 性能报告已保存: {perf_file}")

    # ============================================================
    # 数据验证采样
    # ============================================================
    print("\n" + "=" * 80)
    print("  🔍 数据验证（采样）")
    print("=" * 80)

    print("\n由于数据量较大，仅对部分数据进行验证采样...\n")

    for table_name in generation_order:
        if table_name not in config:
            continue

        # 生成少量数据进行验证
        print(f"  {table_name}: ", end='')
        sample_data, report = app.generate_data(table_name, count=100, validate=True)

        if report.is_valid:
            print(f"✓ 验证通过 (100条采样)")
        else:
            print(f"⚠️  发现 {len(report.errors)} 个问题")
            for error in report.errors[:3]:  # 只显示前3个
                print(f"      - {error}")

    # ============================================================
    # 总结
    # ============================================================
    print("\n" + "=" * 80)
    print("  ✅ 大规模数据生成完成！")
    print("=" * 80)

    total_generated = sum(config[t]['total'] for t in generation_order if t in config)
    total_time = time.time() - perf_tracker.start_time

    print(f"\n生成统计:")
    print(f"  - 总记录数: {total_generated:,}")
    print(f"  - 总用时: {total_time:.1f} 秒 ({total_time/60:.1f} 分钟)")
    print(f"  - 平均速度: {total_generated/total_time:.0f} 条/秒")

    print(f"\n输出文件:")
    for table_name in generation_order:
        if table_name in config:
            csv_file = f"{output_dir}/{table_name}.csv"
            if os.path.exists(csv_file):
                size_mb = os.path.getsize(csv_file) / 1024 / 1024
                print(f"  - {csv_file} ({size_mb:.1f} MB)")

    print(f"\n💡 提示:")
    print(f"  - 所有数据采用增量导出方式，内存占用较小")
    print(f"  - 可以使用数据库批量导入工具导入CSV文件")
    print(f"  - 对于更大规模数据，建议调整批次大小")

    print("\n" + monitor.get_summary())


if __name__ == '__main__':
    try:
        large_scale_generation_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
