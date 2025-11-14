"""
综合使用示例 - Fin-Data-Maker v2.1.0

本示例展示如何综合使用所有功能:
1. 依赖关系分析 - 自动分析表依赖，确定生成顺序
2. ER图可视化 - 生成专业的文档用图表
3. 进度监控 - 实时跟踪数据生成过程
4. 数据生成 - 按依赖顺序生成关联数据
5. 数据验证 - 验证生成数据的质量
6. 多格式导出 - 导出为CSV/JSON/Excel

适用场景:
- 完整的金融数据生成流程
- 需要文档化数据模型
- 大批量数据生成监控
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_customer_table,
    create_account_table,
    create_transaction_table,
    create_bond_table,
    create_fund_table,
    create_derivative_table,
)
from src.analysis.dependency_analyzer import DependencyAnalyzer
from src.visualization.relationship_visualizer import RelationshipVisualizer, VisualizationFormat
from src.core.progress_monitor import ProgressMonitor, ProgressEventType


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def comprehensive_data_generation_demo():
    """综合数据生成演示"""

    # 创建输出目录
    output_dir = "output/comprehensive"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/visualizations", exist_ok=True)
    os.makedirs(f"{output_dir}/data", exist_ok=True)

    print_section("🎯 Fin-Data-Maker 综合使用示例")
    print("\n本示例将演示:")
    print("✓ 1. 依赖关系分析")
    print("✓ 2. ER图和依赖图生成")
    print("✓ 3. 智能生成顺序确定")
    print("✓ 4. 带进度监控的数据生成")
    print("✓ 5. 数据质量验证")
    print("✓ 6. 多格式数据导出")
    print("\n按Enter键开始...")
    input()

    # ============================================================
    # 步骤1: 创建表定义
    # ============================================================
    print_section("步骤 1/6: 创建表定义")

    tables = [
        create_customer_table(),
        create_account_table(),
        create_transaction_table(),
        create_bond_table(),
        create_fund_table(),
        create_derivative_table(),
    ]

    print(f"✓ 已创建 {len(tables)} 个表定义:")
    for table in tables:
        field_count = len(table.fields)
        fk_count = sum(1 for f in table.fields if f.reference_table)
        print(f"  - {table.name:15s} ({field_count:2d} 字段, {fk_count} 个外键)")

    # ============================================================
    # 步骤2: 依赖关系分析
    # ============================================================
    print_section("步骤 2/6: 依赖关系分析")

    print("\n正在分析表间依赖关系...")
    analyzer = DependencyAnalyzer(tables)

    # 检测循环依赖
    cycles = analyzer.detect_cycles()
    if cycles:
        print(f"\n⚠️  警告: 检测到 {len(cycles)} 个循环依赖:")
        for i, cycle in enumerate(cycles, 1):
            print(f"  {i}. {cycle}")
        print("\n⛔ 由于存在循环依赖，无法继续生成数据")
        return
    else:
        print("\n✓ 未检测到循环依赖")

    # 获取生成顺序
    generation_order = analyzer.get_generation_order()
    print(f"\n✓ 推荐的数据生成顺序:")
    for i, table_name in enumerate(generation_order, 1):
        level = analyzer.get_dependency_levels()[table_name]
        print(f"  {i}. {table_name:15s} (层级 {level})")

    # 获取依赖层级分布
    levels = analyzer.get_dependency_levels()
    level_groups = {}
    for table, level in levels.items():
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(table)

    print(f"\n✓ 依赖层级分布:")
    for level in sorted(level_groups.keys()):
        tables_str = ", ".join(level_groups[level])
        print(f"  层级 {level}: {tables_str}")

    # 保存分析报告
    report_file = f"{output_dir}/dependency_analysis_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(analyzer.generate_report())
    print(f"\n✓ 分析报告已保存: {report_file}")

    # ============================================================
    # 步骤3: 生成ER图和可视化
    # ============================================================
    print_section("步骤 3/6: 生成ER图和可视化")

    visualizer = RelationshipVisualizer(tables)

    # 生成Mermaid ER图
    print("\n生成Mermaid格式ER图...")
    mermaid_file = f"{output_dir}/visualizations/er_diagram.mmd"
    visualizer.generate_mermaid(
        output_file=mermaid_file,
        show_fields=True,
        show_field_types=True
    )
    print(f"✓ Mermaid ER图: {mermaid_file}")

    # 生成Graphviz DOT格式
    print("生成Graphviz DOT格式ER图...")
    dot_file = f"{output_dir}/visualizations/er_diagram.dot"
    visualizer.generate_dot(
        output_file=dot_file,
        show_fields=True,
        show_field_types=True,
        highlight_keys=True
    )
    print(f"✓ Graphviz DOT图: {dot_file}")

    # 生成PlantUML格式
    print("生成PlantUML格式ER图...")
    plantuml_file = f"{output_dir}/visualizations/er_diagram.puml"
    visualizer.generate_plantuml(
        output_file=plantuml_file,
        show_fields=True,
        show_field_types=True
    )
    print(f"✓ PlantUML图: {plantuml_file}")

    # 生成依赖关系图
    print("生成依赖关系图...")
    dep_file = f"{output_dir}/visualizations/dependency_graph.mmd"
    visualizer.generate_dependency_diagram(
        output_file=dep_file,
        format=VisualizationFormat.MERMAID
    )
    print(f"✓ 依赖关系图: {dep_file}")

    print("\n✓ 图表文件已生成，可以使用以下在线工具查看:")
    print("  - Mermaid: https://mermaid.live/")
    print("  - Graphviz: https://dreampuf.github.io/GraphvizOnline/")
    print("  - PlantUML: http://www.plantuml.com/plantuml/uml/")

    # ============================================================
    # 步骤4: 准备数据生成环境
    # ============================================================
    print_section("步骤 4/6: 准备数据生成环境")

    # 创建应用实例
    app = DataMakerApp(seed=42)  # 使用固定种子以获得可重复结果

    # 添加所有表定义
    for table in tables:
        app.add_table(table)
    print(f"✓ 已添加 {len(tables)} 个表定义到应用")

    # 创建进度监控器
    monitor = ProgressMonitor()

    # 定义回调函数
    key_events = []

    def log_key_event(event):
        """记录关键事件"""
        if event.event_type in (
            ProgressEventType.TABLE_STARTED,
            ProgressEventType.TABLE_COMPLETED,
            ProgressEventType.VALIDATION_COMPLETED,
            ProgressEventType.ERROR
        ):
            key_events.append(event)

    def simple_progress(event):
        """简单进度显示"""
        if event.event_type == ProgressEventType.PROGRESS:
            print(f"\r  进度: {event.percentage:5.1f}% | {event.message}", end='', flush=True)
        elif event.event_type in (ProgressEventType.TABLE_COMPLETED, ProgressEventType.ERROR):
            print()  # 换行

    monitor.add_callback(log_key_event)
    monitor.add_callback(simple_progress)

    print("✓ 进度监控器已配置")

    # ============================================================
    # 步骤5: 按依赖顺序生成数据
    # ============================================================
    print_section("步骤 5/6: 按依赖顺序生成数据")

    # 定义每个表的生成数量
    generation_config = {
        'customer': 50,
        'account': 100,
        'transaction': 200,
        'bond': 30,
        'fund': 20,
        'derivative': 40,
    }

    print("\n数据生成计划:")
    for table_name in generation_order:
        if table_name in generation_config:
            count = generation_config[table_name]
            print(f"  {table_name:15s}: {count:4d} 条记录")

    print("\n开始生成数据...\n")
    time.sleep(1)

    # 存储生成的数据
    generated_data = {}
    validation_reports = {}

    for table_name in generation_order:
        if table_name not in generation_config:
            continue

        count = generation_config[table_name]
        print(f"\n【{table_name}】")

        # 通知监控器
        monitor.table_started(table_name, count)

        # 获取依赖数据
        related_data = {}
        dependencies = analyzer.graph.get_dependencies(table_name)

        if dependencies:
            for dep_table in dependencies:
                if dep_table in generated_data:
                    # 提取ID字段
                    id_field = f"{dep_table}_id"
                    related_data[dep_table] = [
                        item.get(id_field) for item in generated_data[dep_table]
                        if id_field in item
                    ]
            print(f"  依赖: {', '.join(dependencies)}")

        # 生成数据
        try:
            # 分批生成以更新进度
            batch_size = max(10, count // 5)
            all_data = []

            for batch_num in range(0, count, batch_size):
                batch_count = min(batch_size, count - batch_num)

                if related_data:
                    batch_data, report = app.generate_with_relations(
                        table_name,
                        count=batch_count,
                        related_data=related_data,
                        validate=(batch_num + batch_count >= count)  # 最后一批才验证
                    )
                else:
                    batch_data, report = app.generate_data(
                        table_name,
                        count=batch_count,
                        validate=(batch_num + batch_count >= count)
                    )

                all_data.extend(batch_data)

                # 更新进度
                monitor.update(
                    len(all_data),
                    f"已生成 {len(all_data)}/{count} 条"
                )

            generated_data[table_name] = all_data

            # 验证
            if report:
                validation_reports[table_name] = report
                monitor.validation_completed(
                    count,
                    is_valid=report.is_valid,
                    error_count=len(report.errors)
                )

                if report.is_valid:
                    print(f"  ✓ 数据验证通过")
                else:
                    print(f"  ⚠️  验证失败: {len(report.errors)} 个错误")

            monitor.table_completed(table_name, count)

        except Exception as e:
            print(f"  ✗ 生成失败: {e}")
            monitor.error(f"生成 {table_name} 失败", e)

    monitor.complete("所有数据生成完成！")

    # 显示关键事件
    print("\n" + "-" * 80)
    print("关键事件汇总:")
    print("-" * 80)
    for event in key_events:
        time_str = event.timestamp.strftime("%H:%M:%S")
        print(f"[{time_str}] {event.event_type.value:20s} | {event.message}")

    # ============================================================
    # 步骤6: 导出数据
    # ============================================================
    print_section("步骤 6/6: 导出数据")

    export_summary = []

    for table_name, data in generated_data.items():
        if not data:
            continue

        print(f"\n【{table_name}】")

        # 导出CSV
        csv_file = f"{output_dir}/data/{table_name}.csv"
        app.export_to_csv(data, table_name, csv_file)
        print(f"  ✓ CSV:   {csv_file}")

        # 导出JSON
        json_file = f"{output_dir}/data/{table_name}.json"
        app.export_to_json(data, table_name, json_file)
        print(f"  ✓ JSON:  {json_file}")

        # 导出Excel
        excel_file = f"{output_dir}/data/{table_name}.xlsx"
        app.export_to_excel(data, table_name, excel_file)
        print(f"  ✓ Excel: {excel_file}")

        export_summary.append({
            'table': table_name,
            'records': len(data),
            'csv': csv_file,
            'json': json_file,
            'excel': excel_file
        })

    # ============================================================
    # 总结报告
    # ============================================================
    print_section("📊 综合报告")

    # 统计信息
    total_records = sum(len(data) for data in generated_data.values())
    total_tables = len(generated_data)

    print(f"\n✓ 数据生成完成!")
    print(f"  - 表总数: {total_tables}")
    print(f"  - 记录总数: {total_records}")
    print(f"  - 导出文件: {total_tables * 3} 个")

    print(f"\n✓ 文件生成位置:")
    print(f"  - 数据文件: {output_dir}/data/")
    print(f"  - 可视化文件: {output_dir}/visualizations/")
    print(f"  - 分析报告: {output_dir}/")

    # 生成汇总报告
    summary_file = f"{output_dir}/generation_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Fin-Data-Maker 综合数据生成报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"表总数: {total_tables}\n")
        f.write(f"记录总数: {total_records}\n\n")

        f.write("生成顺序:\n")
        for i, table_name in enumerate(generation_order, 1):
            if table_name in generated_data:
                count = len(generated_data[table_name])
                f.write(f"  {i}. {table_name:15s}: {count:4d} 条记录\n")

        f.write("\n导出文件:\n")
        for item in export_summary:
            f.write(f"\n  {item['table']} ({item['records']} 条记录):\n")
            f.write(f"    CSV:   {item['csv']}\n")
            f.write(f"    JSON:  {item['json']}\n")
            f.write(f"    Excel: {item['excel']}\n")

        f.write("\n可视化文件:\n")
        f.write(f"  - ER图 (Mermaid): {mermaid_file}\n")
        f.write(f"  - ER图 (DOT): {dot_file}\n")
        f.write(f"  - ER图 (PlantUML): {plantuml_file}\n")
        f.write(f"  - 依赖关系图: {dep_file}\n")

        f.write("\n在线查看工具:\n")
        f.write("  - Mermaid: https://mermaid.live/\n")
        f.write("  - Graphviz: https://dreampuf.github.io/GraphvizOnline/\n")
        f.write("  - PlantUML: http://www.plantuml.com/plantuml/uml/\n")

    print(f"\n✓ 汇总报告已保存: {summary_file}")

    # 显示进度摘要
    print("\n" + monitor.get_summary())

    print("\n" + "=" * 80)
    print("✅ 综合示例执行完成！")
    print("=" * 80)
    print(f"\n所有文件已保存到: {output_dir}/")
    print("\n您可以:")
    print("  1. 查看CSV/JSON/Excel数据文件")
    print("  2. 使用在线工具查看ER图和依赖图")
    print("  3. 阅读分析报告和汇总报告")


if __name__ == '__main__':
    try:
        comprehensive_data_generation_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
