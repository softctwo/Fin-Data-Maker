"""
表数据生成器
生成整张表的数据
"""

from typing import List, Dict, Any, Optional
from ..metadata.table import Table
from ..metadata.field import Field
from .field_generator import FieldGenerator
from .base_generator import BaseGenerator


class TableGenerator(BaseGenerator):
    """
    表数据生成器
    根据表定义生成符合要求的数据
    """

    def __init__(
        self,
        table: Table,
        seed: Optional[int] = None,
        locale: str = 'zh_CN'
    ):
        """
        初始化表生成器

        Args:
            table: 表定义
            seed: 随机种子
            locale: 语言区域设置
        """
        super().__init__(seed)
        self.table = table
        self.field_generator = FieldGenerator(seed, locale)

    def generate(self, **kwargs) -> Dict[str, Any]:
        """
        生成一行数据

        Args:
            **kwargs: 预设字段值

        Returns:
            Dict[str, Any]: 生成的行数据
        """
        row = {}

        for field in self.table.fields:
            # 如果kwargs中指定了该字段的值，使用指定值
            if field.name in kwargs:
                row[field.name] = kwargs[field.name]
            else:
                # 否则生成数据
                row[field.name] = self.field_generator.generate(field)

        return row

    def generate_batch(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        批量生成数据

        Args:
            count: 生成行数
            **kwargs: 预设字段值（应用到所有行）

        Returns:
            List[Dict[str, Any]]: 生成的数据列表
        """
        # 重置唯一值跟踪器
        self.field_generator.reset_unique_tracker()

        data = []
        for i in range(count):
            # 支持动态kwargs（可以是函数）
            row_kwargs = {}
            for key, value in kwargs.items():
                if callable(value):
                    row_kwargs[key] = value(i)
                else:
                    row_kwargs[key] = value

            row = self.generate(**row_kwargs)
            data.append(row)

        return data

    def generate_with_relations(
        self,
        count: int,
        related_data: Optional[Dict[str, List[Any]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        生成带关联关系的数据

        Args:
            count: 生成行数
            related_data: 关联表数据，格式为 {table_name: [values]}
            **kwargs: 预设字段值

        Returns:
            List[Dict[str, Any]]: 生成的数据列表
        """
        related_data = related_data or {}
        data = []

        # 重置唯一值跟踪器
        self.field_generator.reset_unique_tracker()

        for i in range(count):
            row = {}

            for field in self.table.fields:
                # 如果字段有外键引用
                if field.reference_table and field.reference_table in related_data:
                    # 从关联数据中随机选择
                    import random
                    ref_values = related_data[field.reference_table]
                    if ref_values:
                        row[field.name] = random.choice(ref_values)
                    else:
                        row[field.name] = self.field_generator.generate(field)
                # 如果kwargs中指定了该字段的值
                elif field.name in kwargs:
                    value = kwargs[field.name]
                    row[field.name] = value(i) if callable(value) else value
                else:
                    # 否则生成数据
                    row[field.name] = self.field_generator.generate(field)

            data.append(row)

        return data
