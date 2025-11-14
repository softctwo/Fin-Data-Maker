"""
数据源连接示例
演示如何连接数据库、提取表结构、分析数据质量并生成测试数据
"""

from src.datasource.db_connector import DatabaseConnector, DatabaseType
from src.datasource.metadata_extractor import MetadataExtractor
from src.datasource.data_profiler import DataProfiler
from src.core.app import DataMakerApp


def example_mysql():
    """MySQL数据库示例"""
    print("=" * 80)
    print("示例: 从MySQL数据库生成测试数据")
    print("=" * 80)

    # 步骤1: 创建数据库连接
    print("\n步骤1: 连接MySQL数据库")
    connector = DatabaseConnector(
        db_type=DatabaseType.MYSQL,
        host='localhost',
        port=3306,
        database='test_db',
        username='root',
        password='password'
    )

    try:
        connector.connect()
        print("✓ 连接成功")
    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        print("\n注意: 这只是一个示例，请修改为实际的数据库连接信息")
        return

    # 步骤2: 列出所有表
    print("\n步骤2: 列出所有表")
    tables = connector.list_tables()
    print(f"找到 {len(tables)} 个表:")
    for table in tables[:5]:  # 只显示前5个
        print(f"  - {table}")

    # 假设我们要提取第一个表
    if not tables:
        print("数据库中没有表")
        return

    table_name = tables[0]
    print(f"\n将提取表: {table_name}")

    # 步骤3: 提取表结构
    print("\n步骤3: 提取表结构")
    extractor = MetadataExtractor(connector)
    table = extractor.extract_table(table_name)

    print(f"✓ 表名: {table.name}")
    print(f"✓ 字段数: {len(table.fields)}")
    print(f"✓ 主键: {table.primary_key}")
    print("\n字段列表:")
    for field in table.fields[:10]:  # 只显示前10个
        print(f"  - {field.name}: {field.field_type.value} (必填: {field.required})")

    # 步骤4: 分析数据质量
    print("\n步骤4: 分析数据质量")
    profiler = DataProfiler(connector)
    profiles = profiler.profile_table(table, sample_size=100)

    print("✓ 数据质量分析完成")
    print("\n前3个字段的质量概要:")
    for i, (field_name, profile) in enumerate(list(profiles.items())[:3]):
        print(f"\n字段: {field_name}")
        print(f"  完整性: {profile.completeness_rate:.2%}")
        print(f"  唯一性: {profile.uniqueness_rate:.2%}")
        if profile.min_value is not None:
            print(f"  范围: [{profile.min_value}, {profile.max_value}]")
        if profile.min_length is not None:
            print(f"  长度: [{profile.min_length}, {profile.max_length}]")

    # 根据分析结果更新表定义
    print("\n步骤5: 根据数据分析更新表定义")
    table = profiler.update_table_metadata(table, profiles)
    print("✓ 表定义已更新")

    # 生成质量规则建议
    rules = profiler.generate_quality_rules(table, profiles, strictness='medium')
    print(f"\n数据质量规则建议（共 {len(rules)} 条）:")
    for i, rule in enumerate(rules[:5], 1):  # 只显示前5条
        print(f"  {i}. {rule}")

    # 步骤6: 生成测试数据
    print("\n步骤6: 生成测试数据")
    app = DataMakerApp(seed=42)
    app.add_table(table)

    data, report = app.generate_data(table.name, count=100, validate=True)
    print(f"✓ 生成了 {len(data)} 条测试数据")

    if report:
        print("\n验证结果:")
        print(report.get_summary())

    # 步骤7: 导出数据
    print("\n步骤7: 导出数据")
    output_file = f"output/{table_name}_test_data.csv"
    app.export_data(data, output_file, format='csv')
    print(f"✓ 数据已导出到: {output_file}")

    # 清理
    connector.disconnect()
    print("\n完成!")


def example_sqlite():
    """SQLite数据库示例（更容易测试）"""
    print("=" * 80)
    print("示例: 从SQLite数据库生成测试数据")
    print("=" * 80)

    # 为演示创建一个临时SQLite数据库
    import sqlite3
    import os

    db_path = "output/test.db"
    os.makedirs("output", exist_ok=True)

    # 创建示例表
    print("\n创建示例SQLite数据库...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            balance REAL,
            created_date TEXT
        )
    """)

    # 插入一些示例数据
    cursor.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, customer_name, email, phone, balance, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, '张三', 'zhang@example.com', '13812345678', 10000.50, '2024-01-01'),
        (2, '李四', 'li@example.com', '13912345678', 25000.00, '2024-01-02'),
        (3, '王五', 'wang@example.com', '13712345678', 8000.75, '2024-01-03'),
    ])

    conn.commit()
    conn.close()
    print("✓ 示例数据库创建完成")

    # 连接数据库
    print("\n步骤1: 连接SQLite数据库")
    connector = DatabaseConnector(
        db_type=DatabaseType.SQLITE,
        database=db_path
    )

    connector.connect()
    print("✓ 连接成功")

    # 列出表
    print("\n步骤2: 列出所有表")
    tables = connector.list_tables()
    print(f"找到表: {tables}")

    # 提取表结构
    print("\n步骤3: 提取表结构")
    extractor = MetadataExtractor(connector)
    table = extractor.extract_table('customers')

    print(f"✓ 表名: {table.name}")
    print(f"✓ 字段数: {len(table.fields)}")
    print("\n字段列表:")
    for field in table.fields:
        print(f"  - {field.name}: {field.field_type.value}")

    # 分析数据质量
    print("\n步骤4: 分析数据质量")
    profiler = DataProfiler(connector)
    profiles = profiler.profile_table(table, sample_size=10)

    # 显示分析报告
    report = profiler.generate_profile_report('customers', profiles)
    print(report)

    # 更新表定义
    table = profiler.update_table_metadata(table, profiles)

    # 生成测试数据
    print("\n步骤5: 生成测试数据")
    app = DataMakerApp(seed=42)
    app.add_table(table)

    data, validation_report = app.generate_data(table.name, count=50, validate=True)
    print(f"✓ 生成了 {len(data)} 条测试数据")

    if validation_report:
        print("\n验证结果:")
        print(validation_report.get_summary())

    # 导出数据
    print("\n步骤6: 导出数据")
    app.export_data(data, "output/customers_test_data.csv", format='csv')
    app.export_data(data, "output/customers_test_data.json", format='json')
    print("✓ 数据已导出")

    # 清理
    connector.disconnect()
    print("\n完成!")


def main():
    """主函数"""
    print("Fin-Data-Maker - 数据源连接示例\n")

    # 运行SQLite示例（容易测试）
    example_sqlite()

    print("\n\n" + "=" * 80)
    print("如需测试MySQL等其他数据库，请修改 example_mysql() 中的连接信息")
    print("=" * 80)


if __name__ == "__main__":
    main()
