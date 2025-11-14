"""
基础生成器
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import random


class BaseGenerator(ABC):
    """
    数据生成器基类
    所有数据生成器都需要继承此类
    """

    def __init__(self, seed: Optional[int] = None):
        """
        初始化生成器

        Args:
            seed: 随机种子，用于生成可重复的数据
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    @abstractmethod
    def generate(self, **kwargs) -> Any:
        """
        生成数据

        Args:
            **kwargs: 生成参数

        Returns:
            Any: 生成的数据
        """
        pass

    def generate_batch(self, count: int, **kwargs) -> list:
        """
        批量生成数据

        Args:
            count: 生成数量
            **kwargs: 生成参数

        Returns:
            list: 生成的数据列表
        """
        return [self.generate(**kwargs) for _ in range(count)]
