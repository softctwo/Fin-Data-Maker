"""
高级功能演示：增量数据生成和新增数据质量规则

演示内容：
1. 增量数据生成
2. 新增的6种数据质量规则
"""

from src.core.app import DataMakerApp
from src.financial.schemas import create_customer_table, create_transaction_table
from src.rules.builtin_rules import (
    TemporalRule, LengthRule, FormatRule,
    EnumRule, DistributionRule, CorrelationRule
)


def demo_incremental_generation():
    """演示增量数据生成功能"""
    print("=" * 70)
    print("示例1: 增量数据生成")
    print("=" * 70)

    # 创建应用
    app = DataMakerApp(seed=42)

    # 添加客户表
    customer_table = create_customer_table()
    app.add_table(customer_table)

    # 第一步：生成初始数据
    print("\n第一步：生成初始客户数据...")
    initial_data, _ = app.generate_data('customer', count=10, validate=False)

    print(f"✓ 生成了 {len(initial_data)} 条初始数据")
    print(f"  - 客户ID范围: {initial_data[0]['customer_id']} - {initial_data[-1]['customer_id']}")
    print(f"  - 创建日期: {initial_data[0]['created_at']} - {initial_data[-1]['created_at']}")

    # 第二步：生成增量数据
    print("\n第二步：生成增量数据...")
    incremental_data, _ = app.generate_incremental_data(
        'customer',
        existing_data=initial_data,
        count=5,
        validate=False
    )

    print(f"✓ 生成了 {len(incremental_data)} 条增量数据")
    print(f"  - 客户ID范围: {incremental_data[0]['customer_id']} - {incremental_data[-1]['customer_id']}")
    print(f"  - 创建日期: {incremental_data[0]['created_at']} - {incremental_data[-1]['created_at']}")

    # 合并数据
    all_data = initial_data + incremental_data
    print(f"\n合并后总数据量: {len(all_data)} 条")

    # 显示部分数据
    print("\n前3条数据示例:")
    for i, record in enumerate(all_data[:3], 1):
        print(f"  {i}. ID: {record['customer_id']}, 姓名: {record['customer_name']}, "
              f"创建时间: {record['created_at']}")


def demo_temporal_rule():
    """演示时序规则"""
    print("\n" + "=" * 70)
    print("示例2: 时序规则 (TemporalRule)")
    print("=" * 70)

    from src.metadata.table import Table
    from src.metadata.field import Field, FieldType

    # 创建订单表
    order_table = Table(
        name="order",
        description="订单表",
        primary_key="order_id"
    )

    order_table.add_field(Field(
        name="order_id",
        field_type=FieldType.INTEGER,
        required=True,
        unique=True
    ))

    order_table.add_field(Field(
        name="order_date",
        field_type=FieldType.DATE,
        required=True
    ))

    order_table.add_field(Field(
        name="ship_date",
        field_type=FieldType.DATE
    ))

    # 添加时序规则：订单日期必须早于发货日期
    temporal_rule = TemporalRule('order_date', 'ship_date')
    order_table.add_rule(temporal_rule)

    # 生成数据并验证
    app = DataMakerApp(seed=42)
    app.add_table(order_table)

    data, report = app.generate_data('order', count=100, validate=True)

    print(f"\n✓ 生成了 {len(data)} 条订单数据")
    print(f"✓ 时序规则验证通过")
    if report:
        print(f"  - 验证规则数: {len(report.rules_checked)}")
        print(f"  - 错误数: {len(report.errors)}")


def demo_length_rule():
    """演示长度规则"""
    print("\n" + "=" * 70)
    print("示例3: 长度规则 (LengthRule)")
    print("=" * 70)

    from src.metadata.table import Table
    from src.metadata.field import Field, FieldType

    # 创建用户表
    user_table = Table(name="user", description="用户表", primary_key="user_id")

    user_table.add_field(Field(
        name="user_id",
        field_type=FieldType.INTEGER,
        required=True
    ))

    user_table.add_field(Field(
        name="username",
        field_type=FieldType.STRING,
        required=True,
        max_length=20
    ))

    user_table.add_field(Field(
        name="password",
        field_type=FieldType.STRING,
        required=True
    ))

    # 添加长度规则
    username_length_rule = LengthRule('username', min_length=3, max_length=20)
    password_length_rule = LengthRule('password', min_length=6)

    user_table.add_rule(username_length_rule)
    user_table.add_rule(password_length_rule)

    # 生成数据
    app = DataMakerApp(seed=42)
    app.add_table(user_table)

    data, report = app.generate_data('user', count=50, validate=True)

    print(f"\n✓ 生成了 {len(data)} 条用户数据")
    print(f"✓ 长度规则验证通过")
    print(f"  - 用户名长度: 3-20个字符")
    print(f"  - 密码长度: 最少6个字符")


def demo_format_rule():
    """演示格式规则"""
    print("\n" + "=" * 70)
    print("示例4: 格式规则 (FormatRule)")
    print("=" * 70)

    from src.metadata.table import Table
    from src.metadata.field import Field, FieldType

    # 创建联系人表
    contact_table = Table(name="contact", description="联系人表", primary_key="contact_id")

    contact_table.add_field(Field(name="contact_id", field_type=FieldType.INTEGER, required=True))
    contact_table.add_field(Field(name="email", field_type=FieldType.EMAIL, required=True))
    contact_table.add_field(Field(name="phone", field_type=FieldType.PHONE, required=True))

    # 添加格式规则
    email_rule = FormatRule('email', 'email')
    phone_rule = FormatRule('phone', 'phone')

    contact_table.add_rule(email_rule)
    contact_table.add_rule(phone_rule)

    # 生成数据
    app = DataMakerApp(seed=42)
    app.add_table(contact_table)

    data, report = app.generate_data('contact', count=30, validate=True)

    print(f"\n✓ 生成了 {len(data)} 条联系人数据")
    print(f"✓ 格式规则验证通过")
    print("\n前5条数据:")
    for i, record in enumerate(data[:5], 1):
        print(f"  {i}. 邮箱: {record['email']}, 电话: {record['phone']}")


def demo_enum_rule():
    """演示枚举规则"""
    print("\n" + "=" * 70)
    print("示例5: 枚举规则 (EnumRule)")
    print("=" * 70)

    from src.metadata.table import Table
    from src.metadata.field import Field, FieldType

    # 创建产品表
    product_table = Table(name="product", description="产品表", primary_key="product_id")

    product_table.add_field(Field(name="product_id", field_type=FieldType.INTEGER, required=True))
    product_table.add_field(Field(name="product_name", field_type=FieldType.STRING, required=True))
    product_table.add_field(Field(
        name="status",
        field_type=FieldType.ENUM,
        enum_values=['active', 'inactive', 'discontinued']
    ))

    # 添加枚举规则
    status_rule = EnumRule('status', ['active', 'inactive', 'discontinued'])
    product_table.add_rule(status_rule)

    # 生成数据
    app = DataMakerApp(seed=42)
    app.add_table(product_table)

    data, report = app.generate_data('product', count=40, validate=True)

    print(f"\n✓ 生成了 {len(data)} 条产品数据")
    print(f"✓ 枚举规则验证通过")

    # 统计状态分布
    status_count = {}
    for record in data:
        status = record.get('status')
        status_count[status] = status_count.get(status, 0) + 1

    print("\n状态分布:")
    for status, count in sorted(status_count.items()):
        print(f"  - {status}: {count} ({count/len(data)*100:.1f}%)")


def demo_distribution_rule():
    """演示分布规则"""
    print("\n" + "=" * 70)
    print("示例6: 分布规则 (DistributionRule)")
    print("=" * 70)

    from src.metadata.table import Table
    from src.metadata.field import Field, FieldType

    # 创建销售表
    sales_table = Table(name="sales", description="销售表", primary_key="sales_id")

    sales_table.add_field(Field(name="sales_id", field_type=FieldType.INTEGER, required=True))
    sales_table.add_field(Field(
        name="amount",
        field_type=FieldType.AMOUNT,
        min_value=100,
        max_value=10000,
        precision=2
    ))

    # 添加分布规则：期望均值5000，标准差2000
    distribution_rule = DistributionRule(
        'amount',
        expected_mean=5000,
        expected_std=2000,
        tolerance=0.3  # 允许30%的偏差
    )
    sales_table.add_rule(distribution_rule)

    # 生成数据
    app = DataMakerApp(seed=42)
    app.add_table(sales_table)

    data, report = app.generate_data('sales', count=200, validate=True)

    print(f"\n✓ 生成了 {len(data)} 条销售数据")

    # 计算实际统计量
    import statistics
    amounts = [record['amount'] for record in data]
    actual_mean = statistics.mean(amounts)
    actual_std = statistics.stdev(amounts)

    print(f"\n统计信息:")
    print(f"  - 期望均值: 5000, 实际均值: {actual_mean:.2f}")
    print(f"  - 期望标准差: 2000, 实际标准差: {actual_std:.2f}")
    print(f"  - 最小值: {min(amounts):.2f}")
    print(f"  - 最大值: {max(amounts):.2f}")


def demo_correlation_rule():
    """演示关联性规则"""
    print("\n" + "=" * 70)
    print("示例7: 关联性规则 (CorrelationRule)")
    print("=" * 70)

    from src.metadata.table import Table
    from src.metadata.field import Field, FieldType

    # 创建员工表
    employee_table = Table(name="employee", description="员工表", primary_key="employee_id")

    employee_table.add_field(Field(name="employee_id", field_type=FieldType.INTEGER, required=True))
    employee_table.add_field(Field(
        name="years_of_experience",
        field_type=FieldType.INTEGER,
        min_value=0,
        max_value=40
    ))
    employee_table.add_field(Field(
        name="salary",
        field_type=FieldType.AMOUNT,
        min_value=30000,
        max_value=200000,
        precision=2
    ))

    # 添加关联性规则：工作年限和薪资应该正相关
    correlation_rule = CorrelationRule(
        'years_of_experience',
        'salary',
        correlation_type='positive'
    )
    employee_table.add_rule(correlation_rule)

    # 生成数据
    app = DataMakerApp(seed=42)
    app.add_table(employee_table)

    data, report = app.generate_data('employee', count=100, validate=True)

    print(f"\n✓ 生成了 {len(data)} 条员工数据")

    # 计算实际相关系数
    import statistics
    experience_values = [record['years_of_experience'] for record in data]
    salary_values = [record['salary'] for record in data]

    mean_exp = statistics.mean(experience_values)
    mean_sal = statistics.mean(salary_values)
    std_exp = statistics.stdev(experience_values)
    std_sal = statistics.stdev(salary_values)

    covariance = sum((e - mean_exp) * (s - mean_sal) for e, s in zip(experience_values, salary_values)) / len(data)
    correlation = covariance / (std_exp * std_sal)

    print(f"\n相关性分析:")
    print(f"  - 工作年限与薪资的相关系数: {correlation:.2f}")
    print(f"  - 期望: 正相关 (>0.5)")


def main():
    """运行所有演示"""
    print("\n" + "=" * 70)
    print("高级功能演示 - 增量数据生成和新增数据质量规则")
    print("=" * 70)

    try:
        # 1. 增量数据生成
        demo_incremental_generation()

        # 2. 新增的数据质量规则
        demo_temporal_rule()
        demo_length_rule()
        demo_format_rule()
        demo_enum_rule()
        demo_distribution_rule()
        demo_correlation_rule()

        print("\n" + "=" * 70)
        print("所有演示执行完成！")
        print("=" * 70)

        print("\n新功能总结:")
        print("1. ✓ 增量数据生成 - 在现有数据基础上智能追加新数据")
        print("2. ✓ 时序规则 - 验证日期/时间的先后顺序")
        print("3. ✓ 长度规则 - 验证字符串长度范围")
        print("4. ✓ 格式规则 - 验证特定格式（邮箱、电话等）")
        print("5. ✓ 枚举规则 - 验证值是否在允许列表中")
        print("6. ✓ 分布规则 - 验证数值分布的合理性")
        print("7. ✓ 关联性规则 - 验证字段间的相关性")

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
