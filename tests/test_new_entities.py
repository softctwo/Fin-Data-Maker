"""
单元测试：新增金融实体（债券、基金、衍生品）
测试实体定义和数据生成功能
"""

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.app import DataMakerApp
from src.financial.schemas import (
    create_bond_table,
    create_fund_table,
    create_derivative_table,
    create_customer_table,
)


class TestBondEntity(unittest.TestCase):
    """测试债券实体"""

    def setUp(self):
        """测试前准备"""
        self.app = DataMakerApp(seed=42)
        self.bond_table = create_bond_table()
        self.customer_table = create_customer_table()

    def test_bond_table_definition(self):
        """测试债券表定义"""
        self.assertEqual(self.bond_table.name, "bond")
        self.assertEqual(self.bond_table.description, "债券信息表")
        self.assertEqual(self.bond_table.primary_key, "bond_id")
        self.assertEqual(len(self.bond_table.fields), 15)

    def test_bond_required_fields(self):
        """测试债券必填字段"""
        required_fields = [f.name for f in self.bond_table.get_required_fields()]
        expected_fields = [
            'bond_id', 'issuer_id', 'bond_code', 'bond_name', 'bond_type',
            'face_value', 'coupon_rate', 'issue_price', 'issue_amount',
            'issue_date', 'maturity_date', 'payment_frequency',
            'credit_rating', 'status'
        ]
        for field in expected_fields:
            self.assertIn(field, required_fields)

    def test_bond_unique_fields(self):
        """测试债券唯一字段"""
        unique_fields = [f.name for f in self.bond_table.get_unique_fields()]
        self.assertIn('bond_id', unique_fields)
        self.assertIn('bond_code', unique_fields)

    def test_bond_types(self):
        """测试债券类型枚举"""
        bond_type_field = self.bond_table.get_field('bond_type')
        self.assertIsNotNone(bond_type_field)
        self.assertEqual(len(bond_type_field.enum_values), 8)
        self.assertIn('国债', bond_type_field.enum_values)
        self.assertIn('公司债', bond_type_field.enum_values)

    def test_bond_data_generation(self):
        """测试债券数据生成"""
        self.app.add_table(self.customer_table)
        self.app.add_table(self.bond_table)

        # 先生成客户数据
        customer_data, _ = self.app.generate_data("customer", count=5)
        self.assertEqual(len(customer_data), 5)

        # 生成债券数据
        customer_ids = [c['customer_id'] for c in customer_data]
        bond_data, report = self.app.generate_with_relations(
            "bond", count=10, related_data={"customer": customer_ids}
        )

        self.assertEqual(len(bond_data), 10)
        self.assertTrue(report.is_valid)

        # 验证字段存在
        for bond in bond_data:
            self.assertIn('bond_id', bond)
            self.assertIn('bond_code', bond)
            self.assertIn('bond_name', bond)
            self.assertIn('coupon_rate', bond)

    def test_bond_foreign_key(self):
        """测试债券外键关联"""
        issuer_field = self.bond_table.get_field('issuer_id')
        self.assertIsNotNone(issuer_field)
        self.assertEqual(issuer_field.reference_table, 'customer')
        self.assertEqual(issuer_field.reference_field, 'customer_id')


class TestFundEntity(unittest.TestCase):
    """测试基金实体"""

    def setUp(self):
        """测试前准备"""
        self.app = DataMakerApp(seed=42)
        self.fund_table = create_fund_table()
        self.customer_table = create_customer_table()

    def test_fund_table_definition(self):
        """测试基金表定义"""
        self.assertEqual(self.fund_table.name, "fund")
        self.assertEqual(self.fund_table.description, "基金信息表")
        self.assertEqual(self.fund_table.primary_key, "fund_id")
        self.assertEqual(len(self.fund_table.fields), 17)

    def test_fund_types(self):
        """测试基金类型枚举"""
        fund_type_field = self.fund_table.get_field('fund_type')
        self.assertIsNotNone(fund_type_field)
        self.assertEqual(len(fund_type_field.enum_values), 9)
        self.assertIn('股票型', fund_type_field.enum_values)
        self.assertIn('ETF', fund_type_field.enum_values)

    def test_fund_risk_levels(self):
        """测试基金风险等级"""
        risk_field = self.fund_table.get_field('risk_level')
        self.assertIsNotNone(risk_field)
        self.assertEqual(len(risk_field.enum_values), 5)
        self.assertIn('低风险', risk_field.enum_values)
        self.assertIn('高风险', risk_field.enum_values)

    def test_fund_data_generation(self):
        """测试基金数据生成"""
        self.app.add_table(self.customer_table)
        self.app.add_table(self.fund_table)

        # 先生成客户数据
        customer_data, _ = self.app.generate_data("customer", count=5)

        # 生成基金数据
        customer_ids = [c['customer_id'] for c in customer_data]
        fund_data, report = self.app.generate_with_relations(
            "fund", count=10, related_data={"customer": customer_ids}
        )

        self.assertEqual(len(fund_data), 10)
        self.assertTrue(report.is_valid)

        # 验证净值精度
        for fund in fund_data:
            self.assertIn('net_value', fund)
            # 净值应该是4位小数
            net_value_str = str(fund['net_value'])
            if '.' in net_value_str:
                decimal_places = len(net_value_str.split('.')[1])
                self.assertLessEqual(decimal_places, 4)

    def test_fund_foreign_key(self):
        """测试基金外键关联"""
        manager_field = self.fund_table.get_field('fund_manager_id')
        self.assertIsNotNone(manager_field)
        self.assertEqual(manager_field.reference_table, 'customer')
        self.assertEqual(manager_field.reference_field, 'customer_id')


class TestDerivativeEntity(unittest.TestCase):
    """测试衍生品实体"""

    def setUp(self):
        """测试前准备"""
        self.app = DataMakerApp(seed=42)
        self.derivative_table = create_derivative_table()

    def test_derivative_table_definition(self):
        """测试衍生品表定义"""
        self.assertEqual(self.derivative_table.name, "derivative")
        self.assertEqual(self.derivative_table.description, "金融衍生品信息表")
        self.assertEqual(self.derivative_table.primary_key, "derivative_id")
        self.assertEqual(len(self.derivative_table.fields), 18)

    def test_derivative_types(self):
        """测试衍生品类型"""
        type_field = self.derivative_table.get_field('derivative_type')
        self.assertIsNotNone(type_field)
        self.assertEqual(len(type_field.enum_values), 6)
        self.assertIn('期货', type_field.enum_values)
        self.assertIn('期权', type_field.enum_values)

    def test_underlying_asset_types(self):
        """测试标的资产类型"""
        asset_field = self.derivative_table.get_field('underlying_asset_type')
        self.assertIsNotNone(asset_field)
        self.assertEqual(len(asset_field.enum_values), 7)
        self.assertIn('股票', asset_field.enum_values)
        self.assertIn('商品', asset_field.enum_values)

    def test_derivative_optional_fields(self):
        """测试衍生品可选字段"""
        # strike_price是可选的（期权才有）
        strike_field = self.derivative_table.get_field('strike_price')
        self.assertFalse(strike_field.required)

        # option_type是可选的
        option_field = self.derivative_table.get_field('option_type')
        self.assertFalse(option_field.required)

    def test_derivative_data_generation(self):
        """测试衍生品数据生成"""
        self.app.add_table(self.derivative_table)

        derivative_data, report = self.app.generate_data("derivative", count=15)

        self.assertEqual(len(derivative_data), 15)
        self.assertTrue(report.is_valid)

        # 验证字段存在
        for deriv in derivative_data:
            self.assertIn('derivative_id', deriv)
            self.assertIn('contract_code', deriv)
            self.assertIn('derivative_type', deriv)
            self.assertIn('exchange', deriv)

    def test_exchange_enum(self):
        """测试交易所枚举"""
        exchange_field = self.derivative_table.get_field('exchange')
        self.assertIsNotNone(exchange_field)
        self.assertEqual(len(exchange_field.enum_values), 6)
        self.assertIn('上海期货交易所', exchange_field.enum_values)
        self.assertIn('中国金融期货交易所', exchange_field.enum_values)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试前准备"""
        self.app = DataMakerApp(seed=42)

    def test_all_entities_together(self):
        """测试所有新实体一起生成"""
        customer_table = create_customer_table()
        bond_table = create_bond_table()
        fund_table = create_fund_table()
        derivative_table = create_derivative_table()

        self.app.add_table(customer_table)
        self.app.add_table(bond_table)
        self.app.add_table(fund_table)
        self.app.add_table(derivative_table)

        # 生成客户
        customer_data, _ = self.app.generate_data("customer", count=10)
        self.assertEqual(len(customer_data), 10)

        customer_ids = [c['customer_id'] for c in customer_data]

        # 生成债券
        bond_data, bond_report = self.app.generate_with_relations(
            "bond", count=20, related_data={"customer": customer_ids}
        )
        self.assertEqual(len(bond_data), 20)
        self.assertTrue(bond_report.is_valid)

        # 生成基金
        fund_data, fund_report = self.app.generate_with_relations(
            "fund", count=15, related_data={"customer": customer_ids}
        )
        self.assertEqual(len(fund_data), 15)
        self.assertTrue(fund_report.is_valid)

        # 生成衍生品
        derivative_data, deriv_report = self.app.generate_data("derivative", count=30)
        self.assertEqual(len(derivative_data), 30)
        self.assertTrue(deriv_report.is_valid)

        # 验证总记录数
        total_records = (len(customer_data) + len(bond_data) +
                        len(fund_data) + len(derivative_data))
        self.assertEqual(total_records, 75)


class TestStringGenerationFix(unittest.TestCase):
    """测试字符串生成修复"""

    def test_short_string_generation(self):
        """测试短字符串生成（修复后）"""
        from src.generators.field_generator import FieldGenerator
        from src.metadata.field import Field, FieldType

        generator = FieldGenerator(seed=42)

        # 测试长度为1的字符串
        field1 = Field(name="test1", field_type=FieldType.STRING, length=1)
        value1 = generator.generate(field1)
        self.assertIsNotNone(value1)
        self.assertEqual(len(value1), 1)

        # 测试长度为3的字符串
        field3 = Field(name="test3", field_type=FieldType.STRING, length=3)
        value3 = generator.generate(field3)
        self.assertIsNotNone(value3)
        self.assertEqual(len(value3), 3)

        # 测试长度为5的字符串（应该使用faker.text）
        field5 = Field(name="test5", field_type=FieldType.STRING, length=5)
        value5 = generator.generate(field5)
        self.assertIsNotNone(value5)
        self.assertLessEqual(len(value5), 5)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestBondEntity))
    suite.addTests(loader.loadTestsFromTestCase(TestFundEntity))
    suite.addTests(loader.loadTestsFromTestCase(TestDerivativeEntity))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStringGenerationFix))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
