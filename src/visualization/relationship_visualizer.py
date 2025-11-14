"""
关系可视化器
生成表关系的ER图（支持Graphviz和Mermaid格式）
"""

from typing import List, Dict, Optional
from enum import Enum
from ..metadata.table import Table
from ..metadata.field import FieldType
from ..analysis.dependency_analyzer import DependencyAnalyzer, DependencyGraph


class VisualizationFormat(Enum):
    """可视化输出格式"""
    GRAPHVIZ_DOT = "dot"  # Graphviz DOT格式
    MERMAID = "mermaid"    # Mermaid格式
    PLANTUML = "plantuml"  # PlantUML格式


class RelationshipVisualizer:
    """
    关系可视化器
    生成表关系的ER图
    """

    def __init__(self, tables: List[Table]):
        """
        初始化可视化器

        Args:
            tables: 表定义列表
        """
        self.tables = {table.name: table for table in tables}
        self.analyzer = DependencyAnalyzer(tables)

    def generate_dot(self, output_file: Optional[str] = None,
                    show_fields: bool = True,
                    show_field_types: bool = True,
                    highlight_keys: bool = True) -> str:
        """
        生成Graphviz DOT格式的ER图

        Args:
            output_file: 输出文件路径（如果提供则写入文件）
            show_fields: 是否显示字段
            show_field_types: 是否显示字段类型
            highlight_keys: 是否高亮主键和外键

        Returns:
            str: DOT格式的字符串
        """
        lines = []
        lines.append('digraph ER {')
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=record, fontname="Arial"];')
        lines.append('  edge [fontname="Arial", fontsize=10];')
        lines.append('')

        # 生成表节点
        for table_name, table in sorted(self.tables.items()):
            lines.append(f'  // Table: {table_name}')
            node_label = self._generate_dot_table_label(
                table, show_fields, show_field_types, highlight_keys
            )
            lines.append(f'  {self._sanitize_name(table_name)} [label="{node_label}"];')
            lines.append('')

        # 生成关系边
        lines.append('  // Relationships')
        for edge in self.analyzer.graph.edges:
            from_node = self._sanitize_name(edge.from_table)
            to_node = self._sanitize_name(edge.to_table)
            label = f"{edge.field_name}"
            lines.append(f'  {from_node} -> {to_node} '
                        f'[label="{label}", arrowhead=crow];')

        lines.append('}')

        dot_content = '\n'.join(lines)

        # 写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(dot_content)

        return dot_content

    def generate_mermaid(self, output_file: Optional[str] = None,
                        show_fields: bool = True,
                        show_field_types: bool = True) -> str:
        """
        生成Mermaid格式的ER图

        Args:
            output_file: 输出文件路径（如果提供则写入文件）
            show_fields: 是否显示字段
            show_field_types: 是否显示字段类型

        Returns:
            str: Mermaid格式的字符串
        """
        lines = []
        lines.append('erDiagram')
        lines.append('')

        # 生成表定义
        for table_name, table in sorted(self.tables.items()):
            lines.append(f'  {table_name} {{')

            if show_fields:
                for field in table.fields:
                    field_line = self._generate_mermaid_field_line(
                        field, show_field_types
                    )
                    lines.append(f'    {field_line}')

            lines.append('  }')
            lines.append('')

        # 生成关系
        for edge in self.analyzer.graph.edges:
            # Mermaid关系语法: TableA ||--o{ TableB : "relationship"
            # ||--o{ 表示一对多关系
            lines.append(f'  {edge.to_table} ||--o{{ {edge.from_table} : "{edge.field_name}"')

        mermaid_content = '\n'.join(lines)

        # 写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_content)

        return mermaid_content

    def generate_plantuml(self, output_file: Optional[str] = None,
                         show_fields: bool = True,
                         show_field_types: bool = True) -> str:
        """
        生成PlantUML格式的ER图

        Args:
            output_file: 输出文件路径（如果提供则写入文件）
            show_fields: 是否显示字段
            show_field_types: 是否显示字段类型

        Returns:
            str: PlantUML格式的字符串
        """
        lines = []
        lines.append('@startuml')
        lines.append('')

        # 设置样式
        lines.append('skinparam linetype ortho')
        lines.append('skinparam class {')
        lines.append('  BackgroundColor White')
        lines.append('  BorderColor Black')
        lines.append('  ArrowColor Black')
        lines.append('}')
        lines.append('')

        # 生成表定义
        for table_name, table in sorted(self.tables.items()):
            lines.append(f'entity {table_name} {{')

            # 主键
            primary_key_field = table.get_field(table.primary_key)
            if primary_key_field:
                field_type = self._get_plantuml_type(primary_key_field.field_type)
                lines.append(f'  * {primary_key_field.name} : {field_type} <<PK>>')

            # 其他字段
            if show_fields:
                for field in table.fields:
                    if field.name == table.primary_key:
                        continue

                    field_type = self._get_plantuml_type(field.field_type) if show_field_types else ""
                    required = "*" if field.required else " "
                    fk_marker = " <<FK>>" if field.reference_table else ""

                    lines.append(f'  {required} {field.name} : {field_type}{fk_marker}')

            lines.append('}')
            lines.append('')

        # 生成关系
        for edge in self.analyzer.graph.edges:
            # PlantUML关系语法: TableA ||--o{ TableB
            lines.append(f'{edge.to_table} ||--o{{ {edge.from_table}')

        lines.append('@enduml')

        plantuml_content = '\n'.join(lines)

        # 写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(plantuml_content)

        return plantuml_content

    def generate(self, format: VisualizationFormat,
                output_file: Optional[str] = None,
                **kwargs) -> str:
        """
        生成可视化图表

        Args:
            format: 输出格式
            output_file: 输出文件路径
            **kwargs: 格式特定的参数

        Returns:
            str: 生成的图表内容
        """
        if format == VisualizationFormat.GRAPHVIZ_DOT:
            return self.generate_dot(output_file, **kwargs)
        elif format == VisualizationFormat.MERMAID:
            return self.generate_mermaid(output_file, **kwargs)
        elif format == VisualizationFormat.PLANTUML:
            return self.generate_plantuml(output_file, **kwargs)
        else:
            raise ValueError(f"不支持的可视化格式: {format}")

    def render_dot_to_image(self, dot_content: str, output_file: str,
                           format: str = 'png'):
        """
        将DOT格式渲染为图片（需要安装Graphviz）

        Args:
            dot_content: DOT格式内容
            output_file: 输出文件路径
            format: 输出格式（png, svg, pdf等）

        Raises:
            ImportError: 如果未安装graphviz库
            Exception: 如果渲染失败
        """
        try:
            import graphviz
        except ImportError:
            raise ImportError(
                "需要安装graphviz库: pip install graphviz\n"
                "并确保系统已安装Graphviz: https://graphviz.org/download/"
            )

        try:
            # 创建Source对象并渲染
            source = graphviz.Source(dot_content)
            source.render(output_file, format=format, cleanup=True)
        except Exception as e:
            raise Exception(f"渲染图片失败: {e}")

    def _generate_dot_table_label(self, table: Table, show_fields: bool,
                                  show_field_types: bool, highlight_keys: bool) -> str:
        """生成DOT格式的表标签"""
        parts = []

        # 表名
        parts.append(f'{{<table>表名: {table.name}|{table.description or ""}}}')

        if show_fields:
            # 字段列表
            field_lines = []
            for field in table.fields:
                field_str = self._format_dot_field(field, show_field_types, highlight_keys, table.primary_key)
                field_lines.append(field_str)

            fields_str = '\\l'.join(field_lines) + '\\l'
            parts.append(f'{{{fields_str}}}')

        return '|'.join(parts)

    def _format_dot_field(self, field, show_field_types: bool,
                         highlight_keys: bool, primary_key: str) -> str:
        """格式化DOT格式的字段"""
        field_str = field.name

        # 主键标记
        if highlight_keys and field.name == primary_key:
            field_str = f'🔑 {field_str}'
        # 外键标记
        elif highlight_keys and field.reference_table:
            field_str = f'🔗 {field_str}'

        # 字段类型
        if show_field_types:
            field_type = self._get_field_type_display(field.field_type)
            field_str += f': {field_type}'

        # 必填标记
        if field.required:
            field_str += ' *'

        return field_str

    def _generate_mermaid_field_line(self, field, show_field_types: bool) -> str:
        """生成Mermaid格式的字段行"""
        field_type = self._get_field_type_display(field.field_type) if show_field_types else "string"

        # 主键标记
        key_marker = "PK" if field.unique and field.required else ""
        # 外键标记
        if field.reference_table:
            key_marker = "FK" if not key_marker else f"{key_marker},FK"

        if key_marker:
            return f'{field_type} {field.name} {key_marker}'
        else:
            return f'{field_type} {field.name}'

    def _get_field_type_display(self, field_type: FieldType) -> str:
        """获取字段类型的显示名称"""
        type_map = {
            FieldType.STRING: 'string',
            FieldType.INTEGER: 'int',
            FieldType.DECIMAL: 'decimal',
            FieldType.DATE: 'date',
            FieldType.DATETIME: 'datetime',
            FieldType.BOOLEAN: 'boolean',
            FieldType.ENUM: 'enum',
            FieldType.ID: 'id',
            FieldType.PHONE: 'phone',
            FieldType.EMAIL: 'email',
            FieldType.ID_CARD: 'id_card',
            FieldType.BANK_CARD: 'bank_card',
            FieldType.AMOUNT: 'amount',
        }
        return type_map.get(field_type, 'unknown')

    def _get_plantuml_type(self, field_type: FieldType) -> str:
        """获取PlantUML的类型名称"""
        type_map = {
            FieldType.STRING: 'VARCHAR',
            FieldType.INTEGER: 'INT',
            FieldType.DECIMAL: 'DECIMAL',
            FieldType.DATE: 'DATE',
            FieldType.DATETIME: 'DATETIME',
            FieldType.BOOLEAN: 'BOOLEAN',
            FieldType.ENUM: 'ENUM',
            FieldType.ID: 'VARCHAR',
            FieldType.PHONE: 'VARCHAR',
            FieldType.EMAIL: 'VARCHAR',
            FieldType.ID_CARD: 'VARCHAR',
            FieldType.BANK_CARD: 'VARCHAR',
            FieldType.AMOUNT: 'DECIMAL',
        }
        return type_map.get(field_type, 'VARCHAR')

    def _sanitize_name(self, name: str) -> str:
        """清理名称以用于DOT格式"""
        # 替换特殊字符
        return name.replace('-', '_').replace(' ', '_')

    def generate_dependency_diagram(self, output_file: Optional[str] = None,
                                   format: VisualizationFormat = VisualizationFormat.MERMAID) -> str:
        """
        生成简化的依赖关系图（仅显示表名和依赖关系，不显示字段）

        Args:
            output_file: 输出文件路径
            format: 输出格式

        Returns:
            str: 生成的图表内容
        """
        if format == VisualizationFormat.MERMAID:
            lines = []
            lines.append('graph LR')
            lines.append('')

            # 生成节点
            for table_name in sorted(self.tables.keys()):
                lines.append(f'  {table_name}["{table_name}"]')

            lines.append('')

            # 生成边
            for edge in self.analyzer.graph.edges:
                lines.append(f'  {edge.from_table} -->|{edge.field_name}| {edge.to_table}')

            content = '\n'.join(lines)

        elif format == VisualizationFormat.GRAPHVIZ_DOT:
            lines = []
            lines.append('digraph Dependencies {')
            lines.append('  rankdir=LR;')
            lines.append('  node [shape=box, style=rounded];')
            lines.append('')

            # 生成边（节点会自动创建）
            for edge in self.analyzer.graph.edges:
                from_node = self._sanitize_name(edge.from_table)
                to_node = self._sanitize_name(edge.to_table)
                lines.append(f'  {from_node} -> {to_node} [label="{edge.field_name}"];')

            lines.append('}')
            content = '\n'.join(lines)

        else:
            raise ValueError(f"依赖关系图不支持格式: {format}")

        # 写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

        return content
