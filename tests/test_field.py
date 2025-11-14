"""
测试字段定义模块
"""

import unittest
from src.metadata.field import Field, FieldType


class TestField(unittest.TestCase):
    """测试Field类"""

    def test_field_creation(self):
        """测试字段创建"""
        field = Field(
            name="test_field",
            field_type=FieldType.STRING,
            description="测试字段",
            required=True,
            max_length=50,
        )

        self.assertEqual(field.name, "test_field")
        self.assertEqual(field.field_type, FieldType.STRING)
        self.assertTrue(field.required)
        self.assertEqual(field.max_length, 50)

    def test_string_validation(self):
        """测试字符串字段验证"""
        field = Field(
            name="name",
            field_type=FieldType.STRING,
            required=True,
            min_length=2,
            max_length=10,
        )

        # 有效值
        self.assertTrue(field.validate("张三"))
        self.assertTrue(field.validate("abcdefghij"))

        # 无效值
        self.assertFalse(field.validate(None))  # 必填但为空
        self.assertFalse(field.validate(""))   # 空字符串
        self.assertFalse(field.validate("a"))  # 太短
        self.assertFalse(field.validate("12345678901"))  # 太长

    def test_integer_validation(self):
        """测试整数字段验证"""
        field = Field(
            name="age",
            field_type=FieldType.INTEGER,
            required=True,
            min_value=0,
            max_value=150,
        )

        # 有效值
        self.assertTrue(field.validate(25))
        self.assertTrue(field.validate(0))
        self.assertTrue(field.validate(150))

        # 无效值
        self.assertFalse(field.validate(-1))  # 小于最小值
        self.assertFalse(field.validate(151))  # 大于最大值
        self.assertFalse(field.validate("25"))  # 类型错误

    def test_enum_validation(self):
        """测试枚举字段验证"""
        field = Field(
            name="status",
            field_type=FieldType.ENUM,
            required=True,
            enum_values=["正常", "冻结", "注销"],
        )

        # 有效值
        self.assertTrue(field.validate("正常"))
        self.assertTrue(field.validate("冻结"))

        # 无效值
        self.assertFalse(field.validate("未知"))
        self.assertFalse(field.validate(""))

    def test_field_to_dict(self):
        """测试字段转换为字典"""
        field = Field(
            name="amount",
            field_type=FieldType.AMOUNT,
            required=True,
            min_value=0,
            max_value=1000000,
            precision=2,
        )

        field_dict = field.to_dict()

        self.assertEqual(field_dict["name"], "amount")
        self.assertEqual(field_dict["type"], "amount")
        self.assertEqual(field_dict["min_value"], 0)
        self.assertEqual(field_dict["max_value"], 1000000)
        self.assertEqual(field_dict["precision"], 2)

    def test_field_from_dict(self):
        """测试从字典创建字段"""
        field_dict = {
            "name": "email",
            "type": "email",
            "description": "邮箱",
            "required": True,
        }

        field = Field.from_dict(field_dict)

        self.assertEqual(field.name, "email")
        self.assertEqual(field.field_type, FieldType.EMAIL)
        self.assertTrue(field.required)


if __name__ == "__main__":
    unittest.main()
