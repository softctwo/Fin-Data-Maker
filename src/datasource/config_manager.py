"""
数据源配置管理器
管理数据源连接配置
"""

import yaml
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class DataSourceConfig:
    """数据源配置类"""

    def __init__(
        self,
        name: str,
        db_type: str,
        host: str = "",
        port: Optional[int] = None,
        database: str = "",
        username: str = "",
        password: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.db_type = db_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.options = options or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'type': self.db_type,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password,
            'options': self.options,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSourceConfig':
        """从字典创建配置"""
        return cls(
            name=data.get('name', ''),
            db_type=data.get('type', ''),
            host=data.get('host', ''),
            port=data.get('port'),
            database=data.get('database', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            options=data.get('options', {}),
        )


class ConfigManager:
    """
    配置管理器
    管理数据源配置的保存和加载
    """

    def __init__(self, config_file: str = "config/datasources.yaml"):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.configs: Dict[str, DataSourceConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """加载配置文件"""
        config_path = Path(self.config_file)

        if not config_path.exists():
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                    data = yaml.safe_load(f)
                elif config_path.suffix == '.json':
                    data = json.load(f)
                else:
                    return

            if data and 'datasources' in data:
                for ds_data in data['datasources']:
                    config = DataSourceConfig.from_dict(ds_data)
                    self.configs[config.name] = config

        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")

    def save_configs(self):
        """保存配置文件"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'datasources': [config.to_dict() for config in self.configs.values()]
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False)
                elif config_path.suffix == '.json':
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def add_config(self, config: DataSourceConfig):
        """添加配置"""
        self.configs[config.name] = config
        self.save_configs()

    def get_config(self, name: str) -> Optional[DataSourceConfig]:
        """获取配置"""
        return self.configs.get(name)

    def remove_config(self, name: str):
        """删除配置"""
        if name in self.configs:
            del self.configs[name]
            self.save_configs()

    def list_configs(self) -> List[str]:
        """列出所有配置名称"""
        return list(self.configs.keys())

    def update_config(self, name: str, config: DataSourceConfig):
        """更新配置"""
        if name in self.configs:
            self.configs[name] = config
            self.save_configs()
