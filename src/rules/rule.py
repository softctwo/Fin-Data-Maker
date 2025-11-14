"""
数据质量规则定义
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class RuleType(Enum):
    """规则类型"""
    COMPLETENESS = "completeness"  # 完整性
    UNIQUENESS = "uniqueness"  # 唯一性
    ACCURACY = "accuracy"  # 准确性
    CONSISTENCY = "consistency"  # 一致性
    VALIDITY = "validity"  # 有效性
    TIMELINESS = "timeliness"  # 及时性
    REFERENTIAL_INTEGRITY = "referential_integrity"  # 引用完整性


class RuleSeverity(Enum):
    """规则严重程度"""
    ERROR = "error"  # 错误，不允许
    WARNING = "warning"  # 警告，允许但需注意
    INFO = "info"  # 信息，仅记录


class RuleViolation:
    """规则违反记录"""

    def __init__(
        self,
        rule_name: str,
        rule_type: RuleType,
        severity: RuleSeverity,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        row_index: Optional[int] = None,
    ):
        self.rule_name = rule_name
        self.rule_type = rule_type
        self.severity = severity
        self.message = message
        self.field = field
        self.value = value
        self.row_index = row_index

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_name": self.rule_name,
            "rule_type": self.rule_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "field": self.field,
            "value": self.value,
            "row_index": self.row_index,
        }


class Rule(ABC):
    """
    数据质量规则基类
    所有规则都需要继承此类并实现validate方法
    """

    def __init__(
        self,
        name: str,
        rule_type: RuleType,
        severity: RuleSeverity = RuleSeverity.ERROR,
        description: str = "",
    ):
        self.name = name
        self.rule_type = rule_type
        self.severity = severity
        self.description = description

    @abstractmethod
    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        """
        验证数据是否符合规则

        Args:
            data: 要验证的数据列表
            **kwargs: 额外参数

        Returns:
            List[RuleViolation]: 违反规则的记录列表
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": self.rule_type.value,
            "severity": self.severity.value,
            "description": self.description,
        }
