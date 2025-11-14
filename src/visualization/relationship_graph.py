"""
数据关系图生成器
分析表之间的关系并生成可视化数据
"""

from typing import List, Dict, Any, Optional, Set
from ..metadata.table import Table
from ..metadata.field import Field


class RelationshipGraphGenerator:
    """
    数据关系图生成器
    分析表之间的外键关系，生成适用于可视化的图数据结构
    """

    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Dict[str, Any]] = []

    def add_table(self, table: Table):
        """添加表定义"""
        self.tables[table.name] = table

    def add_tables(self, tables: List[Table]):
        """批量添加表定义"""
        for table in tables:
            self.add_table(table)

    def analyze_relationships(self):
        """
        分析表之间的关系
        基于字段的reference_table和reference_field识别外键关系
        """
        self.relationships = []

        for table_name, table in self.tables.items():
            for field in table.fields:
                if field.reference_table and field.reference_field:
                    # 确保引用的表存在
                    if field.reference_table in self.tables:
                        relationship = {
                            'source': table_name,
                            'target': field.reference_table,
                            'source_field': field.name,
                            'target_field': field.reference_field,
                            'type': 'foreign_key'
                        }
                        self.relationships.append(relationship)

    def generate_graph_data(self) -> Dict[str, Any]:
        """
        生成图数据结构

        Returns:
            包含nodes和links的字典，适用于D3.js等可视化库
        """
        self.analyze_relationships()

        # 生成节点
        nodes = []
        for table_name, table in self.tables.items():
            node = {
                'id': table_name,
                'name': table_name,
                'description': table.description or '',
                'fields': [
                    {
                        'name': field.name,
                        'type': field.field_type.value,
                        'required': field.required,
                        'unique': field.unique,
                        'primary_key': field.name == table.primary_key
                    }
                    for field in table.fields
                ],
                'field_count': len(table.fields),
                'primary_key': table.primary_key
            }
            nodes.append(node)

        # 生成边（关系）
        links = []
        for rel in self.relationships:
            link = {
                'source': rel['source'],
                'target': rel['target'],
                'source_field': rel['source_field'],
                'target_field': rel['target_field'],
                'type': rel['type'],
                'label': f"{rel['source_field']} → {rel['target_field']}"
            }
            links.append(link)

        return {
            'nodes': nodes,
            'links': links,
            'metadata': {
                'table_count': len(nodes),
                'relationship_count': len(links)
            }
        }

    def get_table_dependencies(self, table_name: str) -> Dict[str, Any]:
        """
        获取特定表的依赖关系

        Args:
            table_name: 表名

        Returns:
            包含依赖表和被依赖表的字典
        """
        if table_name not in self.tables:
            return {'dependencies': [], 'dependents': []}

        self.analyze_relationships()

        # 该表依赖的表（外键指向的表）
        dependencies = []
        for rel in self.relationships:
            if rel['source'] == table_name:
                dependencies.append({
                    'table': rel['target'],
                    'via_field': rel['source_field'],
                    'target_field': rel['target_field']
                })

        # 依赖该表的表（外键指向该表的其他表）
        dependents = []
        for rel in self.relationships:
            if rel['target'] == table_name:
                dependents.append({
                    'table': rel['source'],
                    'via_field': rel['source_field'],
                    'target_field': rel['target_field']
                })

        return {
            'table': table_name,
            'dependencies': dependencies,
            'dependents': dependents,
            'dependency_count': len(dependencies),
            'dependent_count': len(dependents)
        }

    def get_relationship_matrix(self) -> List[List[int]]:
        """
        生成关系矩阵
        用于热力图等可视化

        Returns:
            二维矩阵，表示表之间的关系强度
        """
        self.analyze_relationships()

        table_names = sorted(self.tables.keys())
        n = len(table_names)
        matrix = [[0] * n for _ in range(n)]

        # 创建表名到索引的映射
        table_index = {name: i for i, name in enumerate(table_names)}

        # 填充矩阵
        for rel in self.relationships:
            source_idx = table_index[rel['source']]
            target_idx = table_index[rel['target']]
            matrix[source_idx][target_idx] += 1

        return matrix

    def get_connected_components(self) -> List[Set[str]]:
        """
        获取连通分量
        识别相互关联的表组

        Returns:
            表组列表，每个组包含相互关联的表
        """
        self.analyze_relationships()

        # 构建邻接表
        adjacency = {table_name: set() for table_name in self.tables.keys()}

        for rel in self.relationships:
            adjacency[rel['source']].add(rel['target'])
            adjacency[rel['target']].add(rel['source'])

        # DFS查找连通分量
        visited = set()
        components = []

        def dfs(node: str, component: Set[str]):
            visited.add(node)
            component.add(node)
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        for table_name in self.tables.keys():
            if table_name not in visited:
                component = set()
                dfs(table_name, component)
                components.append(component)

        return components

    def generate_hierarchy(self, root_table: Optional[str] = None) -> Dict[str, Any]:
        """
        生成层次结构数据
        适用于树状图可视化

        Args:
            root_table: 根表名，如果为None则选择没有依赖的表

        Returns:
            树状结构数据
        """
        self.analyze_relationships()

        # 如果没有指定根表，选择没有依赖的表
        if root_table is None:
            for table_name in self.tables.keys():
                has_dependency = any(
                    rel['source'] == table_name for rel in self.relationships
                )
                if not has_dependency:
                    root_table = table_name
                    break

            # 如果所有表都有依赖，选择第一个表
            if root_table is None and self.tables:
                root_table = next(iter(self.tables.keys()))

        if root_table is None or root_table not in self.tables:
            return {}

        # 构建树
        visited = set()

        def build_tree(table_name: str) -> Dict[str, Any]:
            if table_name in visited:
                return None

            visited.add(table_name)

            table = self.tables[table_name]
            node = {
                'name': table_name,
                'description': table.description or '',
                'field_count': len(table.fields),
                'children': []
            }

            # 找到依赖该表的表
            for rel in self.relationships:
                if rel['target'] == table_name and rel['source'] not in visited:
                    child = build_tree(rel['source'])
                    if child:
                        node['children'].append(child)

            return node

        return build_tree(root_table)

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取关系图统计信息

        Returns:
            统计信息字典
        """
        self.analyze_relationships()

        # 计算每个表的度数
        in_degree = {table: 0 for table in self.tables.keys()}
        out_degree = {table: 0 for table in self.tables.keys()}

        for rel in self.relationships:
            out_degree[rel['source']] += 1
            in_degree[rel['target']] += 1

        # 找到最重要的表（度数最高）
        total_degree = {
            table: in_degree[table] + out_degree[table]
            for table in self.tables.keys()
        }

        most_connected = max(total_degree.items(), key=lambda x: x[1])[0] if total_degree else None

        # 找到根表（没有依赖的表）
        root_tables = [
            table for table in self.tables.keys()
            if out_degree[table] == 0
        ]

        # 找到叶子表（没有被依赖的表）
        leaf_tables = [
            table for table in self.tables.keys()
            if in_degree[table] == 0
        ]

        return {
            'table_count': len(self.tables),
            'relationship_count': len(self.relationships),
            'most_connected_table': most_connected,
            'root_tables': root_tables,
            'leaf_tables': leaf_tables,
            'connected_components': len(self.get_connected_components()),
            'in_degree': in_degree,
            'out_degree': out_degree
        }
