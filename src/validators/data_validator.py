"""
数据验证器
综合使用元数据和规则引擎进行数据验证
"""

from typing import List, Dict, Any
from ..metadata.table import Table
from ..rules.rule_engine import RuleEngine, ValidationReport
from ..rules.builtin_rules import (
    CompletenessRule,
    UniquenessRule,
    RangeRule,
    PatternRule,
)


class DataValidator:
    """
    数据验证器
    根据表定义和数据质量规则验证数据
    """

    def __init__(self, table: Table):
        """
        初始化验证器

        Args:
            table: 表定义
        """
        self.table = table
        self.rule_engine = RuleEngine()
        self._setup_default_rules()

    def _setup_default_rules(self):
        """设置默认规则（基于表定义）"""
        # 完整性规则：检查必填字段
        required_fields = [f.name for f in self.table.get_required_fields()]
        if required_fields:
            self.rule_engine.add_rule(CompletenessRule(required_fields))

        # 唯一性规则：检查唯一字段
        unique_fields = [f.name for f in self.table.get_unique_fields()]
        if unique_fields:
            self.rule_engine.add_rule(UniquenessRule(unique_fields))

        # 范围规则：检查数值范围
        for field in self.table.fields:
            if field.min_value is not None or field.max_value is not None:
                self.rule_engine.add_rule(
                    RangeRule(field.name, field.min_value, field.max_value)
                )

            # 模式规则：检查正则表达式
            if field.pattern:
                self.rule_engine.add_rule(PatternRule(field.name, field.pattern))

    def validate(self, data: List[Dict[str, Any]]) -> ValidationReport:
        """
        验证数据

        Args:
            data: 要验证的数据

        Returns:
            ValidationReport: 验证报告
        """
        # 首先使用表定义验证每行数据
        for idx, row in enumerate(data):
            errors = self.table.validate_row(row)
            # 这里可以将errors添加到报告中，但我们主要使用规则引擎

        # 使用规则引擎验证
        return self.rule_engine.validate(data)

    def validate_and_filter(
        self, data: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], ValidationReport]:
        """
        验证数据并过滤掉有错误的行

        Args:
            data: 要验证的数据

        Returns:
            tuple: (有效数据, 验证报告)
        """
        return self.rule_engine.validate_and_filter(data)
