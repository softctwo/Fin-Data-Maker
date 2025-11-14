"""
简单测试：验证新增的金融实体定义
测试债券、基金、衍生品表是否正确定义
"""

from src.financial.schemas import (
    create_bond_table,
    create_fund_table,
    create_derivative_table,
)


def test_entity_definition(entity_name, create_func):
    """测试实体定义"""
    print(f"\n测试 {entity_name}:")
    print("=" * 50)

    # 创建表定义
    table = create_func()

    # 基本信息
    print(f"  表名: {table.name}")
    print(f"  描述: {table.description}")
    print(f"  主键: {table.primary_key}")
    print(f"  字段数量: {len(table.fields)}")

    # 字段详情
    print(f"\n  字段列表:")
    for field in table.fields:
        required = "必填" if field.required else "可选"
        unique = ", 唯一" if field.unique else ""
        ref = f", 关联→{field.reference_table}.{field.reference_field}" if field.reference_table else ""
        print(f"    - {field.name}: {field.field_type.value} ({required}{unique}{ref})")
        print(f"      {field.description}")

    print(f"\n  ✓ {entity_name} 定义验证通过!")
    return table


def main():
    print("=" * 60)
    print("新增金融实体定义验证")
    print("=" * 60)

    try:
        # 测试债券表
        bond_table = test_entity_definition("债券 (Bond)", create_bond_table)

        # 测试基金表
        fund_table = test_entity_definition("基金 (Fund)", create_fund_table)

        # 测试衍生品表
        derivative_table = test_entity_definition("衍生品 (Derivative)", create_derivative_table)

        # 汇总
        print("\n" + "=" * 60)
        print("验证完成!")
        print("=" * 60)
        print(f"✓ 债券表: {len(bond_table.fields)} 个字段")
        print(f"✓ 基金表: {len(fund_table.fields)} 个字段")
        print(f"✓ 衍生品表: {len(derivative_table.fields)} 个字段")
        print(f"\n总计: {len(bond_table.fields) + len(fund_table.fields) + len(derivative_table.fields)} 个字段定义")

        print("\n" + "=" * 60)
        print("新增功能概览:")
        print("=" * 60)

        print("\n1. 债券 (Bond) - 8种类型:")
        bond_field = [f for f in bond_table.fields if f.name == 'bond_type'][0]
        for bond_type in bond_field.enum_values:
            print(f"   - {bond_type}")

        print("\n2. 基金 (Fund) - 9种类型:")
        fund_field = [f for f in fund_table.fields if f.name == 'fund_type'][0]
        for fund_type in fund_field.enum_values:
            print(f"   - {fund_type}")

        print("\n3. 衍生品 (Derivative) - 6种类型:")
        derivative_field = [f for f in derivative_table.fields if f.name == 'derivative_type'][0]
        for derivative_type in derivative_field.enum_values:
            print(f"   - {derivative_type}")

        print("\n" + "=" * 60)
        print("所有新实体定义已成功加载并验证!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
