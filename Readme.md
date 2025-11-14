# Fin-Data-Maker - 金融行业测试数据生成系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)

## 项目简介

Fin-Data-Maker 是一个专为金融行业设计的测试数据生成系统。通过元数据定义和数据质量规则，自动生成符合监管报送要求和业务规范的测试数据，覆盖各种数据质量场景。

## 核心特性

### 1. 元数据驱动
- 灵活的表结构定义
- 丰富的字段类型支持（ID、金额、日期、枚举等）
- 字段约束定义（必填、唯一、范围、模式等）
- 外键关联关系支持

### 2. 数据质量规则
- **完整性规则**：检查必填字段
- **唯一性规则**：确保字段值唯一
- **范围规则**：验证数值范围
- **模式规则**：正则表达式验证
- **一致性规则**：多字段间的业务逻辑校验
- **引用完整性规则**：外键引用验证

### 3. 预定义金融实体
- 客户信息（Customer）
- 账户信息（Account）
- 交易流水（Transaction）
- 贷款信息（Loan）
- 信用卡信息（Credit Card）

### 4. 多格式导出
- CSV格式（支持UTF-8 BOM，Excel兼容）
- JSON格式
- Excel格式（.xlsx）

### 5. 数据关联
- 支持表间关联关系
- 自动处理外键引用
- 保证数据一致性

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用示例

```python
from src.core.app import DataMakerApp
from src.financial.schemas import create_customer_table, create_account_table

# 创建应用实例
app = DataMakerApp(seed=42)

# 添加表定义
app.add_table(create_customer_table())
app.add_table(create_account_table())

# 生成客户数据
customer_data, report = app.generate_data("customer", count=100)

# 导出数据
app.export_data(customer_data, "output/customers.csv", format='csv')

# 生成带关联的账户数据
customer_ids = [c['customer_id'] for c in customer_data]
account_data, _ = app.generate_with_relations(
    "account",
    count=200,
    related_data={"customer": customer_ids}
)
```

### 运行示例

```bash
# 基础示例：生成客户、账户、交易数据
python examples/basic_example.py

# 自定义表示例：创建保险单数据
python examples/custom_table_example.py
```

## 项目结构

```
Fin-Data-Maker/
├── src/
│   ├── metadata/          # 元数据定义模块
│   │   ├── field.py       # 字段定义
│   │   ├── table.py       # 表定义
│   │   └── metadata_manager.py  # 元数据管理器
│   ├── rules/             # 数据质量规则模块
│   │   ├── rule.py        # 规则基类
│   │   ├── builtin_rules.py  # 内置规则
│   │   └── rule_engine.py    # 规则引擎
│   ├── generators/        # 数据生成器模块
│   │   ├── base_generator.py    # 生成器基类
│   │   ├── field_generator.py   # 字段生成器
│   │   └── table_generator.py   # 表生成器
│   ├── financial/         # 金融业务模块
│   │   └── schemas.py     # 预定义金融实体
│   ├── validators/        # 数据验证模块
│   │   └── data_validator.py   # 数据验证器
│   ├── output/            # 数据输出模块
│   │   └── exporter.py    # 数据导出器
│   └── core/              # 核心应用模块
│       └── app.py         # 主应用类
├── examples/              # 示例代码
│   ├── basic_example.py   # 基础示例
│   └── custom_table_example.py  # 自定义表示例
├── tests/                 # 单元测试
├── output/                # 输出目录
├── requirements.txt       # 项目依赖
└── setup.py              # 安装配置
```

## 自定义数据模型

### 1. 定义字段

```python
from src.metadata.field import Field, FieldType

# 定义一个金额字段
amount_field = Field(
    name="amount",
    field_type=FieldType.AMOUNT,
    description="交易金额",
    required=True,
    min_value=0.01,
    max_value=1000000,
    precision=2,
)

# 定义一个枚举字段
status_field = Field(
    name="status",
    field_type=FieldType.ENUM,
    description="状态",
    required=True,
    enum_values=["正常", "冻结", "注销"],
    default_value="正常",
)
```

### 2. 定义表

```python
from src.metadata.table import Table

# 创建表
table = Table(
    name="my_table",
    description="我的自定义表",
    primary_key="id",
)

# 添加字段
table.add_field(id_field)
table.add_field(amount_field)
table.add_field(status_field)
```

### 3. 生成数据

```python
from src.core.app import DataMakerApp

app = DataMakerApp(seed=42)
app.add_table(table)

# 生成数据
data, report = app.generate_data("my_table", count=1000)

# 导出数据
app.export_data(data, "output/my_data.csv", format='csv')
```

## 支持的字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| STRING | 字符串 | "张三" |
| INTEGER | 整数 | 100 |
| DECIMAL | 小数 | 3.14 |
| DATE | 日期 | "2024-01-01" |
| DATETIME | 日期时间 | "2024-01-01 12:00:00" |
| BOOLEAN | 布尔值 | true/false |
| ENUM | 枚举 | "正常", "冻结", "注销" |
| ID | 唯一标识符 | "CUS20240101001" |
| PHONE | 电话号码 | "13812345678" |
| EMAIL | 邮箱 | "user@example.com" |
| ID_CARD | 身份证号 | "110101199001011234" |
| BANK_CARD | 银行卡号 | "6222021234567890123" |
| AMOUNT | 金额 | 1234.56 |

## 数据质量规则

### 内置规则

1. **CompletenessRule** - 完整性规则
   - 检查必填字段是否为空

2. **UniquenessRule** - 唯一性规则
   - 确保字段值在数据集中唯一

3. **RangeRule** - 范围规则
   - 验证数值是否在指定范围内

4. **PatternRule** - 模式规则
   - 使用正则表达式验证字段格式

5. **ConsistencyRule** - 一致性规则
   - 验证多个字段间的业务逻辑

6. **ReferentialIntegrityRule** - 引用完整性规则
   - 验证外键引用的有效性

### 自定义规则

```python
from src.rules.rule import Rule, RuleType, RuleSeverity, RuleViolation

class CustomRule(Rule):
    def __init__(self):
        super().__init__(
            name="custom_rule",
            rule_type=RuleType.CONSISTENCY,
            severity=RuleSeverity.ERROR,
            description="自定义规则描述",
        )

    def validate(self, data, **kwargs):
        violations = []
        # 实现验证逻辑
        return violations
```

## 应用场景

### 1. 监管报送测试
- 生成符合监管要求的标准化数据
- 覆盖各种数据质量场景
- 验证报送系统的数据处理能力

### 2. 系统功能测试
- 为新功能开发提供测试数据
- 模拟各种业务场景
- 压力测试和性能测试

### 3. 数据迁移验证
- 生成源系统格式的数据
- 验证数据转换逻辑
- 对比迁移前后数据一致性

### 4. 培训和演示
- 生成演示用的样本数据
- 提供培训环境的测试数据
- 保护生产数据隐私

## 开发计划

- [ ] 支持更多金融实体（债券、基金、衍生品等）
- [ ] 增加数据关系图可视化
- [ ] 支持从SQL DDL导入元数据
- [ ] 提供Web界面
- [ ] 支持增量数据生成
- [ ] 添加更多数据质量规则
- [ ] 支持自定义数据生成策略

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请提交Issue。
