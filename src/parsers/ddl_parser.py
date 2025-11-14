"""
DDL解析器 - 从SQL CREATE TABLE语句解析元数据
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from src.metadata.field import Field, FieldType
from src.metadata.table import Table


class DDLParser:
    """SQL DDL解析器"""

    # SQL数据类型到FieldType的映射
    TYPE_MAPPING = {
        # 整数类型
        'INT': FieldType.INTEGER,
        'INTEGER': FieldType.INTEGER,
        'TINYINT': FieldType.INTEGER,
        'SMALLINT': FieldType.INTEGER,
        'MEDIUMINT': FieldType.INTEGER,
        'BIGINT': FieldType.INTEGER,

        # 小数类型
        'DECIMAL': FieldType.DECIMAL,
        'NUMERIC': FieldType.DECIMAL,
        'FLOAT': FieldType.DECIMAL,
        'DOUBLE': FieldType.DECIMAL,
        'REAL': FieldType.DECIMAL,

        # 字符串类型
        'CHAR': FieldType.STRING,
        'VARCHAR': FieldType.STRING,
        'TEXT': FieldType.STRING,
        'TINYTEXT': FieldType.STRING,
        'MEDIUMTEXT': FieldType.STRING,
        'LONGTEXT': FieldType.STRING,
        'NCHAR': FieldType.STRING,
        'NVARCHAR': FieldType.STRING,

        # 日期时间类型
        'DATE': FieldType.DATE,
        'DATETIME': FieldType.DATETIME,
        'TIMESTAMP': FieldType.DATETIME,
        'TIME': FieldType.STRING,
        'YEAR': FieldType.INTEGER,

        # 布尔类型
        'BOOLEAN': FieldType.BOOLEAN,
        'BOOL': FieldType.BOOLEAN,
        'BIT': FieldType.BOOLEAN,

        # 枚举类型
        'ENUM': FieldType.ENUM,
        'SET': FieldType.ENUM,
    }

    def __init__(self):
        """初始化解析器"""
        pass

    def parse_ddl(self, ddl: str) -> Table:
        """
        解析DDL语句，生成Table对象

        Args:
            ddl: CREATE TABLE语句

        Returns:
            Table对象
        """
        # 清理DDL语句
        ddl = self._clean_ddl(ddl)

        # 提取表名
        table_name = self._extract_table_name(ddl)

        # 提取表注释
        table_comment = self._extract_table_comment(ddl)

        # 创建Table对象
        table = Table(
            name=table_name,
            description=table_comment or f"从DDL导入的表: {table_name}",
            primary_key=None  # 稍后设置
        )

        # 提取字段定义
        field_defs = self._extract_field_definitions(ddl)

        # 提取表级约束
        constraints = self._extract_table_constraints(ddl)

        # 解析每个字段
        primary_key = None
        for field_def in field_defs:
            field = self._parse_field_definition(field_def)
            if field:
                table.add_field(field)

                # 检查是否是主键
                if self._is_primary_key(field_def):
                    primary_key = field.name

        # 从表级约束中提取主键
        if not primary_key and 'primary_key' in constraints:
            primary_key = constraints['primary_key'][0] if constraints['primary_key'] else None

        # 设置主键
        if primary_key:
            table.primary_key = primary_key

        # 添加外键关系
        if 'foreign_keys' in constraints:
            for fk in constraints['foreign_keys']:
                table.add_foreign_key(
                    field_name=fk['field'],
                    reference_table=fk['ref_table'],
                    reference_field=fk['ref_field']
                )

        return table

    def parse_ddl_file(self, file_path: str) -> List[Table]:
        """
        解析DDL文件，可能包含多个CREATE TABLE语句

        Args:
            file_path: DDL文件路径

        Returns:
            Table对象列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分割多个CREATE TABLE语句
        statements = self._split_statements(content)

        tables = []
        for statement in statements:
            if statement.strip():
                try:
                    table = self.parse_ddl(statement)
                    tables.append(table)
                except Exception as e:
                    print(f"警告: 解析DDL语句失败: {e}")
                    continue

        return tables

    def _clean_ddl(self, ddl: str) -> str:
        """清理DDL语句"""
        # 移除单行注释
        ddl = re.sub(r'--[^\n]*', '', ddl)

        # 移除多行注释
        ddl = re.sub(r'/\*.*?\*/', '', ddl, flags=re.DOTALL)

        # 统一换行符
        ddl = ddl.replace('\r\n', '\n')

        # 移除多余空白
        ddl = ' '.join(ddl.split())

        return ddl

    def _extract_table_name(self, ddl: str) -> str:
        """提取表名"""
        # 匹配 CREATE TABLE table_name 或 CREATE TABLE IF NOT EXISTS table_name
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`)?(\w+)(?:`)?'
        match = re.search(pattern, ddl, re.IGNORECASE)

        if not match:
            raise ValueError("无法从DDL中提取表名")

        return match.group(1)

    def _extract_table_comment(self, ddl: str) -> Optional[str]:
        """提取表注释"""
        # MySQL风格: COMMENT='...'
        pattern = r"COMMENT\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, ddl, re.IGNORECASE)

        if match:
            return match.group(1)

        return None

    def _extract_field_definitions(self, ddl: str) -> List[str]:
        """提取字段定义"""
        # 提取括号内的内容
        pattern = r'CREATE\s+TABLE[^(]+\((.*)\)'
        match = re.search(pattern, ddl, re.IGNORECASE | re.DOTALL)

        if not match:
            raise ValueError("无法提取字段定义")

        fields_block = match.group(1)

        # 分割字段定义（注意要处理嵌套的括号，如ENUM）
        field_defs = []
        current_def = ""
        paren_depth = 0

        for char in fields_block:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                # 这是字段分隔符
                if current_def.strip():
                    field_defs.append(current_def.strip())
                current_def = ""
                continue

            current_def += char

        # 添加最后一个字段
        if current_def.strip():
            field_defs.append(current_def.strip())

        # 过滤掉表级约束
        field_defs = [
            f for f in field_defs
            if not re.match(r'^\s*(PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|INDEX|KEY|CONSTRAINT)', f, re.IGNORECASE)
        ]

        return field_defs

    def _extract_table_constraints(self, ddl: str) -> Dict[str, Any]:
        """提取表级约束"""
        constraints = {
            'primary_key': [],
            'foreign_keys': [],
            'unique': []
        }

        # 提取PRIMARY KEY
        pk_pattern = r'PRIMARY\s+KEY\s*\((?:`)?(\w+)(?:`)?(?:\s*,\s*(?:`)?(\w+)(?:`)?)?\)'
        pk_match = re.search(pk_pattern, ddl, re.IGNORECASE)
        if pk_match:
            constraints['primary_key'] = [g for g in pk_match.groups() if g]

        # 提取FOREIGN KEY
        fk_pattern = r'FOREIGN\s+KEY\s*\((?:`)?(\w+)(?:`)?\)\s*REFERENCES\s+(?:`)?(\w+)(?:`)?\s*\((?:`)?(\w+)(?:`)?\)'
        fk_matches = re.finditer(fk_pattern, ddl, re.IGNORECASE)
        for match in fk_matches:
            constraints['foreign_keys'].append({
                'field': match.group(1),
                'ref_table': match.group(2),
                'ref_field': match.group(3)
            })

        return constraints

    def _parse_field_definition(self, field_def: str) -> Optional[Field]:
        """解析单个字段定义"""
        # 提取字段名
        field_name_pattern = r'^(?:`)?(\w+)(?:`)?'
        field_name_match = re.match(field_name_pattern, field_def)

        if not field_name_match:
            return None

        field_name = field_name_match.group(1)

        # 提取数据类型
        data_type, type_params = self._extract_data_type(field_def)

        # 映射到FieldType
        field_type = self._map_type(data_type)

        # 提取约束
        is_required = self._is_not_null(field_def)
        is_unique = self._is_unique(field_def)
        default_value = self._extract_default(field_def)
        comment = self._extract_field_comment(field_def)

        # 创建Field对象
        field_kwargs = {
            'name': field_name,
            'field_type': field_type,
            'description': comment or f"{field_name}字段",
            'required': is_required,
            'unique': is_unique,
        }

        # 处理默认值
        if default_value is not None:
            field_kwargs['default_value'] = default_value

        # 处理特定类型的参数
        if field_type == FieldType.STRING and type_params:
            # VARCHAR(100) -> max_length=100
            if type_params.get('length'):
                field_kwargs['max_length'] = type_params['length']

        elif field_type == FieldType.DECIMAL and type_params:
            # DECIMAL(10,2) -> precision=2
            if type_params.get('scale'):
                field_kwargs['precision'] = type_params['scale']

        elif field_type == FieldType.ENUM and type_params:
            # ENUM('a','b','c') -> enum_values=['a','b','c']
            if type_params.get('enum_values'):
                field_kwargs['enum_values'] = type_params['enum_values']

        elif field_type == FieldType.INTEGER and type_params:
            # INT(11) -> 范围约束
            pass  # 可以后续添加范围约束

        return Field(**field_kwargs)

    def _extract_data_type(self, field_def: str) -> Tuple[str, Dict[str, Any]]:
        """提取数据类型和参数"""
        # 匹配类型名和括号内的参数
        pattern = r'(?:`)?(\w+)(?:`)?\s+(\w+)(?:\(([^)]+)\))?'
        match = re.match(pattern, field_def, re.IGNORECASE)

        if not match:
            return 'VARCHAR', {}

        data_type = match.group(2).upper()
        params_str = match.group(3)

        params = {}
        if params_str:
            # 处理ENUM类型: ENUM('a','b','c')
            if data_type == 'ENUM':
                enum_values = re.findall(r"['\"]([^'\"]+)['\"]", params_str)
                params['enum_values'] = enum_values

            # 处理DECIMAL类型: DECIMAL(10,2)
            elif ',' in params_str:
                parts = params_str.split(',')
                params['precision'] = int(parts[0].strip())
                params['scale'] = int(parts[1].strip())

            # 处理长度: VARCHAR(100), INT(11)
            else:
                try:
                    params['length'] = int(params_str.strip())
                except ValueError:
                    pass

        return data_type, params

    def _map_type(self, sql_type: str) -> FieldType:
        """映射SQL类型到FieldType"""
        sql_type_upper = sql_type.upper()

        return self.TYPE_MAPPING.get(sql_type_upper, FieldType.STRING)

    def _is_not_null(self, field_def: str) -> bool:
        """检查是否NOT NULL"""
        return bool(re.search(r'\bNOT\s+NULL\b', field_def, re.IGNORECASE))

    def _is_unique(self, field_def: str) -> bool:
        """检查是否UNIQUE"""
        return bool(re.search(r'\bUNIQUE\b', field_def, re.IGNORECASE))

    def _is_primary_key(self, field_def: str) -> bool:
        """检查是否PRIMARY KEY"""
        return bool(re.search(r'\bPRIMARY\s+KEY\b', field_def, re.IGNORECASE))

    def _extract_default(self, field_def: str) -> Optional[Any]:
        """提取默认值"""
        pattern = r"DEFAULT\s+(['\"]?)([^,'\"\s]+)\1"
        match = re.search(pattern, field_def, re.IGNORECASE)

        if match:
            value = match.group(2)

            # 处理特殊值
            if value.upper() in ('NULL', 'CURRENT_TIMESTAMP', 'NOW()'):
                return None

            # 尝试转换为数字
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return value

        return None

    def _extract_field_comment(self, field_def: str) -> Optional[str]:
        """提取字段注释"""
        pattern = r"COMMENT\s+['\"]([^'\"]+)['\"]"
        match = re.search(pattern, field_def, re.IGNORECASE)

        if match:
            return match.group(1)

        return None

    def _split_statements(self, content: str) -> List[str]:
        """分割多个SQL语句"""
        # 简单实现：按分号分割
        statements = []
        current = ""

        for line in content.split('\n'):
            line = line.strip()

            # 跳过注释行
            if line.startswith('--') or line.startswith('#'):
                continue

            current += ' ' + line

            # 检查是否结束
            if line.endswith(';'):
                statements.append(current.strip())
                current = ""

        # 添加最后一个语句
        if current.strip():
            statements.append(current.strip())

        # 只保留CREATE TABLE语句
        statements = [
            s for s in statements
            if re.match(r'^\s*CREATE\s+TABLE', s, re.IGNORECASE)
        ]

        return statements


def parse_ddl_to_table(ddl: str) -> Table:
    """
    便捷函数：从DDL字符串解析Table对象

    Args:
        ddl: CREATE TABLE语句

    Returns:
        Table对象
    """
    parser = DDLParser()
    return parser.parse_ddl(ddl)


def parse_ddl_file_to_tables(file_path: str) -> List[Table]:
    """
    便捷函数：从DDL文件解析多个Table对象

    Args:
        file_path: DDL文件路径

    Returns:
        Table对象列表
    """
    parser = DDLParser()
    return parser.parse_ddl_file(file_path)
