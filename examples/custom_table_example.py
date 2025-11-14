"""
自定义表示例：创建自定义的数据表定义
演示如何定义自己的数据模型
"""

from src.core.app import DataMakerApp
from src.metadata.table import Table
from src.metadata.field import Field, FieldType


def create_insurance_policy_table() -> Table:
    """
    创建保险单表定义
    演示如何自定义表结构
    """
    table = Table(
        name="insurance_policy",
        description="保险单信息表",
        primary_key="policy_id",
    )

    fields = [
        Field(
            name="policy_id",
            field_type=FieldType.ID,
            description="保单唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="policy_no",
            field_type=FieldType.STRING,
            description="保单号",
            required=True,
            unique=True,
            length=30,
        ),
        Field(
            name="customer_name",
            field_type=FieldType.STRING,
            description="投保人姓名",
            required=True,
            min_length=2,
            max_length=50,
        ),
        Field(
            name="product_type",
            field_type=FieldType.ENUM,
            description="产品类型",
            required=True,
            enum_values=["人寿保险", "健康保险", "意外保险", "财产保险", "车险"],
        ),
        Field(
            name="premium",
            field_type=FieldType.AMOUNT,
            description="保费",
            required=True,
            min_value=100,
            max_value=100000,
            precision=2,
        ),
        Field(
            name="insured_amount",
            field_type=FieldType.AMOUNT,
            description="保额",
            required=True,
            min_value=10000,
            max_value=10000000,
            precision=2,
        ),
        Field(
            name="start_date",
            field_type=FieldType.DATE,
            description="起保日期",
            required=True,
        ),
        Field(
            name="end_date",
            field_type=FieldType.DATE,
            description="终保日期",
            required=True,
        ),
        Field(
            name="payment_frequency",
            field_type=FieldType.ENUM,
            description="缴费频率",
            required=True,
            enum_values=["年缴", "半年缴", "季缴", "月缴", "一次性"],
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="保单状态",
            required=True,
            enum_values=["有效", "失效", "理赔中", "已赔付", "已退保"],
            default_value="有效",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def main():
    """主函数"""
    # 创建应用实例
    app = DataMakerApp(seed=123)

    print("=" * 60)
    print("自定义表示例 - 保险单数据生成")
    print("=" * 60)

    # 1. 添加自定义表定义
    print("\n添加自定义保险单表定义...")
    policy_table = create_insurance_policy_table()
    app.add_table(policy_table)
    print("✓ 已添加保险单表定义")

    # 2. 生成数据
    print("\n生成保险单数据...")
    data, report = app.generate_data("insurance_policy", count=500)
    print(f"✓ 已生成 {len(data)} 条保险单数据")

    # 3. 验证结果
    if report:
        print("\n验证结果:")
        print(report.get_summary())
        if report.violations:
            print("\n前5条违规记录:")
            for v in report.violations[:5]:
                print(f"  - {v.message}")

    # 4. 导出数据
    print("\n导出数据...")
    app.export_data(data, "output/insurance_policies.csv", format='csv')
    app.export_data(data, "output/insurance_policies.xlsx", format='excel')
    print("✓ 已导出到 output/insurance_policies.csv 和 .xlsx")

    # 5. 显示样本数据
    print("\n样本数据（前3条）:")
    for i, record in enumerate(data[:3], 1):
        print(f"\n记录 {i}:")
        for key, value in record.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
