"""
元数据管理器
管理所有表和字段的元数据定义
"""

import yaml
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from .table import Table
from .field import Field


class MetadataManager:
    """
    元数据管理器
    负责加载、保存和管理元数据定义
    """

    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def add_table(self, table: Table):
        """添加表定义"""
        self.tables[table.name] = table

    def get_table(self, name: str) -> Optional[Table]:
        """获取表定义"""
        return self.tables.get(name)

    def remove_table(self, name: str):
        """删除表定义"""
        if name in self.tables:
            del self.tables[name]

    def list_tables(self) -> List[str]:
        """列出所有表名"""
        return list(self.tables.keys())

    def load_from_yaml(self, file_path: str):
        """
        从YAML文件加载元数据定义

        Args:
            file_path: YAML文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if 'tables' in data:
            for table_data in data['tables']:
                table = Table.from_dict(table_data)
                self.add_table(table)

    def load_from_json(self, file_path: str):
        """
        从JSON文件加载元数据定义

        Args:
            file_path: JSON文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'tables' in data:
            for table_data in data['tables']:
                table = Table.from_dict(table_data)
                self.add_table(table)

    def save_to_yaml(self, file_path: str):
        """
        保存元数据定义到YAML文件

        Args:
            file_path: YAML文件路径
        """
        data = {
            'tables': [table.to_dict() for table in self.tables.values()]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def save_to_json(self, file_path: str):
        """
        保存元数据定义到JSON文件

        Args:
            file_path: JSON文件路径
        """
        data = {
            'tables': [table.to_dict() for table in self.tables.values()]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def validate_metadata(self) -> List[str]:
        """
        验证元数据定义的完整性和一致性

        Returns:
            List[str]: 错误信息列表
        """
        errors = []

        for table_name, table in self.tables.items():
            # 检查主键字段是否存在
            if table.primary_key and not table.get_field(table.primary_key):
                errors.append(f"表 {table_name} 的主键字段 {table.primary_key} 不存在")

            # 检查索引字段是否存在
            for index_field in table.indexes:
                if not table.get_field(index_field):
                    errors.append(f"表 {table_name} 的索引字段 {index_field} 不存在")

            # 检查外键引用
            for field in table.fields:
                if field.reference_table:
                    ref_table = self.get_table(field.reference_table)
                    if not ref_table:
                        errors.append(
                            f"表 {table_name} 字段 {field.name} "
                            f"引用的表 {field.reference_table} 不存在"
                        )
                    elif field.reference_field and not ref_table.get_field(field.reference_field):
                        errors.append(
                            f"表 {table_name} 字段 {field.name} "
                            f"引用的字段 {field.reference_field} 不存在"
                        )

        return errors
