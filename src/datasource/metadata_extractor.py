"""
元数据提取器
从数据库schema中提取表结构并转换为系统的元数据格式
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import inspect
import logging

from .db_connector import DatabaseConnector
from ..metadata.table import Table
from ..metadata.field import Field, FieldType

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    元数据提取器
    从数据库中提取表结构信息
    """

    # SQLAlchemy类型到系统字段类型的映射
    TYPE_MAPPING = {
        'INTEGER': FieldType.INTEGER,
        'BIGINT': FieldType.INTEGER,
        'SMALLINT': FieldType.INTEGER,
        'TINYINT': FieldType.INTEGER,
        'INT': FieldType.INTEGER,
        'DECIMAL': FieldType.DECIMAL,
        'NUMERIC': FieldType.DECIMAL,
        'FLOAT': FieldType.DECIMAL,
        'DOUBLE': FieldType.DECIMAL,
        'REAL': FieldType.DECIMAL,
        'VARCHAR': FieldType.STRING,
        'CHAR': FieldType.STRING,
        'TEXT': FieldType.STRING,
        'LONGTEXT': FieldType.STRING,
        'MEDIUMTEXT': FieldType.STRING,
        'DATE': FieldType.DATE,
        'DATETIME': FieldType.DATETIME,
        'TIMESTAMP': FieldType.DATETIME,
        'TIME': FieldType.STRING,
        'BOOLEAN': FieldType.BOOLEAN,
        'BOOL': FieldType.BOOLEAN,
        'TINYINT(1)': FieldType.BOOLEAN,
        'ENUM': FieldType.ENUM,
    }

    def __init__(self, connector: DatabaseConnector):
        """
        初始化元数据提取器

        Args:
            connector: 数据库连接器
        """
        self.connector = connector
        self.inspector = connector.get_inspector()

    def extract_table(
        self,
        table_name: str,
        schema: Optional[str] = None,
        include_sample_data: bool = False
    ) -> Table:
        """
        提取表结构

        Args:
            table_name: 表名
            schema: 模式名（可选）
            include_sample_data: 是否包含样本数据用于分析

        Returns:
            Table: 表定义对象
        """
        logger.info(f"开始提取表结构: {table_name}")

        # 创建表对象
        table = Table(
            name=table_name,
            description=f"从数据库提取的表: {table_name}",
        )

        # 提取列信息
        columns = self.inspector.get_columns(table_name, schema=schema)
        for col in columns:
            field = self._column_to_field(col)
            table.add_field(field)

        # 提取主键
        pk_constraint = self.inspector.get_pk_constraint(table_name, schema=schema)
        if pk_constraint and pk_constraint.get('constrained_columns'):
            table.primary_key = pk_constraint['constrained_columns'][0]

        # 提取索引
        indexes = self.inspector.get_indexes(table_name, schema=schema)
        for idx in indexes:
            if idx.get('column_names'):
                table.indexes.extend(idx['column_names'])

        # 提取外键
        foreign_keys = self.inspector.get_foreign_keys(table_name, schema=schema)
        for fk in foreign_keys:
            if fk.get('constrained_columns') and fk.get('referred_table'):
                for col_name in fk['constrained_columns']:
                    field = table.get_field(col_name)
                    if field:
                        field.reference_table = fk['referred_table']
                        if fk.get('referred_columns'):
                            field.reference_field = fk['referred_columns'][0]

        logger.info(f"成功提取表结构: {table_name}, 字段数: {len(table.fields)}")
        return table

    def _column_to_field(self, column: Dict[str, Any]) -> Field:
        """
        将数据库列信息转换为字段对象

        Args:
            column: 列信息字典

        Returns:
            Field: 字段对象
        """
        col_name = column['name']
        col_type = str(column['type']).upper()

        # 提取基础类型名（去除长度等信息）
        base_type = col_type.split('(')[0]

        # 映射到系统字段类型
        field_type = self.TYPE_MAPPING.get(base_type, FieldType.STRING)

        # 提取长度信息
        length = None
        max_length = None
        precision = None

        if 'VARCHAR' in col_type or 'CHAR' in col_type:
            # 提取字符串长度
            if '(' in col_type:
                try:
                    length_str = col_type.split('(')[1].split(')')[0]
                    max_length = int(length_str)
                except:
                    pass

        if 'DECIMAL' in col_type or 'NUMERIC' in col_type:
            # 提取小数精度
            if '(' in col_type:
                try:
                    parts = col_type.split('(')[1].split(')')[0].split(',')
                    if len(parts) == 2:
                        precision = int(parts[1].strip())
                except:
                    pass

        # 检测是否为金额字段
        if 'amount' in col_name.lower() or 'price' in col_name.lower() or 'balance' in col_name.lower():
            field_type = FieldType.AMOUNT

        # 检测是否为邮箱字段
        if 'email' in col_name.lower():
            field_type = FieldType.EMAIL

        # 检测是否为电话字段
        if 'phone' in col_name.lower() or 'mobile' in col_name.lower() or 'tel' in col_name.lower():
            field_type = FieldType.PHONE

        # 检测是否为身份证字段
        if 'id_card' in col_name.lower() or 'idcard' in col_name.lower():
            field_type = FieldType.ID_CARD

        # 检测是否为银行卡字段
        if 'card_no' in col_name.lower() or 'account_no' in col_name.lower():
            field_type = FieldType.BANK_CARD

        # 创建字段对象
        field = Field(
            name=col_name,
            field_type=field_type,
            description=column.get('comment', ''),
            required=not column.get('nullable', True),
            length=length,
            max_length=max_length,
            precision=precision,
        )

        return field

    def extract_multiple_tables(
        self,
        table_names: List[str],
        schema: Optional[str] = None
    ) -> List[Table]:
        """
        批量提取多个表的结构

        Args:
            table_names: 表名列表
            schema: 模式名（可选）

        Returns:
            List[Table]: 表定义列表
        """
        tables = []
        for table_name in table_names:
            try:
                table = self.extract_table(table_name, schema)
                tables.append(table)
            except Exception as e:
                logger.error(f"提取表 {table_name} 失败: {str(e)}")

        return tables

    def extract_all_tables(self, schema: Optional[str] = None) -> List[Table]:
        """
        提取所有表的结构

        Args:
            schema: 模式名（可选）

        Returns:
            List[Table]: 表定义列表
        """
        table_names = self.connector.list_tables(schema)
        return self.extract_multiple_tables(table_names, schema)

    def get_table_statistics(
        self,
        table_name: str,
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取表的统计信息

        Args:
            table_name: 表名
            schema: 模式名（可选）

        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'table_name': table_name,
            'row_count': 0,
            'column_count': 0,
            'has_primary_key': False,
            'index_count': 0,
            'foreign_key_count': 0,
        }

        try:
            # 行数
            stats['row_count'] = self.connector.get_table_row_count(table_name, schema)

            # 列数
            columns = self.inspector.get_columns(table_name, schema=schema)
            stats['column_count'] = len(columns)

            # 主键
            pk_constraint = self.inspector.get_pk_constraint(table_name, schema=schema)
            stats['has_primary_key'] = bool(pk_constraint.get('constrained_columns'))

            # 索引数
            indexes = self.inspector.get_indexes(table_name, schema=schema)
            stats['index_count'] = len(indexes)

            # 外键数
            foreign_keys = self.inspector.get_foreign_keys(table_name, schema=schema)
            stats['foreign_key_count'] = len(foreign_keys)

        except Exception as e:
            logger.error(f"获取表统计信息失败: {str(e)}")

        return stats
