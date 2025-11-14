"""
数据生成策略基类和接口定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import json


class StrategyType(Enum):
    """策略类型枚举"""
    SEQUENTIAL = "sequential"          # 顺序生成
    RANDOM_RANGE = "random_range"      # 随机范围
    WEIGHTED_CHOICE = "weighted_choice"  # 加权选择
    CONDITIONAL = "conditional"        # 条件生成
    DEPENDENT_FIELD = "dependent_field"  # 依赖字段
    DATE_RANGE = "date_range"          # 日期范围
    CUSTOM_FUNCTION = "custom_function"  # 自定义函数
    DISTRIBUTION = "distribution"      # 分布生成（正态、均匀等）


@dataclass
class StrategyContext:
    """
    策略上下文，包含生成时的所有相关信息
    """
    # 当前行数据（已生成的字段）
    current_row: Dict[str, Any] = field(default_factory=dict)

    # 当前行索引
    row_index: int = 0

    # 总行数
    total_rows: int = 0

    # 字段元数据
    field_metadata: Dict[str, Any] = field(default_factory=dict)

    # 表元数据
    table_metadata: Dict[str, Any] = field(default_factory=dict)

    # 其他上下文数据
    extra: Dict[str, Any] = field(default_factory=dict)

    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """获取当前行中某个字段的值"""
        return self.current_row.get(field_name, default)

    def set_field_value(self, field_name: str, value: Any):
        """设置当前行中某个字段的值"""
        self.current_row[field_name] = value


class GenerationStrategy(ABC):
    """
    数据生成策略基类
    所有自定义策略都应继承此类
    """

    def __init__(self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None):
        """
        初始化策略

        Args:
            name: 策略名称
            description: 策略描述
            config: 策略配置参数
        """
        self.name = name
        self.description = description
        self.config = config or {}

    @abstractmethod
    def generate(self, context: StrategyContext) -> Any:
        """
        生成数据的核心方法

        Args:
            context: 策略上下文

        Returns:
            生成的数据值
        """
        pass

    @abstractmethod
    def get_strategy_type(self) -> StrategyType:
        """返回策略类型"""
        pass

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            配置是否有效
        """
        return True

    def reset(self):
        """重置策略状态（用于生成新批次数据时）"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.get_strategy_type().value,
            'config': self.config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationStrategy':
        """从字典创建策略实例"""
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            config=data.get('config', {})
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type={self.get_strategy_type().value})"


class StrategyRegistry:
    """
    策略注册表，管理所有可用的策略
    """

    def __init__(self):
        self._strategies: Dict[str, type] = {}

    def register(self, strategy_class: type, strategy_type: StrategyType):
        """
        注册策略类

        Args:
            strategy_class: 策略类
            strategy_type: 策略类型
        """
        if not issubclass(strategy_class, GenerationStrategy):
            raise ValueError(f"{strategy_class} must inherit from GenerationStrategy")

        self._strategies[strategy_type.value] = strategy_class

    def get(self, strategy_type: str) -> Optional[type]:
        """
        获取策略类

        Args:
            strategy_type: 策略类型

        Returns:
            策略类，如果不存在则返回None
        """
        return self._strategies.get(strategy_type)

    def create(self, strategy_type: str, name: str, description: str = "",
               config: Optional[Dict[str, Any]] = None) -> Optional[GenerationStrategy]:
        """
        创建策略实例

        Args:
            strategy_type: 策略类型
            name: 策略名称
            description: 策略描述
            config: 策略配置

        Returns:
            策略实例，如果策略类型不存在则返回None
        """
        strategy_class = self.get(strategy_type)
        if strategy_class is None:
            return None

        return strategy_class(name=name, description=description, config=config)

    def list_types(self) -> List[str]:
        """返回所有已注册的策略类型"""
        return list(self._strategies.keys())

    def is_registered(self, strategy_type: str) -> bool:
        """检查策略类型是否已注册"""
        return strategy_type in self._strategies


# 全局策略注册表
_global_registry = StrategyRegistry()


def get_global_registry() -> StrategyRegistry:
    """获取全局策略注册表"""
    return _global_registry


def register_strategy(strategy_type: StrategyType):
    """
    策略注册装饰器

    Usage:
        @register_strategy(StrategyType.SEQUENTIAL)
        class MyStrategy(GenerationStrategy):
            ...
    """
    def decorator(strategy_class: type):
        _global_registry.register(strategy_class, strategy_type)
        return strategy_class
    return decorator
