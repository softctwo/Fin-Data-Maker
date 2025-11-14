"""
规则引擎
执行数据质量规则并生成报告
"""

from typing import List, Dict, Any, Optional
from .rule import Rule, RuleViolation, RuleSeverity


class ValidationReport:
    """验证报告"""

    def __init__(self):
        self.violations: List[RuleViolation] = []
        self.total_rows: int = 0
        self.valid_rows: int = 0

    def add_violation(self, violation: RuleViolation):
        """添加违规记录"""
        self.violations.append(violation)

    def get_error_count(self) -> int:
        """获取错误数量"""
        return sum(1 for v in self.violations if v.severity == RuleSeverity.ERROR)

    def get_warning_count(self) -> int:
        """获取警告数量"""
        return sum(1 for v in self.violations if v.severity == RuleSeverity.WARNING)

    def get_info_count(self) -> int:
        """获取信息数量"""
        return sum(1 for v in self.violations if v.severity == RuleSeverity.INFO)

    def is_valid(self) -> bool:
        """数据是否有效（无错误）"""
        return self.get_error_count() == 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "error_count": self.get_error_count(),
            "warning_count": self.get_warning_count(),
            "info_count": self.get_info_count(),
            "violations": [v.to_dict() for v in self.violations],
        }

    def get_summary(self) -> str:
        """获取摘要信息"""
        return (
            f"总行数: {self.total_rows}\n"
            f"有效行数: {self.valid_rows}\n"
            f"错误: {self.get_error_count()}\n"
            f"警告: {self.get_warning_count()}\n"
            f"信息: {self.get_info_count()}"
        )


class RuleEngine:
    """
    规则引擎
    管理和执行数据质量规则
    """

    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule):
        """添加规则"""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """删除规则"""
        self.rules = [r for r in self.rules if r.name != rule_name]

    def clear_rules(self):
        """清空所有规则"""
        self.rules = []

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> ValidationReport:
        """
        验证数据

        Args:
            data: 要验证的数据列表
            **kwargs: 传递给规则的额外参数

        Returns:
            ValidationReport: 验证报告
        """
        report = ValidationReport()
        report.total_rows = len(data)

        # 执行所有规则
        for rule in self.rules:
            violations = rule.validate(data, **kwargs)
            for violation in violations:
                report.add_violation(violation)

        # 计算有效行数（没有错误的行）
        error_rows = set()
        for violation in report.violations:
            if violation.severity == RuleSeverity.ERROR and violation.row_index is not None:
                error_rows.add(violation.row_index)

        report.valid_rows = report.total_rows - len(error_rows)

        return report

    def validate_and_filter(
        self, data: List[Dict[str, Any]], **kwargs
    ) -> tuple[List[Dict[str, Any]], ValidationReport]:
        """
        验证数据并过滤掉有错误的行

        Args:
            data: 要验证的数据列表
            **kwargs: 传递给规则的额外参数

        Returns:
            tuple[List[Dict[str, Any]], ValidationReport]: (有效数据, 验证报告)
        """
        report = self.validate(data, **kwargs)

        # 收集有错误的行索引
        error_rows = set()
        for violation in report.violations:
            if violation.severity == RuleSeverity.ERROR and violation.row_index is not None:
                error_rows.add(violation.row_index)

        # 过滤数据
        valid_data = [row for idx, row in enumerate(data) if idx not in error_rows]

        return valid_data, report
