"""
内置数据质量规则实现
"""

import re
from typing import Any, Dict, List, Optional, Set
from .rule import Rule, RuleType, RuleSeverity, RuleViolation


class CompletenessRule(Rule):
    """完整性规则：检查必填字段是否为空"""

    def __init__(self, fields: List[str], severity: RuleSeverity = RuleSeverity.ERROR):
        super().__init__(
            name=f"completeness_{','.join(fields)}",
            rule_type=RuleType.COMPLETENESS,
            severity=severity,
            description=f"检查字段 {','.join(fields)} 的完整性",
        )
        self.fields = fields

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            for field in self.fields:
                value = row.get(field)
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"字段 {field} 不能为空",
                            field=field,
                            value=value,
                            row_index=idx,
                        )
                    )

        return violations


class UniquenessRule(Rule):
    """唯一性规则：检查字段值是否唯一"""

    def __init__(self, fields: List[str], severity: RuleSeverity = RuleSeverity.ERROR):
        super().__init__(
            name=f"uniqueness_{','.join(fields)}",
            rule_type=RuleType.UNIQUENESS,
            severity=severity,
            description=f"检查字段 {','.join(fields)} 的唯一性",
        )
        self.fields = fields

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for field in self.fields:
            seen: Dict[Any, int] = {}
            for idx, row in enumerate(data):
                value = row.get(field)
                if value is not None:
                    if value in seen:
                        violations.append(
                            RuleViolation(
                                rule_name=self.name,
                                rule_type=self.rule_type,
                                severity=self.severity,
                                message=f"字段 {field} 的值 {value} 重复（首次出现在第 {seen[value]} 行）",
                                field=field,
                                value=value,
                                row_index=idx,
                            )
                        )
                    else:
                        seen[value] = idx

        return violations


class RangeRule(Rule):
    """范围规则：检查数值是否在指定范围内"""

    def __init__(
        self,
        field: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"range_{field}",
            rule_type=RuleType.VALIDITY,
            severity=severity,
            description=f"检查字段 {field} 是否在范围 [{min_value}, {max_value}] 内",
        )
        self.field = field
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            value = row.get(self.field)
            if value is not None:
                try:
                    num_value = float(value)
                    if self.min_value is not None and num_value < self.min_value:
                        violations.append(
                            RuleViolation(
                                rule_name=self.name,
                                rule_type=self.rule_type,
                                severity=self.severity,
                                message=f"字段 {self.field} 的值 {value} 小于最小值 {self.min_value}",
                                field=self.field,
                                value=value,
                                row_index=idx,
                            )
                        )
                    if self.max_value is not None and num_value > self.max_value:
                        violations.append(
                            RuleViolation(
                                rule_name=self.name,
                                rule_type=self.rule_type,
                                severity=self.severity,
                                message=f"字段 {self.field} 的值 {value} 大于最大值 {self.max_value}",
                                field=self.field,
                                value=value,
                                row_index=idx,
                            )
                        )
                except (ValueError, TypeError):
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"字段 {self.field} 的值 {value} 不是有效的数值",
                            field=self.field,
                            value=value,
                            row_index=idx,
                        )
                    )

        return violations


class PatternRule(Rule):
    """模式规则：检查字段值是否匹配指定的正则表达式"""

    def __init__(
        self,
        field: str,
        pattern: str,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"pattern_{field}",
            rule_type=RuleType.VALIDITY,
            severity=severity,
            description=f"检查字段 {field} 是否匹配模式 {pattern}",
        )
        self.field = field
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern)

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            value = row.get(self.field)
            if value is not None:
                str_value = str(value)
                if not self.compiled_pattern.match(str_value):
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"字段 {self.field} 的值 {value} 不匹配模式 {self.pattern}",
                            field=self.field,
                            value=value,
                            row_index=idx,
                        )
                    )

        return violations


class ConsistencyRule(Rule):
    """一致性规则：检查多个字段之间的一致性"""

    def __init__(
        self,
        name: str,
        description: str,
        condition: callable,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=name,
            rule_type=RuleType.CONSISTENCY,
            severity=severity,
            description=description,
        )
        self.condition = condition

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            try:
                if not self.condition(row):
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"行 {idx} 的数据不满足一致性条件: {self.description}",
                            row_index=idx,
                        )
                    )
            except Exception as e:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"行 {idx} 执行一致性检查时出错: {str(e)}",
                        row_index=idx,
                    )
                )

        return violations


class ReferentialIntegrityRule(Rule):
    """引用完整性规则：检查外键引用是否有效"""

    def __init__(
        self,
        field: str,
        reference_data: List[Any],
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"referential_integrity_{field}",
            rule_type=RuleType.REFERENTIAL_INTEGRITY,
            severity=severity,
            description=f"检查字段 {field} 的引用完整性",
        )
        self.field = field
        self.reference_set = set(reference_data)

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            value = row.get(self.field)
            if value is not None and value not in self.reference_set:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field} 的值 {value} 在引用数据中不存在",
                        field=self.field,
                        value=value,
                        row_index=idx,
                    )
                )

        return violations
