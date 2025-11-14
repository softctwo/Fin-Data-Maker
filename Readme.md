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

### 6. 数据源连接
- 支持多种数据库（MySQL、PostgreSQL、Oracle、SQL Server、SQLite）
- 自动提取表结构和元数据
- 数据质量分析和profiling
- 根据现有数据特征生成测试数据

### 7. Web界面（NEW!）
- 现代化的图形用户界面
- 4步向导式操作流程
- 实时数据预览和质量报告
- 无需编程即可使用所有功能

### 8. 高级功能（专业版）
- **用户认证系统**：安全的用户注册、登录和会话管理
- **配置保存**：保存和重用数据生成配置
- **历史记录**：完整的操作历史追踪和统计分析
- **批量处理**：同时处理多个表（计划中）
- **可视化图表**：数据质量可视化展示（计划中）
- **定时任务**：自动化数据生成调度（计划中）

## 快速开始

### 方式1：使用Web界面（推荐）

**基础版（无需认证）：**
```bash
# 安装依赖
pip install -r requirements.txt

# 启动基础版Web服务器
python webapp.py

# 在浏览器中打开
http://localhost:5000
```

**专业版（带用户认证和高级功能）：**
```bash
# 安装依赖
pip install -r requirements.txt

# 启动专业版Web服务器
python webapp_pro.py

# 在浏览器中打开
http://localhost:5000

# 使用默认管理员账户登录
用户名：admin
密码：admin123
```

**专业版额外功能**：
- 用户认证系统（注册/登录/登出）
- 配置保存和管理
- 历史记录查看和统计
- 详见 [高级功能指南](docs/ADVANCED_FEATURES.md)

然后按照界面引导完成操作：
1. 连接数据源
2. 选择表
3. 分析数据质量（可选）
4. 生成并导出数据

详细使用说明请查看 [Web界面使用指南](docs/WEB_GUIDE.md)

### 方式2：使用命令行或编程

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
# Web界面基础版（推荐）
python webapp.py

# Web界面专业版（带认证和高级功能）
python webapp_pro.py

# 交互式命令行工具
python cli.py --interactive

# 基础示例：生成客户、账户、交易数据
python examples/basic_example.py

# 自定义表示例：创建保险单数据
python examples/custom_table_example.py

# 数据源连接示例：从数据库提取表结构并生成数据
python examples/datasource_example.py
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
│   ├── datasource/        # 数据源连接模块
│   │   ├── db_connector.py       # 数据库连接器
│   │   ├── metadata_extractor.py # 元数据提取器
│   │   ├── data_profiler.py      # 数据质量分析器
│   │   └── config_manager.py     # 配置管理器
│   ├── web/               # Web应用模块（专业版）
│   │   ├── __init__.py    # 模块初始化
│   │   ├── models.py      # 数据库模型（User, Config, History, ScheduledTask）
│   │   └── auth.py        # 认证模块（Flask-Login）
│   ├── validators/        # 数据验证模块
│   │   └── data_validator.py   # 数据验证器
│   ├── output/            # 数据输出模块
│   │   └── exporter.py    # 数据导出器
│   └── core/              # 核心应用模块
│       └── app.py         # 主应用类
├── examples/              # 示例代码
│   ├── basic_example.py   # 基础示例
│   ├── custom_table_example.py  # 自定义表示例
│   └── datasource_example.py    # 数据源连接示例
├── config/                # 配置文件目录
│   └── datasources.example.yaml # 数据源配置示例
├── templates/             # Web模板
│   ├── index.html         # Web界面主页
│   ├── login.html         # 登录页面（专业版）
│   └── register.html      # 注册页面（专业版）
├── static/                # 静态资源
│   └── app.js             # 前端JavaScript
├── docs/                  # 文档目录
│   ├── WEB_GUIDE.md       # Web界面使用指南
│   └── ADVANCED_FEATURES.md  # 高级功能指南（专业版）
├── tests/                 # 单元测试
├── output/                # 输出目录
├── webapp.py              # Web应用入口（基础版）
├── webapp_pro.py          # Web应用入口（专业版，带认证）
├── cli.py                 # 交互式命令行工具
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

## 从数据源连接生成数据

系统支持直接连接数据库，自动提取表结构、分析数据质量并生成符合特征的测试数据。

### 1. 连接数据库

```python
from src.datasource.db_connector import DatabaseConnector, DatabaseType

# 连接MySQL
connector = DatabaseConnector(
    db_type=DatabaseType.MYSQL,
    host='localhost',
    port=3306,
    database='your_database',
    username='your_username',
    password='your_password'
)

connector.connect()
```

### 2. 提取表结构

```python
from src.datasource.metadata_extractor import MetadataExtractor

# 创建元数据提取器
extractor = MetadataExtractor(connector)

# 提取单个表
table = extractor.extract_table('customer')

# 或提取所有表
tables = extractor.extract_all_tables()
```

### 3. 分析数据质量

```python
from src.datasource.data_profiler import DataProfiler

# 创建数据分析器
profiler = DataProfiler(connector)

# 分析表数据质量
profiles = profiler.profile_table(table, sample_size=1000)

# 生成分析报告
report = profiler.generate_profile_report('customer', profiles)
print(report)

# 根据分析结果更新表定义
table = profiler.update_table_metadata(table, profiles)

# 生成质量规则建议
rules = profiler.generate_quality_rules(table, profiles, strictness='medium')
```

### 4. 生成测试数据

```python
from src.core.app import DataMakerApp

# 创建应用并生成数据
app = DataMakerApp(seed=42)
app.add_table(table)

# 生成符合数据质量要求的测试数据
data, validation_report = app.generate_data('customer', count=1000)

# 导出数据
app.export_data(data, 'output/customer_test.csv', format='csv')
```

### 5. 使用交互式命令行工具

最简单的方式是使用交互式命令行工具：

```bash
python cli.py --interactive
```

工具会引导您完成以下步骤：
1. 选择数据库类型并输入连接信息
2. 列出并选择要处理的表
3. 可选：分析现有数据质量
4. 设置生成参数（行数、验证、输出格式等）
5. 生成并导出测试数据

### 支持的数据库

| 数据库 | 类型标识 | 默认端口 |
|--------|----------|----------|
| MySQL | mysql | 3306 |
| PostgreSQL | postgresql | 5432 |
| Oracle | oracle | 1521 |
| SQL Server | sqlserver | 1433 |
| SQLite | sqlite | - |

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

**已完成**：
- [x] 提供Web界面
- [x] 用户认证系统
- [x] 配置保存和管理
- [x] 历史记录追踪

**进行中**：
- [ ] 批量处理多个表
- [ ] 数据质量可视化图表
- [ ] 定时任务调度

**计划中**：
- [ ] 支持更多金融实体（债券、基金、衍生品等）
- [ ] 增加数据关系图可视化
- [ ] 支持从SQL DDL导入元数据
- [ ] 支持增量数据生成
- [ ] 添加更多数据质量规则
- [ ] 支持自定义数据生成策略
- [ ] API令牌认证
- [ ] 团队协作功能

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请提交Issue。
