#!/usr/bin/env python
"""
交互式命令行工具
连接数据源、分析数据质量、生成测试数据
"""

import sys
import argparse
from typing import Optional

from src.datasource.db_connector import DatabaseConnector, DatabaseType
from src.datasource.metadata_extractor import MetadataExtractor
from src.datasource.data_profiler import DataProfiler
from src.core.app import DataMakerApp
from src.validators.data_validator import DataValidator


class InteractiveCLI:
    """交互式命令行工具"""

    def __init__(self):
        self.connector: Optional[DatabaseConnector] = None
        self.extractor: Optional[MetadataExtractor] = None
        self.profiler: Optional[DataProfiler] = None
        self.app = DataMakerApp()

    def run(self):
        """运行主程序"""
        print("=" * 80)
        print("Fin-Data-Maker - 金融数据生成系统")
        print("=" * 80)
        print()

        # 步骤1: 连接数据源
        if not self.connect_datasource():
            print("连接数据源失败，退出程序")
            return

        # 步骤2: 选择表
        table_name = self.select_table()
        if not table_name:
            print("未选择表，退出程序")
            return

        # 步骤3: 提取表结构
        print(f"\n正在提取表结构: {table_name}...")
        table = self.extractor.extract_table(table_name)
        print(f"✓ 成功提取表结构，共 {len(table.fields)} 个字段")

        # 步骤4: 分析数据质量
        should_profile = input("\n是否分析现有数据质量? (y/n): ").strip().lower()
        profiles = None

        if should_profile == 'y':
            sample_size = input("采样数量 (默认1000): ").strip()
            sample_size = int(sample_size) if sample_size else 1000

            print(f"\n正在分析数据质量（采样 {sample_size} 条）...")
            profiles = self.profiler.profile_table(table, sample_size)
            print("✓ 完成数据质量分析")

            # 显示分析报告
            show_report = input("\n是否显示详细报告? (y/n): ").strip().lower()
            if show_report == 'y':
                report = self.profiler.generate_profile_report(table_name, profiles)
                print("\n" + report)

            # 根据分析结果更新元数据
            print("\n正在根据数据分析结果更新表定义...")
            table = self.profiler.update_table_metadata(table, profiles)
            print("✓ 表定义已更新")

            # 生成质量规则建议
            strictness = input("\n质量要求严格程度 (loose/medium/strict，默认medium): ").strip()
            strictness = strictness if strictness in ['loose', 'medium', 'strict'] else 'medium'

            rules = self.profiler.generate_quality_rules(table, profiles, strictness)
            if rules:
                print(f"\n建议的数据质量规则（{strictness}）:")
                for i, rule in enumerate(rules, 1):
                    print(f"  {i}. {rule}")

        # 步骤5: 设置生成参数
        print("\n" + "=" * 80)
        print("数据生成配置")
        print("=" * 80)

        count_str = input("生成数据行数 (默认1000): ").strip()
        count = int(count_str) if count_str else 1000

        validate = input("是否验证生成的数据? (y/n，默认y): ").strip().lower()
        validate = validate != 'n'

        output_file = input("输出文件路径 (默认output/generated_data.csv): ").strip()
        output_file = output_file if output_file else "output/generated_data.csv"

        output_format = input("输出格式 (csv/json/excel，默认csv): ").strip().lower()
        output_format = output_format if output_format in ['csv', 'json', 'excel'] else 'csv'

        # 步骤6: 生成数据
        print(f"\n正在生成 {count} 条数据...")
        self.app.add_table(table)
        data, report = self.app.generate_data(table.name, count, validate)
        print(f"✓ 成功生成 {len(data)} 条数据")

        # 验证报告
        if validate and report:
            print("\n验证结果:")
            print(report.get_summary())

            if report.get_error_count() > 0:
                show_errors = input("\n是否显示错误详情? (y/n): ").strip().lower()
                if show_errors == 'y':
                    print("\n错误详情（前10条）:")
                    for v in report.violations[:10]:
                        print(f"  - 行{v.row_index}: {v.message}")

        # 步骤7: 导出数据
        print(f"\n正在导出数据到 {output_file}...")
        self.app.export_data(data, output_file, output_format)
        print(f"✓ 数据已成功导出")

        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)

    def connect_datasource(self) -> bool:
        """连接数据源"""
        print("步骤1: 连接数据源")
        print("-" * 80)

        # 选择数据库类型
        print("\n支持的数据库类型:")
        db_types = {
            '1': ('MySQL', DatabaseType.MYSQL),
            '2': ('PostgreSQL', DatabaseType.POSTGRESQL),
            '3': ('Oracle', DatabaseType.ORACLE),
            '4': ('SQL Server', DatabaseType.SQLSERVER),
            '5': ('SQLite', DatabaseType.SQLITE),
        }

        for key, (name, _) in db_types.items():
            print(f"  {key}. {name}")

        choice = input("\n请选择数据库类型 (1-5): ").strip()
        if choice not in db_types:
            print("无效的选择")
            return False

        db_name, db_type = db_types[choice]

        # SQLite特殊处理
        if db_type == DatabaseType.SQLITE:
            database = input("SQLite数据库文件路径: ").strip()
            self.connector = DatabaseConnector(
                db_type=db_type,
                database=database
            )
        else:
            # 输入连接信息
            host = input("主机地址 (默认localhost): ").strip() or 'localhost'
            port_str = input(f"端口号 (默认{self._get_default_port(db_type)}): ").strip()
            port = int(port_str) if port_str else self._get_default_port(db_type)
            database = input("数据库名: ").strip()
            username = input("用户名: ").strip()
            password = input("密码: ").strip()

            self.connector = DatabaseConnector(
                db_type=db_type,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password
            )

        # 测试连接
        print("\n正在连接数据库...")
        try:
            self.connector.connect()
            self.extractor = MetadataExtractor(self.connector)
            self.profiler = DataProfiler(self.connector)
            print(f"✓ 成功连接到 {db_name} 数据库")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {str(e)}")
            return False

    def select_table(self) -> Optional[str]:
        """选择表"""
        print("\n步骤2: 选择表")
        print("-" * 80)

        # 列出所有表
        tables = self.connector.list_tables()
        if not tables:
            print("数据库中没有找到表")
            return None

        print(f"\n找到 {len(tables)} 个表:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")

        # 选择表
        choice = input(f"\n请选择表 (1-{len(tables)}): ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(tables):
                return tables[index]
        except ValueError:
            pass

        print("无效的选择")
        return None

    def _get_default_port(self, db_type: DatabaseType) -> int:
        """获取默认端口"""
        ports = {
            DatabaseType.MYSQL: 3306,
            DatabaseType.POSTGRESQL: 5432,
            DatabaseType.ORACLE: 1521,
            DatabaseType.SQLSERVER: 1433,
        }
        return ports.get(db_type, 3306)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Fin-Data-Maker - 金融数据生成系统'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='交互式模式'
    )

    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        # 交互式模式
        cli = InteractiveCLI()
        try:
            cli.run()
        except KeyboardInterrupt:
            print("\n\n程序已取消")
        except Exception as e:
            print(f"\n错误: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
