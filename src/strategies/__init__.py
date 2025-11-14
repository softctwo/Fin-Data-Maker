"""
自定义数据生成策略模块
提供灵活的数据生成策略系统，允许用户定义自己的生成逻辑
"""

from .strategy import (
    GenerationStrategy,
    StrategyType,
    StrategyContext,
    StrategyRegistry
)

from .builtin_strategies import (
    SequentialStrategy,
    RandomRangeStrategy,
    WeightedChoiceStrategy,
    ConditionalStrategy,
    DependentFieldStrategy,
    DateRangeStrategy,
    CustomFunctionStrategy,
    DistributionStrategy
)

from .strategy_manager import StrategyManager

__all__ = [
    'GenerationStrategy',
    'StrategyType',
    'StrategyContext',
    'StrategyRegistry',
    'SequentialStrategy',
    'RandomRangeStrategy',
    'WeightedChoiceStrategy',
    'ConditionalStrategy',
    'DependentFieldStrategy',
    'DateRangeStrategy',
    'CustomFunctionStrategy',
    'DistributionStrategy',
    'StrategyManager'
]
