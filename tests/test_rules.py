"""
测试数据质量规则模块
"""

import unittest
from src.rules.builtin_rules import (
    CompletenessRule,
    UniquenessRule,
    RangeRule,
    PatternRule,
)
from src.rules.rule import RuleSeverity


class TestRules(unittest.TestCase):
    """测试数据质量规则"""

    def test_completeness_rule(self):
        """测试完整性规则"""
        rule = CompletenessRule(fields=["name", "email"])

        # 没有违规
        data = [
            {"name": "张三", "email": "zhang@example.com"},
            {"name": "李四", "email": "li@example.com"},
        ]
        violations = rule.validate(data)
        self.assertEqual(len(violations), 0)

        # 有违规
        data_with_nulls = [
            {"name": "张三", "email": None},
            {"name": None, "email": "li@example.com"},
        ]
        violations = rule.validate(data_with_nulls)
        self.assertEqual(len(violations), 2)

    def test_uniqueness_rule(self):
        """测试唯一性规则"""
        rule = UniquenessRule(fields=["id"])

        # 没有违规
        data = [
            {"id": "001", "name": "张三"},
            {"id": "002", "name": "李四"},
            {"id": "003", "name": "王五"},
        ]
        violations = rule.validate(data)
        self.assertEqual(len(violations), 0)

        # 有违规
        data_with_duplicates = [
            {"id": "001", "name": "张三"},
            {"id": "002", "name": "李四"},
            {"id": "001", "name": "王五"},  # 重复
        ]
        violations = rule.validate(data_with_duplicates)
        self.assertEqual(len(violations), 1)

    def test_range_rule(self):
        """测试范围规则"""
        rule = RangeRule(field="age", min_value=0, max_value=150)

        # 没有违规
        data = [
            {"age": 25},
            {"age": 50},
            {"age": 100},
        ]
        violations = rule.validate(data)
        self.assertEqual(len(violations), 0)

        # 有违规
        data_out_of_range = [
            {"age": -1},   # 小于最小值
            {"age": 200},  # 大于最大值
        ]
        violations = rule.validate(data_out_of_range)
        self.assertEqual(len(violations), 2)

    def test_pattern_rule(self):
        """测试模式规则"""
        # 测试手机号格式
        rule = PatternRule(field="phone", pattern=r"^1[3-9]\d{9}$")

        # 没有违规
        data = [
            {"phone": "13812345678"},
            {"phone": "18900001111"},
        ]
        violations = rule.validate(data)
        self.assertEqual(len(violations), 0)

        # 有违规
        data_invalid = [
            {"phone": "12345678901"},  # 不是1开头
            {"phone": "138123456"},    # 长度不对
        ]
        violations = rule.validate(data_invalid)
        self.assertEqual(len(violations), 2)


if __name__ == "__main__":
    unittest.main()
