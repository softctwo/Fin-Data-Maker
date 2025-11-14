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


class TemporalRule(Rule):
    """时序规则：检查日期/时间字段的顺序关系"""

    def __init__(
        self,
        start_field: str,
        end_field: str,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"temporal_{start_field}_{end_field}",
            rule_type=RuleType.CONSISTENCY,
            severity=severity,
            description=f"检查 {start_field} 必须早于或等于 {end_field}",
        )
        self.start_field = start_field
        self.end_field = end_field

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            start_value = row.get(self.start_field)
            end_value = row.get(self.end_field)

            if start_value is not None and end_value is not None:
                # 尝试比较（假设是可比较的类型）
                try:
                    if start_value > end_value:
                        violations.append(
                            RuleViolation(
                                rule_name=self.name,
                                rule_type=self.rule_type,
                                severity=self.severity,
                                message=f"{self.start_field} ({start_value}) 晚于 {self.end_field} ({end_value})",
                                field=f"{self.start_field},{self.end_field}",
                                value=f"{start_value},{end_value}",
                                row_index=idx,
                            )
                        )
                except TypeError:
                    # 类型不可比较，跳过
                    pass

        return violations


class LengthRule(Rule):
    """长度规则：检查字符串字段的长度"""

    def __init__(
        self,
        field: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"length_{field}",
            rule_type=RuleType.RANGE,
            severity=severity,
            description=f"检查字段 {field} 的长度范围",
        )
        self.field = field
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            value = row.get(self.field)

            if value is not None:
                value_str = str(value)
                length = len(value_str)

                if self.min_length is not None and length < self.min_length:
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"字段 {self.field} 长度 {length} 小于最小值 {self.min_length}",
                            field=self.field,
                            value=value,
                            row_index=idx,
                        )
                    )

                if self.max_length is not None and length > self.max_length:
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"字段 {self.field} 长度 {length} 超过最大值 {self.max_length}",
                            field=self.field,
                            value=value,
                            row_index=idx,
                        )
                    )

        return violations


class FormatRule(Rule):
    """格式规则：检查字段值是否符合特定格式"""

    # 预定义的格式模式
    FORMATS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^1[3-9]\d{9}$',  # 中国手机号
        'id_card': r'^\d{17}[\dXx]$',  # 中国身份证号
        'ip': r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$',
        'url': r'^https?://[^\s]+$',
        'date': r'^\d{4}-\d{2}-\d{2}$',
        'time': r'^\d{2}:\d{2}:\d{2}$',
        'datetime': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
    }

    def __init__(
        self,
        field: str,
        format_name: str,
        custom_pattern: Optional[str] = None,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"format_{field}_{format_name}",
            rule_type=RuleType.PATTERN,
            severity=severity,
            description=f"检查字段 {field} 是否符合 {format_name} 格式",
        )
        self.field = field
        self.format_name = format_name

        # 使用自定义模式或预定义模式
        if custom_pattern:
            self.pattern = custom_pattern
        elif format_name in self.FORMATS:
            self.pattern = self.FORMATS[format_name]
        else:
            raise ValueError(f"未知的格式: {format_name}")

        self.regex = re.compile(self.pattern)

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            value = row.get(self.field)

            if value is not None:
                value_str = str(value)

                if not self.regex.match(value_str):
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            rule_type=self.rule_type,
                            severity=self.severity,
                            message=f"字段 {self.field} 的值 {value_str} 不符合 {self.format_name} 格式",
                            field=self.field,
                            value=value,
                            row_index=idx,
                        )
                    )

        return violations


class EnumRule(Rule):
    """枚举规则：检查字段值是否在允许的枚举列表中"""

    def __init__(
        self,
        field: str,
        allowed_values: List[Any],
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(
            name=f"enum_{field}",
            rule_type=RuleType.RANGE,
            severity=severity,
            description=f"检查字段 {field} 的值是否在允许的枚举列表中",
        )
        self.field = field
        self.allowed_values = set(allowed_values)

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        for idx, row in enumerate(data):
            value = row.get(self.field)

            if value is not None and value not in self.allowed_values:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field} 的值 {value} 不在允许的枚举列表中",
                        field=self.field,
                        value=value,
                        row_index=idx,
                    )
                )

        return violations


class DistributionRule(Rule):
    """分布规则：检查数值字段的分布是否合理"""

    def __init__(
        self,
        field: str,
        expected_mean: Optional[float] = None,
        expected_std: Optional[float] = None,
        tolerance: float = 0.3,  # 允许的偏差比例
        severity: RuleSeverity = RuleSeverity.WARNING,
    ):
        super().__init__(
            name=f"distribution_{field}",
            rule_type=RuleType.CONSISTENCY,
            severity=severity,
            description=f"检查字段 {field} 的数值分布",
        )
        self.field = field
        self.expected_mean = expected_mean
        self.expected_std = expected_std
        self.tolerance = tolerance

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        # 收集数值
        values = []
        for row in data:
            value = row.get(self.field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    pass

        if not values:
            return violations

        # 计算统计量
        import statistics

        actual_mean = statistics.mean(values)
        actual_std = statistics.stdev(values) if len(values) > 1 else 0

        # 检查均值
        if self.expected_mean is not None:
            diff_ratio = abs(actual_mean - self.expected_mean) / abs(self.expected_mean) if self.expected_mean != 0 else 0

            if diff_ratio > self.tolerance:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field} 的均值 {actual_mean:.2f} 与期望值 {self.expected_mean:.2f} 偏差过大 ({diff_ratio*100:.1f}%)",
                        field=self.field,
                        value=f"mean={actual_mean:.2f}",
                        row_index=-1,  # 整体检查
                    )
                )

        # 检查标准差
        if self.expected_std is not None:
            diff_ratio = abs(actual_std - self.expected_std) / abs(self.expected_std) if self.expected_std != 0 else 0

            if diff_ratio > self.tolerance:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field} 的标准差 {actual_std:.2f} 与期望值 {self.expected_std:.2f} 偏差过大 ({diff_ratio*100:.1f}%)",
                        field=self.field,
                        value=f"std={actual_std:.2f}",
                        row_index=-1,  # 整体检查
                    )
                )

        return violations


class CorrelationRule(Rule):
    """关联性规则：检查两个字段间的关联关系"""

    def __init__(
        self,
        field1: str,
        field2: str,
        correlation_type: str = 'positive',  # 'positive', 'negative', 'none'
        severity: RuleSeverity = RuleSeverity.WARNING,
    ):
        super().__init__(
            name=f"correlation_{field1}_{field2}",
            rule_type=RuleType.CONSISTENCY,
            severity=severity,
            description=f"检查字段 {field1} 和 {field2} 的关联性",
        )
        self.field1 = field1
        self.field2 = field2
        self.correlation_type = correlation_type

    def validate(self, data: List[Dict[str, Any]], **kwargs) -> List[RuleViolation]:
        violations = []

        # 收集数值对
        pairs = []
        for row in data:
            val1 = row.get(self.field1)
            val2 = row.get(self.field2)

            if val1 is not None and val2 is not None:
                try:
                    pairs.append((float(val1), float(val2)))
                except (ValueError, TypeError):
                    pass

        if len(pairs) < 2:
            return violations

        # 计算相关系数
        try:
            import statistics

            values1 = [p[0] for p in pairs]
            values2 = [p[1] for p in pairs]

            mean1 = statistics.mean(values1)
            mean2 = statistics.mean(values2)

            std1 = statistics.stdev(values1)
            std2 = statistics.stdev(values2)

            if std1 == 0 or std2 == 0:
                return violations

            # 计算皮尔逊相关系数
            covariance = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in pairs) / len(pairs)
            correlation = covariance / (std1 * std2)

            # 检查相关性
            if self.correlation_type == 'positive' and correlation < 0.5:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field1} 和 {self.field2} 的正相关性不足 (相关系数={correlation:.2f})",
                        field=f"{self.field1},{self.field2}",
                        value=f"correlation={correlation:.2f}",
                        row_index=-1,
                    )
                )

            elif self.correlation_type == 'negative' and correlation > -0.5:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field1} 和 {self.field2} 的负相关性不足 (相关系数={correlation:.2f})",
                        field=f"{self.field1},{self.field2}",
                        value=f"correlation={correlation:.2f}",
                        row_index=-1,
                    )
                )

            elif self.correlation_type == 'none' and abs(correlation) > 0.3:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        rule_type=self.rule_type,
                        severity=self.severity,
                        message=f"字段 {self.field1} 和 {self.field2} 存在非预期的相关性 (相关系数={correlation:.2f})",
                        field=f"{self.field1},{self.field2}",
                        value=f"correlation={correlation:.2f}",
                        row_index=-1,
                    )
                )

        except Exception:
            # 计算失败，跳过
            pass

        return violations
