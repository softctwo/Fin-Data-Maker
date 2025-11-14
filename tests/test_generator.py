"""
测试数据生成器模块
"""

import unittest
from src.metadata.field import Field, FieldType
from src.metadata.table import Table
from src.generators.field_generator import FieldGenerator
from src.generators.table_generator import TableGenerator


class TestFieldGenerator(unittest.TestCase):
    """测试字段生成器"""

    def setUp(self):
        """设置测试环境"""
        self.generator = FieldGenerator(seed=42)

    def test_generate_string(self):
        """测试生成字符串"""
        field = Field(
            name="name",
            field_type=FieldType.STRING,
            min_length=5,
            max_length=10,
        )

        value = self.generator.generate(field)
        self.assertIsInstance(value, str)
        self.assertGreaterEqual(len(value), 5)
        self.assertLessEqual(len(value), 10)

    def test_generate_integer(self):
        """测试生成整数"""
        field = Field(
            name="age",
            field_type=FieldType.INTEGER,
            min_value=18,
            max_value=65,
        )

        value = self.generator.generate(field)
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 18)
        self.assertLessEqual(value, 65)

    def test_generate_enum(self):
        """测试生成枚举值"""
        field = Field(
            name="status",
            field_type=FieldType.ENUM,
            enum_values=["正常", "冻结", "注销"],
        )

        value = self.generator.generate(field)
        self.assertIn(value, ["正常", "冻结", "注销"])

    def test_generate_unique(self):
        """测试生成唯一值"""
        field = Field(
            name="id",
            field_type=FieldType.ID,
            unique=True,
            length=10,
        )

        # 生成多个值
        values = [self.generator.generate(field) for _ in range(100)]

        # 检查唯一性
        self.assertEqual(len(values), len(set(values)))


class TestTableGenerator(unittest.TestCase):
    """测试表生成器"""

    def setUp(self):
        """设置测试环境"""
        # 创建测试表
        self.table = Table(name="test_table", primary_key="id")

        self.table.add_field(Field(
            name="id",
            field_type=FieldType.ID,
            required=True,
            unique=True,
            length=10,
        ))

        self.table.add_field(Field(
            name="name",
            field_type=FieldType.STRING,
            required=True,
            min_length=2,
            max_length=20,
        ))

        self.table.add_field(Field(
            name="age",
            field_type=FieldType.INTEGER,
            required=True,
            min_value=18,
            max_value=65,
        ))

        self.generator = TableGenerator(self.table, seed=42)

    def test_generate_single_row(self):
        """测试生成单行数据"""
        row = self.generator.generate()

        # 检查所有字段都存在
        self.assertIn("id", row)
        self.assertIn("name", row)
        self.assertIn("age", row)

        # 检查数据类型
        self.assertIsInstance(row["name"], str)
        self.assertIsInstance(row["age"], int)

    def test_generate_batch(self):
        """测试批量生成数据"""
        count = 100
        data = self.generator.generate_batch(count)

        # 检查数量
        self.assertEqual(len(data), count)

        # 检查ID唯一性
        ids = [row["id"] for row in data]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
