"""
表依赖关系分析器
分析表之间的外键依赖关系，检测循环依赖，生成拓扑排序
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass
from ..metadata.table import Table
from ..metadata.field import Field


@dataclass
class DependencyEdge:
    """依赖关系边"""
    from_table: str  # 依赖方（子表）
    to_table: str    # 被依赖方（父表）
    field_name: str  # 外键字段名
    reference_field: str  # 引用字段名

    def __str__(self):
        return f"{self.from_table}.{self.field_name} -> {self.to_table}.{self.reference_field}"


@dataclass
class CyclicDependency:
    """循环依赖"""
    cycle: List[str]  # 形成循环的表列表

    def __str__(self):
        cycle_str = " -> ".join(self.cycle + [self.cycle[0]])
        return f"循环依赖: {cycle_str}"


class DependencyGraph:
    """
    依赖关系图
    用于表示表之间的依赖关系
    """

    def __init__(self):
        """初始化依赖关系图"""
        self.edges: List[DependencyEdge] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)  # 邻接表：table -> [dependent_tables]
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)  # 反向邻接表：table -> [dependency_tables]
        self.tables: Set[str] = set()

    def add_edge(self, edge: DependencyEdge):
        """添加依赖关系边"""
        self.edges.append(edge)
        self.adjacency[edge.to_table].append(edge.from_table)
        self.reverse_adjacency[edge.from_table].append(edge.to_table)
        self.tables.add(edge.from_table)
        self.tables.add(edge.to_table)

    def get_dependencies(self, table_name: str) -> List[str]:
        """
        获取指定表的所有依赖（父表）

        Args:
            table_name: 表名

        Returns:
            List[str]: 依赖的表列表
        """
        return self.reverse_adjacency.get(table_name, [])

    def get_dependents(self, table_name: str) -> List[str]:
        """
        获取依赖指定表的所有表（子表）

        Args:
            table_name: 表名

        Returns:
            List[str]: 依赖该表的表列表
        """
        return self.adjacency.get(table_name, [])

    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        return sorted(self.tables)

    def get_edges_for_table(self, table_name: str) -> List[DependencyEdge]:
        """
        获取与指定表相关的所有边

        Args:
            table_name: 表名

        Returns:
            List[DependencyEdge]: 相关的依赖关系边
        """
        return [edge for edge in self.edges
                if edge.from_table == table_name or edge.to_table == table_name]

    def is_empty(self) -> bool:
        """判断图是否为空"""
        return len(self.tables) == 0

    def __str__(self):
        lines = ["依赖关系图:"]
        lines.append(f"  表数量: {len(self.tables)}")
        lines.append(f"  依赖关系数: {len(self.edges)}")
        lines.append("\n依赖关系详情:")
        for edge in sorted(self.edges, key=lambda e: (e.from_table, e.to_table)):
            lines.append(f"  {edge}")
        return "\n".join(lines)


class DependencyAnalyzer:
    """
    表依赖关系分析器
    分析表之间的依赖关系，提供拓扑排序、循环检测等功能
    """

    def __init__(self, tables: List[Table]):
        """
        初始化分析器

        Args:
            tables: 表定义列表
        """
        self.tables = {table.name: table for table in tables}
        self.graph = self._build_dependency_graph()

    def _build_dependency_graph(self) -> DependencyGraph:
        """
        构建依赖关系图

        Returns:
            DependencyGraph: 依赖关系图
        """
        graph = DependencyGraph()

        # 首先确保所有表都在图中
        for table_name in self.tables.keys():
            graph.tables.add(table_name)

        # 然后添加依赖关系边
        for table_name, table in self.tables.items():
            # 查找所有外键字段
            for field in table.fields:
                if field.reference_table:
                    # 创建依赖关系边
                    edge = DependencyEdge(
                        from_table=table_name,
                        to_table=field.reference_table,
                        field_name=field.name,
                        reference_field=field.reference_field or 'id'
                    )
                    graph.add_edge(edge)

        return graph

    def detect_cycles(self) -> List[CyclicDependency]:
        """
        检测循环依赖

        Returns:
            List[CyclicDependency]: 检测到的循环依赖列表
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            """深度优先搜索检测循环"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # 遍历所有依赖
            for dependent in self.graph.reverse_adjacency.get(node, []):
                if dependent not in visited:
                    if dfs(dependent):
                        return True
                elif dependent in rec_stack:
                    # 找到循环
                    cycle_start = path.index(dependent)
                    cycle = path[cycle_start:] + [dependent]
                    cycles.append(CyclicDependency(cycle=cycle))
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        # 对所有节点执行DFS
        for table in self.graph.get_all_tables():
            if table not in visited:
                dfs(table)

        return cycles

    def topological_sort(self) -> Tuple[List[str], bool]:
        """
        拓扑排序
        返回生成数据的推荐顺序（父表在前，子表在后）

        Returns:
            Tuple[List[str], bool]: (排序后的表列表, 是否成功)
        """
        # 检测循环依赖
        cycles = self.detect_cycles()
        if cycles:
            # 有循环依赖，无法完成拓扑排序
            return [], False

        # 使用Kahn算法进行拓扑排序
        in_degree = defaultdict(int)

        # 计算每个节点的入度
        for table in self.graph.get_all_tables():
            in_degree[table] = len(self.graph.get_dependencies(table))

        # 将入度为0的节点加入队列
        queue = deque([table for table in self.graph.get_all_tables()
                      if in_degree[table] == 0])
        result = []

        while queue:
            # 取出入度为0的节点
            node = queue.popleft()
            result.append(node)

            # 减少依赖该节点的节点的入度
            for dependent in self.graph.get_dependents(node):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # 如果所有节点都被处理，则排序成功
        success = len(result) == len(self.graph.get_all_tables())
        return result, success

    def get_generation_order(self) -> List[str]:
        """
        获取推荐的数据生成顺序

        Returns:
            List[str]: 按依赖关系排序的表名列表

        Raises:
            ValueError: 如果存在循环依赖
        """
        order, success = self.topological_sort()
        if not success:
            cycles = self.detect_cycles()
            cycle_strs = "\n".join(str(cycle) for cycle in cycles)
            raise ValueError(f"存在循环依赖，无法确定生成顺序:\n{cycle_strs}")
        return order

    def get_dependency_levels(self) -> Dict[str, int]:
        """
        获取每个表的依赖层级
        层级0表示没有依赖，层级N表示依赖于层级N-1的表

        Returns:
            Dict[str, int]: 表名到层级的映射
        """
        levels = {}

        # 获取拓扑排序
        order, success = self.topological_sort()
        if not success:
            raise ValueError("存在循环依赖，无法计算依赖层级")

        # 计算每个表的层级
        for table in order:
            dependencies = self.graph.get_dependencies(table)
            if not dependencies:
                # 没有依赖，层级为0
                levels[table] = 0
            else:
                # 层级为所有依赖的最大层级 + 1
                max_dep_level = max(levels[dep] for dep in dependencies)
                levels[table] = max_dep_level + 1

        return levels

    def get_root_tables(self) -> List[str]:
        """
        获取根表（没有依赖其他表的表）

        Returns:
            List[str]: 根表列表
        """
        return [table for table in self.graph.get_all_tables()
                if not self.graph.get_dependencies(table)]

    def get_leaf_tables(self) -> List[str]:
        """
        获取叶子表（没有其他表依赖的表）

        Returns:
            List[str]: 叶子表列表
        """
        return [table for table in self.graph.get_all_tables()
                if not self.graph.get_dependents(table)]

    def get_dependency_chain(self, table_name: str) -> List[str]:
        """
        获取指定表的完整依赖链（从根表到目标表）

        Args:
            table_name: 表名

        Returns:
            List[str]: 依赖链中的表列表
        """
        if table_name not in self.tables:
            raise ValueError(f"表 {table_name} 不存在")

        chain = []
        visited = set()

        def dfs(node: str):
            """深度优先搜索收集依赖链"""
            if node in visited:
                return
            visited.add(node)

            # 先处理依赖
            for dep in self.graph.get_dependencies(node):
                dfs(dep)

            # 再添加当前节点
            chain.append(node)

        dfs(table_name)
        return chain

    def analyze_table(self, table_name: str) -> Dict:
        """
        分析单个表的依赖关系

        Args:
            table_name: 表名

        Returns:
            Dict: 包含分析结果的字典
        """
        if table_name not in self.tables:
            raise ValueError(f"表 {table_name} 不存在")

        levels = self.get_dependency_levels()

        return {
            'table_name': table_name,
            'dependencies': self.graph.get_dependencies(table_name),
            'dependents': self.graph.get_dependents(table_name),
            'dependency_level': levels.get(table_name, 0),
            'is_root': table_name in self.get_root_tables(),
            'is_leaf': table_name in self.get_leaf_tables(),
            'dependency_chain': self.get_dependency_chain(table_name),
            'related_edges': self.graph.get_edges_for_table(table_name),
        }

    def generate_report(self) -> str:
        """
        生成依赖关系分析报告

        Returns:
            str: 格式化的报告文本
        """
        lines = ["=" * 60]
        lines.append("表依赖关系分析报告")
        lines.append("=" * 60)

        # 基本统计
        lines.append(f"\n表总数: {len(self.tables)}")
        lines.append(f"依赖关系数: {len(self.graph.edges)}")

        # 检测循环依赖
        cycles = self.detect_cycles()
        if cycles:
            lines.append(f"\n⚠️  警告: 检测到 {len(cycles)} 个循环依赖:")
            for i, cycle in enumerate(cycles, 1):
                lines.append(f"  {i}. {cycle}")
        else:
            lines.append("\n✅ 未检测到循环依赖")

        # 拓扑排序
        order, success = self.topological_sort()
        if success:
            lines.append(f"\n推荐的数据生成顺序:")
            for i, table in enumerate(order, 1):
                lines.append(f"  {i}. {table}")

        # 依赖层级
        try:
            levels = self.get_dependency_levels()
            lines.append(f"\n依赖层级分布:")
            level_groups = defaultdict(list)
            for table, level in levels.items():
                level_groups[level].append(table)
            for level in sorted(level_groups.keys()):
                tables = ", ".join(sorted(level_groups[level]))
                lines.append(f"  层级 {level}: {tables}")
        except ValueError as e:
            lines.append(f"\n⚠️  无法计算依赖层级: {e}")

        # 根表和叶子表
        root_tables = self.get_root_tables()
        leaf_tables = self.get_leaf_tables()

        lines.append(f"\n根表（无依赖）: {', '.join(root_tables) if root_tables else '无'}")
        lines.append(f"叶子表（无依赖方）: {', '.join(leaf_tables) if leaf_tables else '无'}")

        # 详细依赖关系
        lines.append(f"\n详细依赖关系:")
        for table_name in sorted(self.tables.keys()):
            deps = self.graph.get_dependencies(table_name)
            if deps:
                lines.append(f"  {table_name} 依赖于: {', '.join(deps)}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)
