"""
数据质量分析器
分析现有数据的质量特征，为生成测试数据提供参考
"""

from typing import List, Dict, Any, Optional
import logging
from collections import Counter
import re

from .db_connector import DatabaseConnector
from ..metadata.table import Table
from ..metadata.field import Field

logger = logging.getLogger(__name__)


class DataProfile:
    """数据概要类"""

    def __init__(self, field_name: str):
        self.field_name = field_name
        self.total_count = 0
        self.null_count = 0
        self.unique_count = 0
        self.min_value = None
        self.max_value = None
        self.avg_value = None
        self.min_length = None
        self.max_length = None
        self.avg_length = None
        self.most_common_values = []
        self.pattern_samples = []
        self.completeness_rate = 0.0
        self.uniqueness_rate = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'field_name': self.field_name,
            'total_count': self.total_count,
            'null_count': self.null_count,
            'unique_count': self.unique_count,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'avg_value': self.avg_value,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'avg_length': self.avg_length,
            'completeness_rate': self.completeness_rate,
            'uniqueness_rate': self.uniqueness_rate,
            'most_common_values': self.most_common_values,
            'pattern_samples': self.pattern_samples,
        }


class DataProfiler:
    """
    数据质量分析器
    分析现有数据的质量特征
    """

    def __init__(self, connector: DatabaseConnector):
        """
        初始化数据分析器

        Args:
            connector: 数据库连接器
        """
        self.connector = connector

    def profile_table(
        self,
        table: Table,
        sample_size: int = 1000,
        schema: Optional[str] = None
    ) -> Dict[str, DataProfile]:
        """
        分析表的数据质量

        Args:
            table: 表定义
            sample_size: 采样数量
            schema: 模式名（可选）

        Returns:
            Dict[str, DataProfile]: 字段名到数据概要的映射
        """
        logger.info(f"开始分析表: {table.name}")

        profiles = {}

        # 采样数据
        sample_data = self.connector.sample_table_data(
            table.name,
            limit=sample_size,
            schema=schema
        )

        if not sample_data:
            logger.warning(f"表 {table.name} 没有数据")
            return profiles

        # 获取实际行数
        total_rows = self.connector.get_table_row_count(table.name, schema)

        # 分析每个字段
        for field in table.fields:
            profile = self._profile_field(field, sample_data, total_rows)
            profiles[field.name] = profile

        logger.info(f"完成表分析: {table.name}")
        return profiles

    def _profile_field(
        self,
        field: Field,
        sample_data: List[Dict[str, Any]],
        total_rows: int
    ) -> DataProfile:
        """
        分析字段的数据质量

        Args:
            field: 字段定义
            sample_data: 采样数据
            total_rows: 总行数

        Returns:
            DataProfile: 数据概要
        """
        profile = DataProfile(field.name)
        profile.total_count = len(sample_data)

        # 提取字段值
        values = [row.get(field.name) for row in sample_data]

        # 空值统计
        null_values = [v for v in values if v is None or v == '']
        profile.null_count = len(null_values)
        profile.completeness_rate = (profile.total_count - profile.null_count) / profile.total_count if profile.total_count > 0 else 0

        # 非空值
        non_null_values = [v for v in values if v is not None and v != '']

        if not non_null_values:
            return profile

        # 唯一值统计
        unique_values = set(non_null_values)
        profile.unique_count = len(unique_values)
        profile.uniqueness_rate = profile.unique_count / len(non_null_values) if non_null_values else 0

        # 最常见的值
        value_counts = Counter(non_null_values)
        profile.most_common_values = [
            {'value': str(v), 'count': c}
            for v, c in value_counts.most_common(10)
        ]

        # 数值型字段分析
        if self._is_numeric_field(field):
            try:
                numeric_values = [float(v) for v in non_null_values if v is not None]
                if numeric_values:
                    profile.min_value = min(numeric_values)
                    profile.max_value = max(numeric_values)
                    profile.avg_value = sum(numeric_values) / len(numeric_values)
            except (ValueError, TypeError):
                pass

        # 字符串型字段分析
        if self._is_string_field(field):
            str_values = [str(v) for v in non_null_values]
            if str_values:
                lengths = [len(s) for s in str_values]
                profile.min_length = min(lengths)
                profile.max_length = max(lengths)
                profile.avg_length = sum(lengths) / len(lengths)

                # 模式样本（前5个）
                profile.pattern_samples = str_values[:5]

        return profile

    def _is_numeric_field(self, field: Field) -> bool:
        """判断是否为数值型字段"""
        from ..metadata.field import FieldType
        return field.field_type in [
            FieldType.INTEGER,
            FieldType.DECIMAL,
            FieldType.AMOUNT,
        ]

    def _is_string_field(self, field: Field) -> bool:
        """判断是否为字符串型字段"""
        from ..metadata.field import FieldType
        return field.field_type in [
            FieldType.STRING,
            FieldType.ID,
            FieldType.PHONE,
            FieldType.EMAIL,
            FieldType.ID_CARD,
            FieldType.BANK_CARD,
        ]

    def generate_quality_rules(
        self,
        table: Table,
        profiles: Dict[str, DataProfile],
        strictness: str = 'medium'
    ) -> List[str]:
        """
        根据数据概要生成数据质量规则建议

        Args:
            table: 表定义
            profiles: 字段数据概要
            strictness: 严格程度（loose/medium/strict）

        Returns:
            List[str]: 质量规则建议
        """
        rules = []

        # 严格程度阈值
        thresholds = {
            'loose': {'completeness': 0.7, 'uniqueness': 0.7},
            'medium': {'completeness': 0.9, 'uniqueness': 0.9},
            'strict': {'completeness': 0.95, 'uniqueness': 0.95},
        }

        threshold = thresholds.get(strictness, thresholds['medium'])

        for field_name, profile in profiles.items():
            field = table.get_field(field_name)
            if not field:
                continue

            # 完整性规则
            if profile.completeness_rate >= threshold['completeness']:
                rules.append(
                    f"字段 {field_name} 应保持 {profile.completeness_rate:.1%} 的完整性"
                )

            # 唯一性规则
            if profile.uniqueness_rate >= threshold['uniqueness']:
                rules.append(
                    f"字段 {field_name} 应保持 {profile.uniqueness_rate:.1%} 的唯一性"
                )

            # 范围规则
            if self._is_numeric_field(field):
                if profile.min_value is not None and profile.max_value is not None:
                    rules.append(
                        f"字段 {field_name} 数值范围应在 [{profile.min_value}, {profile.max_value}]"
                    )

            # 长度规则
            if self._is_string_field(field):
                if profile.min_length is not None and profile.max_length is not None:
                    rules.append(
                        f"字段 {field_name} 长度范围应在 [{profile.min_length}, {profile.max_length}]"
                    )

        return rules

    def update_table_metadata(
        self,
        table: Table,
        profiles: Dict[str, DataProfile]
    ) -> Table:
        """
        根据数据概要更新表的元数据定义

        Args:
            table: 表定义
            profiles: 字段数据概要

        Returns:
            Table: 更新后的表定义
        """
        for field_name, profile in profiles.items():
            field = table.get_field(field_name)
            if not field:
                continue

            # 更新必填属性
            if profile.completeness_rate >= 0.95:
                field.required = True

            # 更新唯一属性
            if profile.uniqueness_rate >= 0.95:
                field.unique = True

            # 更新数值范围
            if self._is_numeric_field(field):
                if profile.min_value is not None:
                    field.min_value = profile.min_value
                if profile.max_value is not None:
                    field.max_value = profile.max_value

            # 更新字符串长度
            if self._is_string_field(field):
                if profile.max_length is not None:
                    field.max_length = int(profile.max_length)
                if profile.min_length is not None:
                    field.min_length = int(profile.min_length)

        return table

    def generate_profile_report(
        self,
        table_name: str,
        profiles: Dict[str, DataProfile]
    ) -> str:
        """
        生成数据质量分析报告

        Args:
            table_name: 表名
            profiles: 字段数据概要

        Returns:
            str: 报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"数据质量分析报告: {table_name}")
        lines.append("=" * 80)
        lines.append("")

        for field_name, profile in profiles.items():
            lines.append(f"字段: {field_name}")
            lines.append(f"  总数: {profile.total_count}")
            lines.append(f"  空值数: {profile.null_count}")
            lines.append(f"  唯一值数: {profile.unique_count}")
            lines.append(f"  完整性: {profile.completeness_rate:.2%}")
            lines.append(f"  唯一性: {profile.uniqueness_rate:.2%}")

            if profile.min_value is not None:
                lines.append(f"  最小值: {profile.min_value}")
                lines.append(f"  最大值: {profile.max_value}")
                lines.append(f"  平均值: {profile.avg_value:.2f}")

            if profile.min_length is not None:
                lines.append(f"  最小长度: {profile.min_length}")
                lines.append(f"  最大长度: {profile.max_length}")
                lines.append(f"  平均长度: {profile.avg_length:.1f}")

            if profile.most_common_values:
                lines.append("  最常见的值:")
                for item in profile.most_common_values[:5]:
                    lines.append(f"    {item['value']}: {item['count']} 次")

            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)
