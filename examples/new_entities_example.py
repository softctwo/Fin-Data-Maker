"""
新金融实体示例：生成债券、基金、衍生品数据
演示如何使用Fin-Data-Maker生成新增的金融实体测试数据
"""

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_customer_table,
    create_bond_table,
    create_fund_table,
    create_derivative_table,
)


def main():
    """主函数"""
    # 创建应用实例
    app = DataMakerApp(seed=42)  # 使用固定种子以便生成可重复的数据

    print("=" * 60)
    print("金融数据生成系统 - 新金融实体示例")
    print("=" * 60)

    # 1. 添加表定义
    print("\n步骤1: 添加表定义")
    customer_table = create_customer_table()
    bond_table = create_bond_table()
    fund_table = create_fund_table()
    derivative_table = create_derivative_table()

    app.add_table(customer_table)
    app.add_table(bond_table)
    app.add_table(fund_table)
    app.add_table(derivative_table)
    print("✓ 已添加客户表、债券表、基金表、衍生品表定义")

    # 2. 生成客户数据（作为发行人/基金经理）
    print("\n步骤2: 生成客户数据")
    customer_data, customer_report = app.generate_data("customer", count=50)
    print(f"✓ 已生成 {len(customer_data)} 条客户数据")
    print(f"  验证结果: {customer_report.get_summary()}")

    # 导出客户数据
    app.export_data(customer_data, "output/new_entities_customers.csv", format='csv')
    print("✓ 已导出客户数据到 output/ 目录")

    # 提取客户ID列表用于关联
    customer_ids = [c['customer_id'] for c in customer_data]

    # 3. 生成债券数据（关联客户作为发行人）
    print("\n步骤3: 生成债券数据")
    bond_data, bond_report = app.generate_with_relations(
        "bond",
        count=100,
        related_data={"customer": customer_ids}
    )
    print(f"✓ 已生成 {len(bond_data)} 条债券数据")
    print(f"  验证结果: {bond_report.get_summary()}")

    # 显示部分债券数据示例
    if bond_data:
        print("\n  债券数据示例:")
        sample = bond_data[0]
        print(f"    债券代码: {sample['bond_code']}")
        print(f"    债券名称: {sample['bond_name']}")
        print(f"    债券类型: {sample['bond_type']}")
        print(f"    票面利率: {sample['coupon_rate']}%")
        print(f"    信用评级: {sample['credit_rating']}")

    # 导出债券数据
    app.export_data(bond_data, "output/bonds.csv", format='csv')
    app.export_data(bond_data, "output/bonds.json", format='json')
    app.export_data(bond_data, "output/bonds.xlsx", format='excel')
    print("✓ 已导出债券数据")

    # 4. 生成基金数据（关联客户作为基金经理）
    print("\n步骤4: 生成基金数据")
    fund_data, fund_report = app.generate_with_relations(
        "fund",
        count=80,
        related_data={"customer": customer_ids}
    )
    print(f"✓ 已生成 {len(fund_data)} 条基金数据")
    print(f"  验证结果: {fund_report.get_summary()}")

    # 显示部分基金数据示例
    if fund_data:
        print("\n  基金数据示例:")
        sample = fund_data[0]
        print(f"    基金代码: {sample['fund_code']}")
        print(f"    基金名称: {sample['fund_name']}")
        print(f"    基金类型: {sample['fund_type']}")
        print(f"    单位净值: {sample['net_value']}")
        print(f"    风险等级: {sample['risk_level']}")

    # 导出基金数据
    app.export_data(fund_data, "output/funds.csv", format='csv')
    app.export_data(fund_data, "output/funds.json", format='json')
    app.export_data(fund_data, "output/funds.xlsx", format='excel')
    print("✓ 已导出基金数据")

    # 5. 生成衍生品数据
    print("\n步骤5: 生成衍生品数据")
    derivative_data, derivative_report = app.generate_data(
        "derivative",
        count=120
    )
    print(f"✓ 已生成 {len(derivative_data)} 条衍生品数据")
    print(f"  验证结果: {derivative_report.get_summary()}")

    # 显示部分衍生品数据示例
    if derivative_data:
        print("\n  衍生品数据示例:")
        sample = derivative_data[0]
        print(f"    合约代码: {sample['contract_code']}")
        print(f"    合约名称: {sample['contract_name']}")
        print(f"    衍生品类型: {sample['derivative_type']}")
        print(f"    标的资产类型: {sample['underlying_asset_type']}")
        print(f"    交易所: {sample['exchange']}")

    # 导出衍生品数据
    app.export_data(derivative_data, "output/derivatives.csv", format='csv')
    app.export_data(derivative_data, "output/derivatives.json", format='json')
    app.export_data(derivative_data, "output/derivatives.xlsx", format='excel')
    print("✓ 已导出衍生品数据")

    # 6. 统计信息
    print("\n" + "=" * 60)
    print("生成完成! 统计信息:")
    print("=" * 60)
    print(f"客户数量: {len(customer_data)} (作为发行人/基金经理)")
    print(f"债券数量: {len(bond_data)}")
    print(f"基金数量: {len(fund_data)}")
    print(f"衍生品数量: {len(derivative_data)}")
    print(f"\n总计: {len(customer_data) + len(bond_data) + len(fund_data) + len(derivative_data)} 条记录")

    print("\n数据已保存到 output/ 目录:")
    print("  - bonds.csv / bonds.json / bonds.xlsx")
    print("  - funds.csv / funds.json / funds.xlsx")
    print("  - derivatives.csv / derivatives.json / derivatives.xlsx")

    print("\n" + "=" * 60)
    print("新增金融实体类型:")
    print("=" * 60)
    print("1. 债券 (Bond):")
    print("   - 支持8种债券类型: 国债、地方政府债、政策性金融债、企业债、公司债、可转债、短期融资券、中期票据")
    print("   - 包含票面利率、信用评级、付息频率等关键字段")
    print("\n2. 基金 (Fund):")
    print("   - 支持9种基金类型: 股票型、债券型、混合型、货币型、指数型、QDII、ETF、LOF、FOF")
    print("   - 包含净值、规模、费率、风险等级等关键字段")
    print("\n3. 衍生品 (Derivative):")
    print("   - 支持6种衍生品类型: 期货、期权、互换、远期、结构化产品、权证")
    print("   - 包含标的资产、合约规模、行权价格、保证金比例等关键字段")


if __name__ == "__main__":
    main()
