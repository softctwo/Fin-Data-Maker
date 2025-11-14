"""
内置的数据生成策略实现
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import math

from .strategy import (
    GenerationStrategy,
    StrategyType,
    StrategyContext,
    register_strategy
)


@register_strategy(StrategyType.SEQUENTIAL)
class SequentialStrategy(GenerationStrategy):
    """
    顺序生成策略
    生成递增的序列值

    配置参数:
        start: 起始值（默认1）
        step: 步长（默认1）
        format: 格式化字符串（可选，如 "ID_{:05d}"）
    """

    def __init__(self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, description, config)
        self.current = self.config.get('start', 1)
        self.step = self.config.get('step', 1)
        self.format_str = self.config.get('format', None)

    def generate(self, context: StrategyContext) -> Any:
        value = self.current
        self.current += self.step

        if self.format_str:
            return self.format_str.format(value)
        return value

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.SEQUENTIAL

    def reset(self):
        self.current = self.config.get('start', 1)


@register_strategy(StrategyType.RANDOM_RANGE)
class RandomRangeStrategy(GenerationStrategy):
    """
    随机范围生成策略
    在指定范围内生成随机值

    配置参数:
        min_value: 最小值
        max_value: 最大值
        data_type: 数据类型 ('int', 'float', 'decimal')
        precision: 小数精度（仅用于float和decimal）
    """

    def generate(self, context: StrategyContext) -> Any:
        min_val = self.config.get('min_value', 0)
        max_val = self.config.get('max_value', 100)
        data_type = self.config.get('data_type', 'int')
        precision = self.config.get('precision', 2)

        if data_type == 'int':
            return random.randint(min_val, max_val)
        elif data_type in ['float', 'decimal']:
            value = random.uniform(min_val, max_val)
            return round(value, precision)
        else:
            return random.randint(min_val, max_val)

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.RANDOM_RANGE


@register_strategy(StrategyType.WEIGHTED_CHOICE)
class WeightedChoiceStrategy(GenerationStrategy):
    """
    加权选择策略
    根据权重从选项中随机选择

    配置参数:
        choices: 选项列表
        weights: 权重列表（与choices对应）
    """

    def generate(self, context: StrategyContext) -> Any:
        choices = self.config.get('choices', [])
        weights = self.config.get('weights', None)

        if not choices:
            return None

        if weights and len(weights) == len(choices):
            return random.choices(choices, weights=weights, k=1)[0]
        else:
            return random.choice(choices)

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.WEIGHTED_CHOICE

    def validate_config(self) -> bool:
        choices = self.config.get('choices', [])
        weights = self.config.get('weights', None)

        if not choices:
            return False

        if weights and len(weights) != len(choices):
            return False

        return True


@register_strategy(StrategyType.CONDITIONAL)
class ConditionalStrategy(GenerationStrategy):
    """
    条件生成策略
    根据条件生成不同的值

    配置参数:
        conditions: 条件列表，每个条件包含:
            - field: 判断的字段名
            - operator: 操作符 ('eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'in', 'not_in')
            - value: 比较值
            - result: 满足条件时的返回值
        default: 默认值（所有条件都不满足时）
    """

    def generate(self, context: StrategyContext) -> Any:
        conditions = self.config.get('conditions', [])
        default = self.config.get('default', None)

        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            compare_value = condition.get('value')
            result = condition.get('result')

            field_value = context.get_field_value(field)

            if self._evaluate_condition(field_value, operator, compare_value):
                return result

        return default

    def _evaluate_condition(self, field_value: Any, operator: str, compare_value: Any) -> bool:
        """评估条件"""
        if operator == 'eq':
            return field_value == compare_value
        elif operator == 'ne':
            return field_value != compare_value
        elif operator == 'gt':
            return field_value > compare_value
        elif operator == 'lt':
            return field_value < compare_value
        elif operator == 'gte':
            return field_value >= compare_value
        elif operator == 'lte':
            return field_value <= compare_value
        elif operator == 'in':
            return field_value in compare_value
        elif operator == 'not_in':
            return field_value not in compare_value
        else:
            return False

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.CONDITIONAL


@register_strategy(StrategyType.DEPENDENT_FIELD)
class DependentFieldStrategy(GenerationStrategy):
    """
    依赖字段策略
    根据其他字段的值生成数据

    配置参数:
        source_field: 依赖的源字段
        mapping: 映射关系字典 {source_value: target_value}
        calculation: 计算方式 ('multiply', 'divide', 'add', 'subtract', 'percentage')
        factor: 计算因子（用于数值计算）
        default: 默认值
    """

    def generate(self, context: StrategyContext) -> Any:
        source_field = self.config.get('source_field')
        mapping = self.config.get('mapping', {})
        calculation = self.config.get('calculation', None)
        factor = self.config.get('factor', 1)
        default = self.config.get('default', None)

        source_value = context.get_field_value(source_field)

        if source_value is None:
            return default

        # 如果有映射关系，使用映射
        if mapping:
            return mapping.get(str(source_value), default)

        # 如果有计算方式，进行计算
        if calculation and isinstance(source_value, (int, float)):
            if calculation == 'multiply':
                return source_value * factor
            elif calculation == 'divide':
                return source_value / factor if factor != 0 else default
            elif calculation == 'add':
                return source_value + factor
            elif calculation == 'subtract':
                return source_value - factor
            elif calculation == 'percentage':
                return source_value * (factor / 100)

        return default

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.DEPENDENT_FIELD


@register_strategy(StrategyType.DATE_RANGE)
class DateRangeStrategy(GenerationStrategy):
    """
    日期范围生成策略
    在指定日期范围内生成随机日期

    配置参数:
        start_date: 起始日期（字符串格式 'YYYY-MM-DD' 或 'now', 'today'）
        end_date: 结束日期（字符串格式 'YYYY-MM-DD' 或 'now', 'today'）
        date_format: 输出日期格式（默认 '%Y-%m-%d'）
        sequential: 是否顺序生成（默认False）
        step_days: 顺序生成时的步长天数（默认1）
    """

    def __init__(self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, description, config)
        self.current_date = None

    def generate(self, context: StrategyContext) -> Any:
        start_date = self._parse_date(self.config.get('start_date', 'today'))
        end_date = self._parse_date(self.config.get('end_date', 'today'))
        date_format = self.config.get('date_format', '%Y-%m-%d')
        sequential = self.config.get('sequential', False)
        step_days = self.config.get('step_days', 1)

        if sequential:
            if self.current_date is None:
                self.current_date = start_date
            else:
                self.current_date += timedelta(days=step_days)

            if self.current_date > end_date:
                self.current_date = start_date

            result_date = self.current_date
        else:
            # 随机生成
            time_delta = end_date - start_date
            random_days = random.randint(0, time_delta.days)
            result_date = start_date + timedelta(days=random_days)

        return result_date.strftime(date_format)

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if date_str in ['now', 'today']:
            return datetime.now()
        else:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.now()

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.DATE_RANGE

    def reset(self):
        self.current_date = None


@register_strategy(StrategyType.CUSTOM_FUNCTION)
class CustomFunctionStrategy(GenerationStrategy):
    """
    自定义函数策略
    使用用户自定义的Python表达式生成数据

    配置参数:
        expression: Python表达式（可以访问context）
        例如: "context.row_index * 100"
              "random.randint(1, 100) if context.get_field_value('type') == 'A' else 0"
    """

    def generate(self, context: StrategyContext) -> Any:
        expression = self.config.get('expression', '')

        if not expression:
            return None

        # 创建安全的执行环境
        safe_globals = {
            'random': random,
            'math': math,
            'datetime': datetime,
            'timedelta': timedelta,
            'context': context,
            '__builtins__': {}
        }

        try:
            result = eval(expression, safe_globals)
            return result
        except Exception as e:
            print(f"Error evaluating expression: {e}")
            return None

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.CUSTOM_FUNCTION


@register_strategy(StrategyType.DISTRIBUTION)
class DistributionStrategy(GenerationStrategy):
    """
    分布生成策略
    根据统计分布生成数据

    配置参数:
        distribution_type: 分布类型 ('normal', 'uniform', 'exponential', 'poisson')
        mean: 均值（用于正态分布）
        std_dev: 标准差（用于正态分布）
        min_value: 最小值（用于均匀分布）
        max_value: 最大值（用于均匀分布）
        lambda_param: Lambda参数（用于指数分布和泊松分布）
        round_to_int: 是否四舍五入为整数（默认False）
    """

    def generate(self, context: StrategyContext) -> Any:
        dist_type = self.config.get('distribution_type', 'normal')
        round_to_int = self.config.get('round_to_int', False)

        if dist_type == 'normal':
            mean = self.config.get('mean', 0)
            std_dev = self.config.get('std_dev', 1)
            value = random.gauss(mean, std_dev)
        elif dist_type == 'uniform':
            min_val = self.config.get('min_value', 0)
            max_val = self.config.get('max_value', 1)
            value = random.uniform(min_val, max_val)
        elif dist_type == 'exponential':
            lambda_param = self.config.get('lambda_param', 1.0)
            value = random.expovariate(lambda_param)
        elif dist_type == 'poisson':
            lambda_param = self.config.get('lambda_param', 1.0)
            # 使用numpy的泊松分布更好，但为了避免依赖，这里简化处理
            # 使用近似方法
            value = -math.log(random.random()) * lambda_param
        else:
            value = 0

        if round_to_int:
            return int(round(value))
        else:
            return round(value, self.config.get('precision', 2))

    def get_strategy_type(self) -> StrategyType:
        return StrategyType.DISTRIBUTION
