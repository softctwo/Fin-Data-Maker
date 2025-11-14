"""
数据生成应用主类
整合所有模块功能
"""

from typing import List, Dict, Any, Optional
from ..metadata.metadata_manager import MetadataManager
from ..metadata.table import Table
from ..generators.table_generator import TableGenerator
from ..validators.data_validator import DataValidator
from ..rules.rule_engine import ValidationReport
from ..output.exporter import CSVExporter, JSONExporter, ExcelExporter


class DataMakerApp:
    """
    数据生成应用
    提供完整的数据生成、验证和导出功能
    """

    def __init__(self, seed: Optional[int] = None):
        """
        初始化应用

        Args:
            seed: 随机种子，用于生成可重复的数据
        """
        self.seed = seed
        self.metadata_manager = MetadataManager()

    def load_metadata(self, file_path: str, format: str = 'yaml'):
        """
        加载元数据定义

        Args:
            file_path: 元数据文件路径
            format: 文件格式（yaml或json）
        """
        if format == 'yaml':
            self.metadata_manager.load_from_yaml(file_path)
        elif format == 'json':
            self.metadata_manager.load_from_json(file_path)
        else:
            raise ValueError(f"不支持的格式: {format}")

    def add_table(self, table: Table):
        """添加表定义"""
        self.metadata_manager.add_table(table)

    def generate_data(
        self,
        table_name: str,
        count: int,
        validate: bool = True,
        **kwargs
    ) -> tuple[List[Dict[str, Any]], Optional[ValidationReport]]:
        """
        生成数据

        Args:
            table_name: 表名
            count: 生成行数
            validate: 是否验证数据
            **kwargs: 传递给生成器的额外参数

        Returns:
            tuple: (生成的数据, 验证报告)
        """
        # 获取表定义
        table = self.metadata_manager.get_table(table_name)
        if not table:
            raise ValueError(f"表 {table_name} 不存在")

        # 生成数据
        generator = TableGenerator(table, seed=self.seed)
        data = generator.generate_batch(count, **kwargs)

        # 验证数据
        report = None
        if validate:
            validator = DataValidator(table)
            report = validator.validate(data)

        return data, report

    def generate_with_relations(
        self,
        table_name: str,
        count: int,
        related_data: Optional[Dict[str, List[Any]]] = None,
        validate: bool = True,
        **kwargs
    ) -> tuple[List[Dict[str, Any]], Optional[ValidationReport]]:
        """
        生成带关联关系的数据

        Args:
            table_name: 表名
            count: 生成行数
            related_data: 关联表数据
            validate: 是否验证数据
            **kwargs: 传递给生成器的额外参数

        Returns:
            tuple: (生成的数据, 验证报告)
        """
        # 获取表定义
        table = self.metadata_manager.get_table(table_name)
        if not table:
            raise ValueError(f"表 {table_name} 不存在")

        # 生成数据
        generator = TableGenerator(table, seed=self.seed)
        data = generator.generate_with_relations(count, related_data, **kwargs)

        # 验证数据
        report = None
        if validate:
            validator = DataValidator(table)
            report = validator.validate(data)

        return data, report

    def export_data(
        self,
        data: List[Dict[str, Any]],
        file_path: str,
        format: str = 'csv',
        **kwargs
    ):
        """
        导出数据

        Args:
            data: 要导出的数据
            file_path: 输出文件路径
            format: 输出格式（csv、json、excel）
            **kwargs: 传递给导出器的额外参数
        """
        if format == 'csv':
            exporter = CSVExporter()
        elif format == 'json':
            exporter = JSONExporter()
        elif format == 'excel':
            exporter = ExcelExporter()
        else:
            raise ValueError(f"不支持的格式: {format}")

        exporter.export(data, file_path, **kwargs)

    def generate_and_export(
        self,
        table_name: str,
        count: int,
        file_path: str,
        format: str = 'csv',
        validate: bool = True,
        **kwargs
    ) -> Optional[ValidationReport]:
        """
        生成数据并导出

        Args:
            table_name: 表名
            count: 生成行数
            file_path: 输出文件路径
            format: 输出格式
            validate: 是否验证数据
            **kwargs: 额外参数

        Returns:
            ValidationReport: 验证报告（如果启用验证）
        """
        # 生成数据
        data, report = self.generate_data(table_name, count, validate, **kwargs)

        # 导出数据
        self.export_data(data, file_path, format)

        return report

    def generate_incremental_data(
        self,
        table_name: str,
        existing_data: List[Dict[str, Any]],
        count: int,
        validate: bool = True
    ) -> tuple[List[Dict[str, Any]], Optional[ValidationReport]]:
        """
        生成增量数据（在现有数据基础上追加新数据）

        Args:
            table_name: 表名
            existing_data: 现有数据列表
            count: 要生成的增量记录数
            validate: 是否验证数据

        Returns:
            tuple: (增量数据列表, 验证报告)
        """
        from ..generators.incremental_generator import IncrementalGenerator

        # 获取表定义
        table = self.metadata_manager.get_table(table_name)
        if not table:
            raise ValueError(f"表 '{table_name}' 不存在")

        # 创建增量生成器
        generator = IncrementalGenerator(table, existing_data, seed=self.seed)

        # 生成增量数据
        incremental_data = generator.generate_incremental_data(count)

        # 验证数据
        report = None
        if validate and table.rules:
            validator = DataValidator()
            report = validator.validate(incremental_data, table)

        return incremental_data, report

    def generate_incremental_with_relations(
        self,
        table_name: str,
        existing_data: List[Dict[str, Any]],
        count: int,
        related_data: Dict[str, List[Any]],
        validate: bool = True
    ) -> tuple[List[Dict[str, Any]], Optional[ValidationReport]]:
        """
        生成带关联的增量数据

        Args:
            table_name: 表名
            existing_data: 现有数据列表
            count: 要生成的增量记录数
            related_data: 关联表的ID列表，格式: {table_name: [id1, id2, ...]}
            validate: 是否验证数据

        Returns:
            tuple: (增量数据列表, 验证报告)
        """
        from ..generators.incremental_generator import IncrementalGenerator

        # 获取表定义
        table = self.metadata_manager.get_table(table_name)
        if not table:
            raise ValueError(f"表 '{table_name}' 不存在")

        # 创建增量生成器
        generator = IncrementalGenerator(table, existing_data, seed=self.seed)

        # 生成带关联的增量数据
        incremental_data = generator.generate_with_relations(count, related_data)

        # 验证数据
        report = None
        if validate and table.rules:
            validator = DataValidator()
            report = validator.validate(incremental_data, table)

        return incremental_data, report
