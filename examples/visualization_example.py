"""
数据关系可视化、依赖分析和进度监控示例

本示例演示以下功能：
1. 表间依赖关系分析
2. 数据关系图可视化（Graphviz/Mermaid/PlantUML）
3. 数据生成过程实时进度监控
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_customer_table,
    create_account_table,
    create_bond_table,
    create_fund_table,
    create_derivative_table,
)
from src.analysis.dependency_analyzer import DependencyAnalyzer
from src.visualization.relationship_visualizer import RelationshipVisualizer, VisualizationFormat
from src.core.progress_monitor import (
    ProgressMonitor,
    console_callback,
    simple_progress_bar_callback,
    ProgressEventType
)


def demo_dependency_analysis():
    """演示依赖关系分析"""
    print("\n" + "=" * 60)
    print("功能演示 1: 表间依赖关系分析")
    print("=" * 60)

    # 创建表定义
    tables = [
        create_customer_table(),
        create_account_table(),
        create_bond_table(),
        create_fund_table(),
        create_derivative_table(),
    ]

    # 创建依赖分析器
    analyzer = DependencyAnalyzer(tables)

    # 生成并打印分析报告
    print(analyzer.generate_report())

    # 详细分析bond表
    print("\n" + "-" * 60)
    print("详细分析：债券表")
    print("-" * 60)

    bond_analysis = analyzer.analyze_table('bond')
    print(f"表名: {bond_analysis['table_name']}")
    print(f"依赖于: {', '.join(bond_analysis['dependencies']) if bond_analysis['dependencies'] else '无'}")
    print(f"被依赖: {', '.join(bond_analysis['dependents']) if bond_analysis['dependents'] else '无'}")
    print(f"依赖层级: {bond_analysis['dependency_level']}")
    print(f"是否为根表: {'是' if bond_analysis['is_root'] else '否'}")
    print(f"是否为叶子表: {'是' if bond_analysis['is_leaf'] else '否'}")
    print(f"完整依赖链: {' → '.join(bond_analysis['dependency_chain'])}")

    # 获取推荐的生成顺序
    print("\n" + "-" * 60)
    print("推荐的数据生成顺序:")
    print("-" * 60)

    try:
        order = analyzer.get_generation_order()
        for i, table_name in enumerate(order, 1):
            print(f"{i}. {table_name}")
    except ValueError as e:
        print(f"错误: {e}")


def demo_relationship_visualization():
    """演示关系可视化"""
    print("\n" + "=" * 60)
    print("功能演示 2: 数据关系图可视化")
    print("=" * 60)

    # 创建表定义
    tables = [
        create_customer_table(),
        create_account_table(),
        create_bond_table(),
        create_fund_table(),
        create_derivative_table(),
    ]

    # 创建可视化器
    visualizer = RelationshipVisualizer(tables)

    # 创建输出目录
    output_dir = "output/visualizations"
    os.makedirs(output_dir, exist_ok=True)

    # 1. 生成Mermaid格式的ER图
    print("\n生成Mermaid格式ER图...")
    mermaid_file = f"{output_dir}/er_diagram.mmd"
    mermaid_content = visualizer.generate_mermaid(
        output_file=mermaid_file,
        show_fields=True,
        show_field_types=True
    )
    print(f"✓ 已保存到: {mermaid_file}")
    print("\n预览（前20行）:")
    print('\n'.join(mermaid_content.split('\n')[:20]))

    # 2. 生成Graphviz DOT格式的ER图
    print("\n生成Graphviz DOT格式ER图...")
    dot_file = f"{output_dir}/er_diagram.dot"
    dot_content = visualizer.generate_dot(
        output_file=dot_file,
        show_fields=True,
        show_field_types=True,
        highlight_keys=True
    )
    print(f"✓ 已保存到: {dot_file}")

    # 3. 生成PlantUML格式的ER图
    print("\n生成PlantUML格式ER图...")
    plantuml_file = f"{output_dir}/er_diagram.puml"
    plantuml_content = visualizer.generate_plantuml(
        output_file=plantuml_file,
        show_fields=True,
        show_field_types=True
    )
    print(f"✓ 已保存到: {plantuml_file}")

    # 4. 生成简化的依赖关系图
    print("\n生成简化依赖关系图（Mermaid）...")
    dep_file = f"{output_dir}/dependency_graph.mmd"
    dep_content = visualizer.generate_dependency_diagram(
        output_file=dep_file,
        format=VisualizationFormat.MERMAID
    )
    print(f"✓ 已保存到: {dep_file}")
    print("\n预览:")
    print(dep_content)

    # 5. 尝试渲染为图片（需要安装graphviz）
    print("\n尝试渲染DOT文件为PNG图片...")
    try:
        png_file = f"{output_dir}/er_diagram"
        visualizer.render_dot_to_image(dot_content, png_file, format='png')
        print(f"✓ 已保存到: {png_file}.png")
    except ImportError as e:
        print(f"⚠️  {e}")
        print("   提示: 可以使用在线工具查看DOT文件:")
        print("   - Graphviz Online: https://dreampuf.github.io/GraphvizOnline/")
        print("   - Mermaid Live: https://mermaid.live/")

    print("\n" + "=" * 60)
    print("可视化文件已生成！")
    print("=" * 60)
    print(f"\n查看方式:")
    print(f"1. Mermaid文件 (.mmd): 在线查看 https://mermaid.live/")
    print(f"2. DOT文件 (.dot): 在线查看 https://dreampuf.github.io/GraphvizOnline/")
    print(f"3. PlantUML文件 (.puml): 在线查看 http://www.plantuml.com/plantuml/uml/")


def demo_progress_monitoring():
    """演示进度监控"""
    print("\n" + "=" * 60)
    print("功能演示 3: 数据生成实时进度监控")
    print("=" * 60)

    # 创建应用
    app = DataMakerApp(seed=42)

    # 添加表定义
    customer_table = create_customer_table()
    bond_table = create_bond_table()
    app.add_table(customer_table)
    app.add_table(bond_table)

    # 创建进度监控器
    monitor = ProgressMonitor()

    # 添加回调函数
    # monitor.add_callback(console_callback)  # 详细控制台输出
    monitor.add_callback(simple_progress_bar_callback)  # 简单进度条

    # 自定义回调：记录关键事件
    key_events = []

    def custom_callback(event):
        if event.event_type in (
            ProgressEventType.STARTED,
            ProgressEventType.TABLE_STARTED,
            ProgressEventType.TABLE_COMPLETED,
            ProgressEventType.VALIDATION_STARTED,
            ProgressEventType.VALIDATION_COMPLETED,
            ProgressEventType.COMPLETED
        ):
            key_events.append(event)

    monitor.add_callback(custom_callback)

    # 模拟数据生成过程
    print("\n开始生成客户数据...")
    monitor.table_started("customer", 50)

    # 生成客户数据
    customer_data = []
    batch_size = 10
    for i in range(5):
        # 模拟生成
        time.sleep(0.2)  # 模拟处理时间
        customer_batch = app.generate_data("customer", count=batch_size, validate=False)[0]
        customer_data.extend(customer_batch)

        monitor.batch_completed(batch_size, i + 1)
        monitor.update((i + 1) * batch_size, f"生成客户数据批次 {i + 1}")

    monitor.table_completed("customer", 50)

    print("\n")  # 进度条换行

    # 验证数据
    print("\n验证客户数据...")
    monitor.validation_started(50)
    time.sleep(0.3)  # 模拟验证时间
    monitor.validation_completed(50, is_valid=True)

    # 生成债券数据
    print("\n开始生成债券数据...")
    monitor.table_started("bond", 100)

    customer_ids = [c['customer_id'] for c in customer_data]
    bond_data = []
    batch_size = 20
    for i in range(5):
        # 模拟生成
        time.sleep(0.2)  # 模拟处理时间
        bond_batch = app.generate_with_relations(
            "bond",
            count=batch_size,
            related_data={"customer": customer_ids},
            validate=False
        )[0]
        bond_data.extend(bond_batch)

        monitor.batch_completed(batch_size, i + 1)
        monitor.update((i + 1) * batch_size, f"生成债券数据批次 {i + 1}")

    monitor.table_completed("bond", 100)

    print("\n")  # 进度条换行

    # 验证数据
    print("\n验证债券数据...")
    monitor.validation_started(100)
    time.sleep(0.3)  # 模拟验证时间
    monitor.validation_completed(100, is_valid=True)

    # 完成
    monitor.complete("所有数据生成完成！")

    # 显示关键事件摘要
    print("\n" + "-" * 60)
    print("关键事件摘要:")
    print("-" * 60)

    for event in key_events:
        timestamp = event.timestamp.strftime("%H:%M:%S")
        print(f"[{timestamp}] {event.event_type.value}: {event.message}")

    # 显示进度摘要
    print(monitor.get_summary())


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Fin-Data-Maker 新功能演示")
    print("=" * 60)
    print("\n本示例将演示以下三个新功能:")
    print("1. 表间依赖关系分析")
    print("2. 数据关系图可视化")
    print("3. 数据生成实时进度监控")

    try:
        # 1. 依赖关系分析
        demo_dependency_analysis()

        # 2. 关系可视化
        demo_relationship_visualization()

        # 3. 进度监控
        demo_progress_monitoring()

        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
