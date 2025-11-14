#!/usr/bin/env python
"""
从Python生成的数据转换为SQL INSERT语句
使用Fin-Data-Maker生成数据，然后转换为SQL格式
"""

import sys
import os
from datetime import date, datetime
from decimal import Decimal

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_customer_table,
    create_bond_table,
    create_fund_table,
    create_derivative_table,
)


def format_sql_value(value):
    """格式化Python值为SQL值"""
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return '1' if value else '0'
    elif isinstance(value, (int, float, Decimal)):
        return str(value)
    elif isinstance(value, (date, datetime)):
        return f"'{value.strftime('%Y-%m-%d')}'"
    elif isinstance(value, str):
        # 转义单引号
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    else:
        return f"'{str(value)}'"


def generate_insert_statement(table_name, data_list):
    """生成INSERT语句"""
    if not data_list:
        return ""

    # 获取字段列表
    fields = list(data_list[0].keys())

    sql_lines = []
    sql_lines.append(f"-- {table_name} 数据")
    sql_lines.append(f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES")

    # 生成每行数据
    values_lines = []
    for row in data_list:
        values = [format_sql_value(row[field]) for field in fields]
        values_lines.append(f"({', '.join(values)})")

    sql_lines.append(',\n'.join(values_lines) + ';')
    sql_lines.append('')

    return '\n'.join(sql_lines)


def main():
    """主函数"""
    print("=" * 60)
    print("SQL INSERT语句生成器")
    print("=" * 60)

    # 创建应用实例
    app = DataMakerApp(seed=42)

    # 添加表定义
    print("\n步骤1: 添加表定义")
    customer_table = create_customer_table()
    bond_table = create_bond_table()
    fund_table = create_fund_table()
    derivative_table = create_derivative_table()

    app.add_table(customer_table)
    app.add_table(bond_table)
    app.add_table(fund_table)
    app.add_table(derivative_table)
    print("✓ 表定义添加完成")

    # 生成数据
    print("\n步骤2: 生成测试数据")
    customer_data, _ = app.generate_data("customer", count=20)
    print(f"✓ 已生成 {len(customer_data)} 条客户数据")

    customer_ids = [c['customer_id'] for c in customer_data]

    bond_data, _ = app.generate_with_relations(
        "bond", count=30, related_data={"customer": customer_ids}
    )
    print(f"✓ 已生成 {len(bond_data)} 条债券数据")

    fund_data, _ = app.generate_with_relations(
        "fund", count=25, related_data={"customer": customer_ids}
    )
    print(f"✓ 已生成 {len(fund_data)} 条基金数据")

    derivative_data, _ = app.generate_data("derivative", count=40)
    print(f"✓ 已生成 {len(derivative_data)} 条衍生品数据")

    # 生成SQL语句
    print("\n步骤3: 生成SQL INSERT语句")

    output_file = 'sql/generated_test_data.sql'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- 自动生成的测试数据\n")
        f.write("-- 由 generate_sql_inserts.py 生成\n")
        f.write("-- ============================================================\n\n")
        f.write("SET NAMES utf8mb4;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        # 客户数据
        f.write(generate_insert_statement('customer', customer_data))
        f.write('\n')

        # 债券数据
        f.write(generate_insert_statement('bond', bond_data))
        f.write('\n')

        # 基金数据
        f.write(generate_insert_statement('fund', fund_data))
        f.write('\n')

        # 衍生品数据
        f.write(generate_insert_statement('derivative', derivative_data))
        f.write('\n')

        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")

        # 统计信息
        f.write("-- 数据统计\n")
        f.write("SELECT '客户数据' AS '表名', COUNT(*) AS '记录数' FROM customer\n")
        f.write("UNION ALL\n")
        f.write("SELECT '债券数据', COUNT(*) FROM bond\n")
        f.write("UNION ALL\n")
        f.write("SELECT '基金数据', COUNT(*) FROM fund\n")
        f.write("UNION ALL\n")
        f.write("SELECT '衍生品数据', COUNT(*) FROM derivative;\n")

    print(f"✓ SQL文件已生成: {output_file}")

    # 统计信息
    print("\n" + "=" * 60)
    print("生成完成!")
    print("=" * 60)
    print(f"总记录数: {len(customer_data) + len(bond_data) + len(fund_data) + len(derivative_data)}")
    print(f"  - 客户: {len(customer_data)} 条")
    print(f"  - 债券: {len(bond_data)} 条")
    print(f"  - 基金: {len(fund_data)} 条")
    print(f"  - 衍生品: {len(derivative_data)} 条")
    print(f"\n输出文件: {output_file}")
    print("\n使用方法:")
    print(f"  mysql -u root -p fin_data_maker < {output_file}")


if __name__ == "__main__":
    main()
