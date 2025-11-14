"""
表定义模块
定义数据表的结构、字段、约束等
"""

from typing import List, Dict, Any, Optional
from .field import Field


class Table:
    """
    数据表定义类
    定义表的结构、字段列表和约束
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fields: Optional[List[Field]] = None,
        primary_key: Optional[str] = None,
        indexes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化表定义

        Args:
            name: 表名
            description: 表描述
            fields: 字段列表
            primary_key: 主键字段名
            indexes: 索引字段列表
            metadata: 额外元数据
        """
        self.name = name
        self.description = description
        self.fields = fields or []
        self.primary_key = primary_key
        self.indexes = indexes or []
        self.metadata = metadata or {}

        # 创建字段名到字段对象的映射
        self._field_map = {field.name: field for field in self.fields}

    def add_field(self, field: Field):
        """添加字段"""
        self.fields.append(field)
        self._field_map[field.name] = field

    def get_field(self, name: str) -> Optional[Field]:
        """获取字段"""
        return self._field_map.get(name)

    def get_required_fields(self) -> List[Field]:
        """获取所有必填字段"""
        return [field for field in self.fields if field.required]

    def get_unique_fields(self) -> List[Field]:
        """获取所有唯一字段"""
        return [field for field in self.fields if field.unique]

    def validate_row(self, row: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        验证一行数据

        Args:
            row: 行数据字典

        Returns:
            Dict[str, List[str]]: 字段名到错误信息列表的映射
        """
        errors = {}

        for field in self.fields:
            field_errors = []
            value = row.get(field.name)

            # 必填检查
            if field.required and value is None:
                field_errors.append(f"字段 {field.name} 为必填项")

            # 字段验证
            if value is not None and not field.validate(value):
                field_errors.append(f"字段 {field.name} 值 {value} 不符合定义")

            if field_errors:
                errors[field.name] = field_errors

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "description": self.description,
            "fields": [field.to_dict() for field in self.fields],
            "primary_key": self.primary_key,
            "indexes": self.indexes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """从字典创建表对象"""
        fields = [Field.from_dict(f) for f in data.get("fields", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            fields=fields,
            primary_key=data.get("primary_key"),
            indexes=data.get("indexes", []),
            metadata=data.get("metadata", {}),
        )
