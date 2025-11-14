"""
增量数据生成器 - 在现有数据基础上追加新数据
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
from src.metadata.table import Table
from src.metadata.field import Field, FieldType
from src.generators.table_generator import TableGenerator


class IncrementalGenerator:
    """增量数据生成器"""

    def __init__(self, table: Table, existing_data: List[Dict[str, Any]], seed: Optional[int] = None):
        """
        初始化增量生成器

        Args:
            table: 表定义
            existing_data: 现有数据列表
            seed: 随机种子
        """
        self.table = table
        self.existing_data = existing_data
        self.seed = seed

        if seed is not None:
            random.seed(seed)

        # 分析现有数据
        self.data_analysis = self._analyze_existing_data()

        # 创建基础生成器
        self.base_generator = TableGenerator(table, seed=seed)

    def _analyze_existing_data(self) -> Dict[str, Any]:
        """
        分析现有数据，提取关键信息

        Returns:
            数据分析结果
        """
        analysis = {
            'count': len(self.existing_data),
            'fields': {}
        }

        if not self.existing_data:
            return analysis

        # 分析每个字段
        for field_name, field in self.table.fields.items():
            field_analysis = {
                'type': field.field_type,
                'has_data': False,
                'min_value': None,
                'max_value': None,
                'unique_values': set(),
                'last_value': None
            }

            # 收集字段值
            values = []
            for record in self.existing_data:
                if field_name in record and record[field_name] is not None:
                    value = record[field_name]
                    values.append(value)
                    field_analysis['unique_values'].add(value)

            if values:
                field_analysis['has_data'] = True
                field_analysis['last_value'] = values[-1]

                # 根据字段类型分析
                if field.field_type in (FieldType.INTEGER, FieldType.DECIMAL, FieldType.AMOUNT):
                    field_analysis['min_value'] = min(values)
                    field_analysis['max_value'] = max(values)

                elif field.field_type in (FieldType.DATE, FieldType.DATETIME):
                    # 转换为datetime进行比较
                    date_values = []
                    for v in values:
                        if isinstance(v, str):
                            try:
                                if field.field_type == FieldType.DATE:
                                    date_values.append(datetime.strptime(v, '%Y-%m-%d'))
                                else:
                                    date_values.append(datetime.strptime(v, '%Y-%m-%d %H:%M:%S'))
                            except ValueError:
                                pass
                        elif isinstance(v, datetime):
                            date_values.append(v)

                    if date_values:
                        field_analysis['min_value'] = min(date_values)
                        field_analysis['max_value'] = max(date_values)

            # 转换set为list以便序列化
            field_analysis['unique_values'] = list(field_analysis['unique_values'])
            analysis['fields'][field_name] = field_analysis

        return analysis

    def generate_incremental_data(self, count: int) -> List[Dict[str, Any]]:
        """
        生成增量数据

        Args:
            count: 要生成的记录数

        Returns:
            增量数据列表
        """
        incremental_data = []

        for i in range(count):
            record = self._generate_incremental_record(i)
            incremental_data.append(record)

        return incremental_data

    def _generate_incremental_record(self, index: int) -> Dict[str, Any]:
        """
        生成单条增量记录

        Args:
            index: 记录索引

        Returns:
            增量记录
        """
        record = {}

        for field_name, field in self.table.fields.items():
            field_analysis = self.data_analysis['fields'].get(field_name, {})

            # 根据字段类型和现有数据生成值
            if field.field_type == FieldType.ID and field_name == self.table.primary_key:
                # 主键ID：在最大值基础上递增
                record[field_name] = self._generate_incremental_id(field, field_analysis, index)

            elif field.field_type in (FieldType.INTEGER, FieldType.DECIMAL, FieldType.AMOUNT):
                # 数值类型：保持在现有范围内或略微扩展
                record[field_name] = self._generate_incremental_number(field, field_analysis)

            elif field.field_type in (FieldType.DATE, FieldType.DATETIME):
                # 日期类型：在最近日期之后
                record[field_name] = self._generate_incremental_date(field, field_analysis)

            else:
                # 其他类型：使用基础生成器
                record[field_name] = self.base_generator.field_generator.generate_value(field)

        return record

    def _generate_incremental_id(self, field: Field, analysis: Dict[str, Any], index: int) -> Any:
        """生成递增的ID"""
        if analysis.get('has_data') and analysis.get('max_value') is not None:
            # 在最大值基础上递增
            max_id = analysis['max_value']

            # 尝试转换为整数
            try:
                if isinstance(max_id, str):
                    # 提取字符串中的数字部分
                    import re
                    numbers = re.findall(r'\d+', max_id)
                    if numbers:
                        max_id = int(numbers[-1])
                    else:
                        max_id = 0
                else:
                    max_id = int(max_id)

                return max_id + index + 1

            except (ValueError, TypeError):
                # 无法提取数字，使用基础生成器
                return self.base_generator.field_generator.generate_value(field)
        else:
            # 没有现有数据，从1开始
            return index + 1

    def _generate_incremental_number(self, field: Field, analysis: Dict[str, Any]) -> Any:
        """生成数值（保持在现有范围内或略微扩展）"""
        if analysis.get('has_data') and analysis.get('min_value') is not None:
            min_val = analysis['min_value']
            max_val = analysis['max_value']

            # 扩展范围（增加10%的变化）
            range_size = max_val - min_val
            if range_size > 0:
                min_val = min_val - range_size * 0.1
                max_val = max_val + range_size * 0.1

            # 生成值
            if field.field_type == FieldType.INTEGER:
                return random.randint(int(min_val), int(max_val))
            else:
                value = random.uniform(min_val, max_val)
                if field.precision:
                    return round(value, field.precision)
                return value
        else:
            # 使用基础生成器
            return self.base_generator.field_generator.generate_value(field)

    def _generate_incremental_date(self, field: Field, analysis: Dict[str, Any]) -> str:
        """生成递增的日期（在最近日期之后）"""
        if analysis.get('has_data') and analysis.get('max_value') is not None:
            max_date = analysis['max_value']

            # 确保是datetime对象
            if isinstance(max_date, str):
                try:
                    if field.field_type == FieldType.DATE:
                        max_date = datetime.strptime(max_date, '%Y-%m-%d')
                    else:
                        max_date = datetime.strptime(max_date, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    max_date = datetime.now()
            elif not isinstance(max_date, datetime):
                max_date = datetime.now()

            # 在最近日期后1-30天
            days_after = random.randint(1, 30)
            new_date = max_date + timedelta(days=days_after)

            # 格式化返回
            if field.field_type == FieldType.DATE:
                return new_date.strftime('%Y-%m-%d')
            else:
                return new_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 使用基础生成器
            return self.base_generator.field_generator.generate_value(field)

    def generate_with_relations(
        self,
        count: int,
        related_data: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成带关联的增量数据

        Args:
            count: 要生成的记录数
            related_data: 关联表的ID列表，格式: {table_name: [id1, id2, ...]}

        Returns:
            增量数据列表
        """
        incremental_data = []

        for i in range(count):
            record = self._generate_incremental_record(i)

            # 处理外键关联
            for fk in self.table.foreign_keys:
                field_name = fk['field_name']
                ref_table = fk['reference_table']

                if ref_table in related_data and related_data[ref_table]:
                    # 从关联数据中随机选择
                    record[field_name] = random.choice(related_data[ref_table])

            incremental_data.append(record)

        return incremental_data


def generate_incremental_data(
    table: Table,
    existing_data: List[Dict[str, Any]],
    count: int,
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    便捷函数：生成增量数据

    Args:
        table: 表定义
        existing_data: 现有数据
        count: 要生成的记录数
        seed: 随机种子

    Returns:
        增量数据列表
    """
    generator = IncrementalGenerator(table, existing_data, seed=seed)
    return generator.generate_incremental_data(count)
