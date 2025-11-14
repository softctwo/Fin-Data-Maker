"""
基础示例：生成客户、账户和交易数据
演示如何使用Fin-Data-Maker生成金融测试数据
"""

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_customer_table,
    create_account_table,
    create_transaction_table,
)


def main():
    """主函数"""
    # 创建应用实例
    app = DataMakerApp(seed=42)  # 使用固定种子以便生成可重复的数据

    print("=" * 60)
    print("金融数据生成系统 - 基础示例")
    print("=" * 60)

    # 1. 添加表定义
    print("\n步骤1: 添加表定义")
    customer_table = create_customer_table()
    account_table = create_account_table()
    transaction_table = create_transaction_table()

    app.add_table(customer_table)
    app.add_table(account_table)
    app.add_table(transaction_table)
    print("✓ 已添加客户表、账户表、交易表定义")

    # 2. 生成客户数据
    print("\n步骤2: 生成客户数据")
    customer_data, customer_report = app.generate_data("customer", count=100)
    print(f"✓ 已生成 {len(customer_data)} 条客户数据")
    print(f"  验证结果: {customer_report.get_summary()}")

    # 导出客户数据
    app.export_data(customer_data, "output/customers.csv", format='csv')
    app.export_data(customer_data, "output/customers.json", format='json')
    app.export_data(customer_data, "output/customers.xlsx", format='excel')
    print("✓ 已导出客户数据到 output/ 目录")

    # 3. 生成账户数据（关联客户）
    print("\n步骤3: 生成账户数据")
    # 提取客户ID列表用于关联
    customer_ids = [c['customer_id'] for c in customer_data]

    account_data, account_report = app.generate_with_relations(
        "account",
        count=200,
        related_data={"customer": customer_ids}
    )
    print(f"✓ 已生成 {len(account_data)} 条账户数据")
    print(f"  验证结果: {account_report.get_summary()}")

    # 导出账户数据
    app.export_data(account_data, "output/accounts.csv", format='csv')
    print("✓ 已导出账户数据")

    # 4. 生成交易数据（关联账户）
    print("\n步骤4: 生成交易数据")
    # 提取账户ID列表用于关联
    account_ids = [a['account_id'] for a in account_data]

    transaction_data, transaction_report = app.generate_with_relations(
        "transaction",
        count=1000,
        related_data={"account": account_ids}
    )
    print(f"✓ 已生成 {len(transaction_data)} 条交易数据")
    print(f"  验证结果: {transaction_report.get_summary()}")

    # 导出交易数据
    app.export_data(transaction_data, "output/transactions.csv", format='csv')
    print("✓ 已导出交易数据")

    # 5. 统计信息
    print("\n" + "=" * 60)
    print("生成完成! 统计信息:")
    print("=" * 60)
    print(f"客户数量: {len(customer_data)}")
    print(f"账户数量: {len(account_data)}")
    print(f"交易数量: {len(transaction_data)}")
    print("\n数据已保存到 output/ 目录:")
    print("  - customers.csv / customers.json / customers.xlsx")
    print("  - accounts.csv")
    print("  - transactions.csv")


if __name__ == "__main__":
    main()
