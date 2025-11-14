"""
字段数据生成器
根据字段类型生成相应的数据
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Optional, Set, Dict
from faker import Faker
from ..metadata.field import Field, FieldType
from .base_generator import BaseGenerator

# 导入策略相关类
try:
    from ..strategies.strategy import StrategyContext
    from ..strategies.strategy_manager import StrategyManager
    STRATEGIES_AVAILABLE = True
except ImportError:
    STRATEGIES_AVAILABLE = False


class FieldGenerator(BaseGenerator):
    """
    字段数据生成器
    根据字段定义生成符合要求的数据
    """

    def __init__(self, seed: Optional[int] = None, locale: str = 'zh_CN'):
        """
        初始化字段生成器

        Args:
            seed: 随机种子
            locale: 语言区域设置
        """
        super().__init__(seed)
        self.faker = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
        self.unique_values: dict[str, Set[Any]] = {}

        # 初始化策略管理器
        self.strategy_manager = StrategyManager() if STRATEGIES_AVAILABLE else None

        # 字段到策略的映射
        self.field_strategies: Dict[str, str] = {}

    def generate(self, field: Field, **kwargs) -> Any:
        """
        生成字段数据

        Args:
            field: 字段定义
            **kwargs: 额外参数（可以包含context用于策略生成）

        Returns:
            Any: 生成的字段值
        """
        # 检查是否使用自定义策略
        if self.strategy_manager and field.name in self.field_strategies:
            strategy_name = self.field_strategies[field.name]
            context = kwargs.get('context')

            if context:
                value = self.strategy_manager.apply_strategy(strategy_name, context)
                if value is not None:
                    # 如果字段要求唯一，确保唯一性
                    if field.unique:
                        value = self._ensure_unique(field.name, value, field)
                    return value

        # 如果有默认值，使用默认值
        if field.default_value is not None:
            return field.default_value

        # 如果字段非必填且随机决定为空
        if not field.required and random.random() < 0.1:  # 10%概率为空
            return None

        # 根据字段类型生成数据
        value = self._generate_by_type(field)

        # 如果字段要求唯一，确保唯一性
        if field.unique:
            value = self._ensure_unique(field.name, value, field)

        return value

    def _generate_by_type(self, field: Field) -> Any:
        """根据字段类型生成数据"""
        field_type = field.field_type

        if field_type == FieldType.STRING:
            return self._generate_string(field)
        elif field_type == FieldType.INTEGER:
            return self._generate_integer(field)
        elif field_type == FieldType.DECIMAL or field_type == FieldType.AMOUNT:
            return self._generate_decimal(field)
        elif field_type == FieldType.DATE:
            return self._generate_date(field)
        elif field_type == FieldType.DATETIME:
            return self._generate_datetime(field)
        elif field_type == FieldType.BOOLEAN:
            return self._generate_boolean(field)
        elif field_type == FieldType.ENUM:
            return self._generate_enum(field)
        elif field_type == FieldType.ID:
            return self._generate_id(field)
        elif field_type == FieldType.PHONE:
            return self._generate_phone(field)
        elif field_type == FieldType.EMAIL:
            return self._generate_email(field)
        elif field_type == FieldType.ID_CARD:
            return self._generate_id_card(field)
        elif field_type == FieldType.BANK_CARD:
            return self._generate_bank_card(field)
        else:
            return self._generate_string(field)

    def _generate_string(self, field: Field) -> str:
        """生成字符串"""
        if field.length:
            length = field.length
        elif field.max_length:
            min_len = field.min_length or 1
            length = random.randint(min_len, field.max_length)
        else:
            length = random.randint(5, 20)

        # 如果有正则表达式模式，尝试生成匹配的字符串
        if field.pattern:
            # 简单实现，实际可使用rstr等库
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        return self.faker.text(max_nb_chars=length)[:length]

    def _generate_integer(self, field: Field) -> int:
        """生成整数"""
        min_val = int(field.min_value) if field.min_value is not None else 0
        max_val = int(field.max_value) if field.max_value is not None else 1000000
        return random.randint(min_val, max_val)

    def _generate_decimal(self, field: Field) -> float:
        """生成小数"""
        min_val = field.min_value if field.min_value is not None else 0.0
        max_val = field.max_value if field.max_value is not None else 1000000.0
        value = random.uniform(min_val, max_val)

        if field.precision is not None:
            value = round(value, field.precision)

        return value

    def _generate_date(self, field: Field) -> str:
        """生成日期"""
        date = self.faker.date_between(start_date='-10y', end_date='today')
        return date.strftime('%Y-%m-%d')

    def _generate_datetime(self, field: Field) -> str:
        """生成日期时间"""
        dt = self.faker.date_time_between(start_date='-10y', end_date='now')
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _generate_boolean(self, field: Field) -> bool:
        """生成布尔值"""
        return random.choice([True, False])

    def _generate_enum(self, field: Field) -> Any:
        """生成枚举值"""
        if field.enum_values:
            return random.choice(field.enum_values)
        return None

    def _generate_id(self, field: Field) -> str:
        """生成唯一标识符"""
        if field.length:
            length = field.length
        else:
            length = 32
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def _generate_phone(self, field: Field) -> str:
        """生成电话号码"""
        return self.faker.phone_number()

    def _generate_email(self, field: Field) -> str:
        """生成邮箱"""
        return self.faker.email()

    def _generate_id_card(self, field: Field) -> str:
        """生成身份证号"""
        return self.faker.ssn()

    def _generate_bank_card(self, field: Field) -> str:
        """生成银行卡号"""
        return self.faker.credit_card_number()

    def _ensure_unique(self, field_name: str, value: Any, field: Field) -> Any:
        """确保值的唯一性"""
        if field_name not in self.unique_values:
            self.unique_values[field_name] = set()

        # 如果值已存在，重新生成
        max_attempts = 1000
        attempts = 0
        while value in self.unique_values[field_name] and attempts < max_attempts:
            value = self._generate_by_type(field)
            attempts += 1

        if attempts >= max_attempts:
            # 如果尝试次数过多，添加后缀确保唯一
            value = f"{value}_{len(self.unique_values[field_name])}"

        self.unique_values[field_name].add(value)
        return value

    def reset_unique_tracker(self):
        """重置唯一值跟踪器"""
        self.unique_values = {}

    # ===== 策略管理方法 =====

    def set_field_strategy(self, field_name: str, strategy_name: str):
        """
        为字段设置自定义策略

        Args:
            field_name: 字段名
            strategy_name: 策略名
        """
        self.field_strategies[field_name] = strategy_name

    def remove_field_strategy(self, field_name: str):
        """
        移除字段的自定义策略

        Args:
            field_name: 字段名
        """
        if field_name in self.field_strategies:
            del self.field_strategies[field_name]

    def get_strategy_manager(self) -> Optional[StrategyManager]:
        """获取策略管理器"""
        return self.strategy_manager
