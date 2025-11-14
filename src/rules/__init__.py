"""
数据质量规则模块
定义和执行数据质量规则
"""

from .rule import Rule, RuleType, RuleSeverity
from .rule_engine import RuleEngine
from .builtin_rules import (
    CompletenessRule,
    UniquenessRule,
    RangeRule,
    PatternRule,
    ConsistencyRule,
    ReferentialIntegrityRule,
)

__all__ = [
    'Rule', 'RuleType', 'RuleSeverity', 'RuleEngine',
    'CompletenessRule', 'UniquenessRule', 'RangeRule',
    'PatternRule', 'ConsistencyRule', 'ReferentialIntegrityRule',
]
