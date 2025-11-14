"""
字段定义模块
定义字段的类型、约束、规则等
"""

from enum import Enum
from typing import Any, Optional, List, Dict
from datetime import datetime


class FieldType(Enum):
    """字段类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    ENUM = "enum"
    ID = "id"  # 唯一标识符
    PHONE = "phone"  # 电话号码
    EMAIL = "email"  # 邮箱
    ID_CARD = "id_card"  # 身份证号
    BANK_CARD = "bank_card"  # 银行卡号
    AMOUNT = "amount"  # 金额


class Field:
    """
    字段定义类
    定义字段的属性、约束和生成规则
    """

    def __init__(
        self,
        name: str,
        field_type: FieldType,
        description: str = "",
        required: bool = True,
        unique: bool = False,
        length: Optional[int] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        precision: Optional[int] = None,  # 小数位数
        enum_values: Optional[List[Any]] = None,
        default_value: Any = None,
        pattern: Optional[str] = None,  # 正则表达式
        reference_table: Optional[str] = None,  # 外键引用表
        reference_field: Optional[str] = None,  # 外键引用字段
        custom_generator: Optional[str] = None,  # 自定义生成器名称
        metadata: Optional[Dict[str, Any]] = None,  # 额外元数据
    ):
        self.name = name
        self.field_type = field_type
        self.description = description
        self.required = required
        self.unique = unique
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision
        self.enum_values = enum_values or []
        self.default_value = default_value
        self.pattern = pattern
        self.reference_table = reference_table
        self.reference_field = reference_field
        self.custom_generator = custom_generator
        self.metadata = metadata or {}

    def validate(self, value: Any) -> bool:
        """
        验证值是否符合字段定义

        Args:
            value: 要验证的值

        Returns:
            bool: 是否有效
        """
        # 必填项检查
        if self.required and value is None:
            return False

        if value is None:
            return True

        # 类型检查
        if self.field_type == FieldType.STRING:
            if not isinstance(value, str):
                return False
            if self.length and len(value) != self.length:
                return False
            if self.min_length and len(value) < self.min_length:
                return False
            if self.max_length and len(value) > self.max_length:
                return False

        elif self.field_type == FieldType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        elif self.field_type in [FieldType.DECIMAL, FieldType.AMOUNT]:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        elif self.field_type in [FieldType.DATE, FieldType.DATETIME]:
            if not isinstance(value, (datetime, str)):
                return False

        elif self.field_type == FieldType.ENUM:
            if value not in self.enum_values:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "type": self.field_type.value,
            "description": self.description,
            "required": self.required,
            "unique": self.unique,
            "length": self.length,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "precision": self.precision,
            "enum_values": self.enum_values,
            "default_value": self.default_value,
            "pattern": self.pattern,
            "reference_table": self.reference_table,
            "reference_field": self.reference_field,
            "custom_generator": self.custom_generator,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Field':
        """从字典创建字段对象"""
        field_type = FieldType(data.get("type", "string"))
        return cls(
            name=data["name"],
            field_type=field_type,
            description=data.get("description", ""),
            required=data.get("required", True),
            unique=data.get("unique", False),
            length=data.get("length"),
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            precision=data.get("precision"),
            enum_values=data.get("enum_values"),
            default_value=data.get("default_value"),
            pattern=data.get("pattern"),
            reference_table=data.get("reference_table"),
            reference_field=data.get("reference_field"),
            custom_generator=data.get("custom_generator"),
            metadata=data.get("metadata", {}),
        )
