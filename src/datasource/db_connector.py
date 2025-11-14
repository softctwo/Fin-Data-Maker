"""
数据库连接器
支持MySQL、PostgreSQL、Oracle、SQL Server等数据库
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
import logging

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"


class DatabaseConnector:
    """
    数据库连接器
    负责创建和管理数据库连接
    """

    def __init__(
        self,
        db_type: DatabaseType,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ):
        """
        初始化数据库连接器

        Args:
            db_type: 数据库类型
            host: 主机地址
            port: 端口号
            database: 数据库名
            username: 用户名
            password: 密码
            **kwargs: 其他连接参数
        """
        self.db_type = db_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.kwargs = kwargs
        self.engine: Optional[Engine] = None
        self._connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """构建数据库连接字符串"""
        if self.db_type == DatabaseType.MYSQL:
            port = self.port or 3306
            return (
                f"mysql+pymysql://{self.username}:{self.password}"
                f"@{self.host}:{port}/{self.database}"
                f"?charset=utf8mb4"
            )

        elif self.db_type == DatabaseType.POSTGRESQL:
            port = self.port or 5432
            return (
                f"postgresql+psycopg2://{self.username}:{self.password}"
                f"@{self.host}:{port}/{self.database}"
            )

        elif self.db_type == DatabaseType.ORACLE:
            port = self.port or 1521
            # Oracle连接字符串格式：oracle+cx_oracle://user:pass@host:port/?service_name=db
            service_name = self.kwargs.get('service_name', self.database)
            return (
                f"oracle+cx_oracle://{self.username}:{self.password}"
                f"@{self.host}:{port}/?service_name={service_name}"
            )

        elif self.db_type == DatabaseType.SQLSERVER:
            port = self.port or 1433
            driver = self.kwargs.get('driver', 'ODBC Driver 17 for SQL Server')
            return (
                f"mssql+pyodbc://{self.username}:{self.password}"
                f"@{self.host}:{port}/{self.database}"
                f"?driver={driver}"
            )

        elif self.db_type == DatabaseType.SQLITE:
            # SQLite使用文件路径
            return f"sqlite:///{self.database}"

        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

    def connect(self) -> Engine:
        """
        连接数据库

        Returns:
            Engine: SQLAlchemy引擎对象
        """
        try:
            self.engine = create_engine(
                self._connection_string,
                pool_pre_ping=True,  # 自动重连
                echo=False,
            )
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"成功连接到数据库: {self.db_type.value}")
            return self.engine
        except Exception as e:
            logger.error(f"连接数据库失败: {str(e)}")
            raise

    def disconnect(self):
        """断开数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("已断开数据库连接")

    def get_inspector(self):
        """获取数据库检查器"""
        if not self.engine:
            self.connect()
        return inspect(self.engine)

    def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        列出所有表

        Args:
            schema: 模式名称（可选）

        Returns:
            List[str]: 表名列表
        """
        inspector = self.get_inspector()
        return inspector.get_table_names(schema=schema)

    def list_views(self, schema: Optional[str] = None) -> List[str]:
        """
        列出所有视图

        Args:
            schema: 模式名称（可选）

        Returns:
            List[str]: 视图名列表
        """
        inspector = self.get_inspector()
        return inspector.get_view_names(schema=schema)

    def list_schemas(self) -> List[str]:
        """
        列出所有模式

        Returns:
            List[str]: 模式名列表
        """
        inspector = self.get_inspector()
        return inspector.get_schema_names()

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句

        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        if not self.engine:
            self.connect()

        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_table_row_count(self, table_name: str, schema: Optional[str] = None) -> int:
        """
        获取表的行数

        Args:
            table_name: 表名
            schema: 模式名（可选）

        Returns:
            int: 行数
        """
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        query = f"SELECT COUNT(*) as count FROM {full_table_name}"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0

    def sample_table_data(
        self,
        table_name: str,
        limit: int = 100,
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        采样表数据

        Args:
            table_name: 表名
            limit: 采样数量
            schema: 模式名（可选）

        Returns:
            List[Dict[str, Any]]: 采样数据
        """
        full_table_name = f"{schema}.{table_name}" if schema else table_name

        # 不同数据库的随机采样语法不同
        if self.db_type == DatabaseType.MYSQL:
            query = f"SELECT * FROM {full_table_name} ORDER BY RAND() LIMIT {limit}"
        elif self.db_type == DatabaseType.POSTGRESQL:
            query = f"SELECT * FROM {full_table_name} ORDER BY RANDOM() LIMIT {limit}"
        elif self.db_type == DatabaseType.SQLSERVER:
            query = f"SELECT TOP {limit} * FROM {full_table_name} ORDER BY NEWID()"
        elif self.db_type == DatabaseType.ORACLE:
            query = f"SELECT * FROM (SELECT * FROM {full_table_name} ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM <= {limit}"
        else:
            # 默认使用简单的LIMIT
            query = f"SELECT * FROM {full_table_name} LIMIT {limit}"

        return self.execute_query(query)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DatabaseConnector':
        """
        从配置字典创建连接器

        Args:
            config: 配置字典

        Returns:
            DatabaseConnector: 连接器实例
        """
        db_type = DatabaseType(config['type'])
        return cls(
            db_type=db_type,
            host=config.get('host'),
            port=config.get('port'),
            database=config.get('database', ''),
            username=config.get('username'),
            password=config.get('password'),
            **config.get('options', {})
        )

    def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            bool: 连接是否成功
        """
        try:
            self.connect()
            self.disconnect()
            return True
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False
