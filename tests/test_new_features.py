"""
单元测试：新增功能（可视化、依赖分析、进度监控）
测试三个新模块的功能
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.financial.schemas import (
    create_customer_table,
    create_account_table,
    create_bond_table,
    create_fund_table,
    create_derivative_table,
)
from src.analysis.dependency_analyzer import DependencyAnalyzer, DependencyGraph, DependencyEdge
from src.visualization.relationship_visualizer import RelationshipVisualizer, VisualizationFormat
from src.core.progress_monitor import ProgressMonitor, ProgressEvent, ProgressEventType


class TestDependencyAnalyzer(unittest.TestCase):
    """测试依赖分析器"""

    def setUp(self):
        """测试前准备"""
        self.tables = [
            create_customer_table(),
            create_account_table(),
            create_bond_table(),
            create_fund_table(),
            create_derivative_table(),
        ]
        self.analyzer = DependencyAnalyzer(self.tables)

    def test_dependency_graph_creation(self):
        """测试依赖关系图创建"""
        graph = self.analyzer.graph
        self.assertIsInstance(graph, DependencyGraph)
        self.assertGreater(len(graph.edges), 0)
        self.assertGreater(len(graph.tables), 0)

    def test_get_dependencies(self):
        """测试获取表的依赖"""
        # account表依赖customer表
        account_deps = self.analyzer.graph.get_dependencies('account')
        self.assertIn('customer', account_deps)

        # bond表依赖customer表
        bond_deps = self.analyzer.graph.get_dependencies('bond')
        self.assertIn('customer', bond_deps)

        # customer表没有依赖
        customer_deps = self.analyzer.graph.get_dependencies('customer')
        self.assertEqual(len(customer_deps), 0)

    def test_get_dependents(self):
        """测试获取依赖指定表的表"""
        # customer表被account和bond依赖
        customer_dependents = self.analyzer.graph.get_dependents('customer')
        self.assertIn('account', customer_dependents)
        self.assertIn('bond', customer_dependents)

    def test_detect_cycles(self):
        """测试循环依赖检测"""
        cycles = self.analyzer.detect_cycles()
        # 当前的表结构不应该有循环依赖
        self.assertEqual(len(cycles), 0)

    def test_topological_sort(self):
        """测试拓扑排序"""
        order, success = self.analyzer.topological_sort()
        self.assertTrue(success)
        self.assertGreater(len(order), 0)

        # customer表应该在account和bond之前
        customer_idx = order.index('customer')
        account_idx = order.index('account')
        bond_idx = order.index('bond')

        self.assertLess(customer_idx, account_idx)
        self.assertLess(customer_idx, bond_idx)

    def test_get_generation_order(self):
        """测试获取生成顺序"""
        order = self.analyzer.get_generation_order()
        self.assertEqual(len(order), len(self.tables))

        # 第一个应该是没有依赖的表
        first_table = order[0]
        deps = self.analyzer.graph.get_dependencies(first_table)
        self.assertEqual(len(deps), 0)

    def test_get_dependency_levels(self):
        """测试获取依赖层级"""
        levels = self.analyzer.get_dependency_levels()

        # customer应该在层级0（没有依赖）
        self.assertEqual(levels['customer'], 0)

        # account和bond应该在层级1（依赖customer）
        self.assertGreaterEqual(levels['account'], 1)
        self.assertGreaterEqual(levels['bond'], 1)

    def test_get_root_tables(self):
        """测试获取根表"""
        root_tables = self.analyzer.get_root_tables()
        self.assertIn('customer', root_tables)
        self.assertIn('derivative', root_tables)  # derivative没有外键依赖

    def test_get_leaf_tables(self):
        """测试获取叶子表"""
        leaf_tables = self.analyzer.get_leaf_tables()
        # 叶子表是没有其他表依赖的表
        self.assertIsInstance(leaf_tables, list)

    def test_get_dependency_chain(self):
        """测试获取依赖链"""
        # account的依赖链应该包含customer和account
        chain = self.analyzer.get_dependency_chain('account')
        self.assertIn('customer', chain)
        self.assertIn('account', chain)

        # customer应该在account之前
        self.assertLess(chain.index('customer'), chain.index('account'))

    def test_analyze_table(self):
        """测试单表分析"""
        analysis = self.analyzer.analyze_table('bond')

        self.assertEqual(analysis['table_name'], 'bond')
        self.assertIn('dependencies', analysis)
        self.assertIn('dependents', analysis)
        self.assertIn('dependency_level', analysis)
        self.assertIn('is_root', analysis)
        self.assertIn('is_leaf', analysis)
        self.assertIn('dependency_chain', analysis)
        self.assertIn('related_edges', analysis)

        # bond依赖customer
        self.assertIn('customer', analysis['dependencies'])

    def test_generate_report(self):
        """测试生成分析报告"""
        report = self.analyzer.generate_report()
        self.assertIsInstance(report, str)
        self.assertIn('表依赖关系分析报告', report)
        self.assertIn('customer', report)


class TestRelationshipVisualizer(unittest.TestCase):
    """测试关系可视化器"""

    def setUp(self):
        """测试前准备"""
        self.tables = [
            create_customer_table(),
            create_account_table(),
            create_bond_table(),
        ]
        self.visualizer = RelationshipVisualizer(self.tables)

    def test_generate_dot(self):
        """测试生成DOT格式"""
        dot_content = self.visualizer.generate_dot(
            show_fields=True,
            show_field_types=True,
            highlight_keys=True
        )

        self.assertIsInstance(dot_content, str)
        self.assertIn('digraph ER', dot_content)
        self.assertIn('customer', dot_content)
        self.assertIn('account', dot_content)
        self.assertIn('bond', dot_content)

    def test_generate_mermaid(self):
        """测试生成Mermaid格式"""
        mermaid_content = self.visualizer.generate_mermaid(
            show_fields=True,
            show_field_types=True
        )

        self.assertIsInstance(mermaid_content, str)
        self.assertIn('erDiagram', mermaid_content)
        self.assertIn('customer', mermaid_content)
        self.assertIn('account', mermaid_content)

    def test_generate_plantuml(self):
        """测试生成PlantUML格式"""
        plantuml_content = self.visualizer.generate_plantuml(
            show_fields=True,
            show_field_types=True
        )

        self.assertIsInstance(plantuml_content, str)
        self.assertIn('@startuml', plantuml_content)
        self.assertIn('@enduml', plantuml_content)
        self.assertIn('customer', plantuml_content)

    def test_generate_dependency_diagram_mermaid(self):
        """测试生成Mermaid依赖关系图"""
        dep_content = self.visualizer.generate_dependency_diagram(
            format=VisualizationFormat.MERMAID
        )

        self.assertIsInstance(dep_content, str)
        self.assertIn('graph LR', dep_content)
        self.assertIn('customer', dep_content)

    def test_generate_dependency_diagram_dot(self):
        """测试生成DOT依赖关系图"""
        dep_content = self.visualizer.generate_dependency_diagram(
            format=VisualizationFormat.GRAPHVIZ_DOT
        )

        self.assertIsInstance(dep_content, str)
        self.assertIn('digraph Dependencies', dep_content)

    def test_generate_to_file(self):
        """测试生成到文件"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mmd') as f:
            temp_file = f.name

        try:
            self.visualizer.generate_mermaid(output_file=temp_file)

            # 验证文件是否创建
            self.assertTrue(os.path.exists(temp_file))

            # 验证文件内容
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('erDiagram', content)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_generate_with_enum_format(self):
        """测试使用枚举格式生成"""
        dot_content = self.visualizer.generate(
            format=VisualizationFormat.GRAPHVIZ_DOT,
            show_fields=True
        )
        self.assertIn('digraph ER', dot_content)

        mermaid_content = self.visualizer.generate(
            format=VisualizationFormat.MERMAID,
            show_fields=True
        )
        self.assertIn('erDiagram', mermaid_content)


class TestProgressMonitor(unittest.TestCase):
    """测试进度监控器"""

    def setUp(self):
        """测试前准备"""
        self.monitor = ProgressMonitor()

    def test_initialization(self):
        """测试初始化"""
        self.assertFalse(self.monitor.is_running)
        self.assertFalse(self.monitor.is_cancelled)
        self.assertEqual(self.monitor.total_items, 0)
        self.assertEqual(self.monitor.completed_items, 0)

    def test_add_remove_callback(self):
        """测试添加和移除回调"""
        callback = MagicMock()

        self.monitor.add_callback(callback)
        self.assertIn(callback, self.monitor.callbacks)

        self.monitor.remove_callback(callback)
        self.assertNotIn(callback, self.monitor.callbacks)

    def test_start(self):
        """测试开始监控"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(total_items=100, table_name='test_table')

        self.assertTrue(self.monitor.is_running)
        self.assertEqual(self.monitor.total_items, 100)
        self.assertEqual(self.monitor.current_table, 'test_table')

        # 验证回调被调用
        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.STARTED)

    def test_update(self):
        """测试更新进度"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(total_items=100)
        callback.reset_mock()

        self.monitor.update(completed=50, message="测试进度")

        self.assertEqual(self.monitor.completed_items, 50)

        # 验证回调被调用
        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.PROGRESS)
        self.assertEqual(event.current, 50)
        self.assertEqual(event.total, 100)
        self.assertEqual(event.percentage, 50.0)

    def test_table_started(self):
        """测试表开始"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.table_started('test_table', 50)

        self.assertEqual(self.monitor.current_table, 'test_table')
        self.assertEqual(self.monitor.total_items, 50)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.TABLE_STARTED)

    def test_table_completed(self):
        """测试表完成"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(100, 'test_table')
        callback.reset_mock()

        self.monitor.table_completed('test_table', 100)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.TABLE_COMPLETED)

    def test_batch_completed(self):
        """测试批次完成"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(100)
        callback.reset_mock()

        self.monitor.batch_completed(batch_size=20, batch_num=1)

        self.assertEqual(self.monitor.completed_items, 20)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.BATCH_COMPLETED)

    def test_validation_started(self):
        """测试验证开始"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.validation_started(100)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.VALIDATION_STARTED)

    def test_validation_completed(self):
        """测试验证完成"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.validation_completed(100, is_valid=True, error_count=0)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.VALIDATION_COMPLETED)
        self.assertTrue(event.metadata['is_valid'])
        self.assertEqual(event.metadata['error_count'], 0)

    def test_complete(self):
        """测试完成"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(100)
        self.monitor.update(100)
        callback.reset_mock()

        self.monitor.complete("测试完成")

        self.assertFalse(self.monitor.is_running)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.COMPLETED)

    def test_error(self):
        """测试错误报告"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(100)
        callback.reset_mock()

        test_exception = ValueError("测试错误")
        self.monitor.error("发生错误", test_exception)

        self.assertFalse(self.monitor.is_running)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.ERROR)
        self.assertIn('exception_type', event.metadata)
        self.assertEqual(event.metadata['exception_type'], 'ValueError')

    def test_cancel(self):
        """测试取消操作"""
        callback = MagicMock()
        self.monitor.add_callback(callback)

        self.monitor.start(100)
        callback.reset_mock()

        self.monitor.cancel()

        self.assertFalse(self.monitor.is_running)
        self.assertTrue(self.monitor.is_cancelled)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        self.assertEqual(event.event_type, ProgressEventType.CANCELLED)

    def test_get_current_progress(self):
        """测试获取当前进度"""
        self.monitor.start(100, 'test_table')
        self.monitor.update(50)

        progress = self.monitor.get_current_progress()

        self.assertTrue(progress['is_running'])
        self.assertFalse(progress['is_cancelled'])
        self.assertEqual(progress['current_table'], 'test_table')
        self.assertEqual(progress['completed_items'], 50)
        self.assertEqual(progress['total_items'], 100)
        self.assertEqual(progress['percentage'], 50.0)

    def test_get_summary(self):
        """测试获取摘要"""
        self.monitor.start(100, 'test_table')
        self.monitor.update(50)

        summary = self.monitor.get_summary()

        self.assertIsInstance(summary, str)
        self.assertIn('进度摘要', summary)
        self.assertIn('test_table', summary)
        self.assertIn('50/100', summary)

    def test_history(self):
        """测试历史记录"""
        self.monitor.start(100)
        self.monitor.update(50)
        self.monitor.complete()

        self.assertGreater(len(self.monitor.history), 0)

        # 验证历史记录顺序
        first_event = self.monitor.history[0]
        last_event = self.monitor.history[-1]

        self.assertEqual(first_event.event_type, ProgressEventType.STARTED)
        self.assertEqual(last_event.event_type, ProgressEventType.COMPLETED)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestRelationshipVisualizer))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressMonitor))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
