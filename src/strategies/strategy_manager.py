"""
策略管理器
管理策略的创建、存储和应用
"""

from typing import Dict, List, Optional, Any
import json
from pathlib import Path

from .strategy import GenerationStrategy, StrategyContext, get_global_registry


class StrategyManager:
    """
    策略管理器
    负责管理和应用数据生成策略
    """

    def __init__(self):
        self.registry = get_global_registry()
        self.strategies: Dict[str, GenerationStrategy] = {}

    def create_strategy(self, strategy_type: str, name: str,
                       description: str = "", config: Optional[Dict[str, Any]] = None) -> Optional[GenerationStrategy]:
        """
        创建策略

        Args:
            strategy_type: 策略类型
            name: 策略名称
            description: 策略描述
            config: 策略配置

        Returns:
            策略实例
        """
        strategy = self.registry.create(strategy_type, name, description, config)
        if strategy:
            self.strategies[name] = strategy
        return strategy

    def add_strategy(self, strategy: GenerationStrategy):
        """添加策略"""
        self.strategies[strategy.name] = strategy

    def get_strategy(self, name: str) -> Optional[GenerationStrategy]:
        """获取策略"""
        return self.strategies.get(name)

    def remove_strategy(self, name: str) -> bool:
        """删除策略"""
        if name in self.strategies:
            del self.strategies[name]
            return True
        return False

    def list_strategies(self) -> List[Dict[str, Any]]:
        """列出所有策略"""
        return [strategy.to_dict() for strategy in self.strategies.values()]

    def apply_strategy(self, strategy_name: str, context: StrategyContext) -> Any:
        """
        应用策略生成数据

        Args:
            strategy_name: 策略名称
            context: 策略上下文

        Returns:
            生成的数据值
        """
        strategy = self.get_strategy(strategy_name)
        if strategy:
            return strategy.generate(context)
        return None

    def reset_all_strategies(self):
        """重置所有策略状态"""
        for strategy in self.strategies.values():
            strategy.reset()

    def save_strategies(self, file_path: str):
        """
        保存策略配置到文件

        Args:
            file_path: 文件路径
        """
        data = {
            'strategies': [strategy.to_dict() for strategy in self.strategies.values()]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_strategies(self, file_path: str):
        """
        从文件加载策略配置

        Args:
            file_path: 文件路径
        """
        if not Path(file_path).exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        strategies_data = data.get('strategies', [])
        for strategy_data in strategies_data:
            strategy_type = strategy_data.get('type')
            name = strategy_data.get('name')
            description = strategy_data.get('description', '')
            config = strategy_data.get('config', {})

            strategy = self.create_strategy(strategy_type, name, description, config)
            if strategy:
                self.add_strategy(strategy)

    def get_available_strategy_types(self) -> List[str]:
        """获取所有可用的策略类型"""
        return self.registry.list_types()

    def validate_all_strategies(self) -> Dict[str, bool]:
        """验证所有策略的配置"""
        results = {}
        for name, strategy in self.strategies.items():
            results[name] = strategy.validate_config()
        return results
