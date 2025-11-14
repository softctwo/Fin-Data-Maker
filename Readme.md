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
**基础实体**:
- 客户信息（Customer）
- 账户信息（Account）
- 交易流水（Transaction）
- 贷款信息（Loan）
- 信用卡信息（Credit Card）

**新增实体** 🆕:
- **债券信息（Bond）** - 支持8种债券类型，15个字段
- **基金信息（Fund）** - 支持9种基金类型，17个字段
- **衍生品信息（Derivative）** - 支持6种衍生品类型，18个字段

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

### 8. 数据关系可视化 🆕
- **ER图生成**：支持Mermaid/Graphviz/PlantUML格式
- **依赖关系图**：可视化表间依赖关系
- **自动渲染**：可导出为PNG/SVG/PDF图片
- **在线查看**：生成的图表可直接在线查看

### 9. 表间依赖分析 🆕
- **循环依赖检测**：自动识别循环引用问题
- **拓扑排序**：推荐最优数据生成顺序
- **依赖层级**：计算表的依赖深度
- **依赖链分析**：完整的依赖路径追踪
- **详细报告**：生成全面的依赖分析报告

### 10. 实时进度监控 🆕
- **实时进度跟踪**：监控数据生成过程
- **进度条显示**：直观的可视化进度
- **事件回调**：灵活的事件通知机制
- **ETA预测**：预计剩余完成时间
- **历史记录**：保存完整的进度历史

### 11. 高级功能（专业版）
- **用户认证系统**：安全的用户注册、登录和会话管理
- **配置保存**：保存和重用数据生成配置
- **历史记录**：完整的操作历史追踪和统计分析
- **批量处理**：同时处理多个表（计划中）
- **定时任务**：自动化数据生成调度（计划中）

## 快速开始

### 方式一：使用Docker（推荐）🐳

最快速的方式是使用Docker Compose启动MySQL测试环境：

```bash
# 启动MySQL + Adminer
docker-compose up -d

# 访问Adminer Web管理界面
# http://localhost:8080
# 服务器: mysql, 用户: root, 密码: findata123
```

SQL脚本会自动导入，立即可用！详见 [Docker使用指南](docker/README.md)

### 方式二：使用SQL脚本

如果已有MySQL数据库，可以直接导入SQL脚本：

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE fin_data_maker CHARACTER SET utf8mb4;"

# 导入表结构和测试数据
mysql -u root -p fin_data_maker < sql/full_setup.sql

# 验证数据
mysql -u root -p fin_data_maker -e "SELECT COUNT(*) FROM bond;"
```

详见 [SQL脚本使用说明](sql/README.md)

### 方式三：使用Python生成数据

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 基础使用示例

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
# 访问 http://localhost:5000

# Web界面专业版（带认证和高级功能）✨
python webapp_pro.py
# 访问 http://localhost:5000
# 功能页面：
#   - /          数据生成（4步向导）
#   - /dashboard 数据仪表板（可视化图表）
#   - /batch     批量处理管理
#   - /tasks     定时任务管理

# 交互式命令行工具
python cli.py --interactive

# 基础示例：生成客户、账户、交易数据
python examples/basic_example.py

# 新增实体示例：生成债券、基金、衍生品数据 🆕
python examples/new_entities_example.py

# 自定义表示例：创建保险单数据
python examples/custom_table_example.py

# DDL导入示例：从SQL DDL生成数据 🆕
python examples/ddl_import_example.py

# 高级功能示例：增量数据生成和新规则 🆕
python examples/advanced_features_example.py

# 生成SQL INSERT语句 🆕
python tools/generate_sql_inserts.py

# 可视化和依赖分析示例 🆕🎨
python examples/visualization_example.py
```

**新功能快速体验**：

```python
# 1. 依赖关系分析
from src.analysis.dependency_analyzer import DependencyAnalyzer
from src.financial.schemas import create_customer_table, create_bond_table

analyzer = DependencyAnalyzer([create_customer_table(), create_bond_table()])
print(analyzer.generate_report())  # 生成分析报告

# 2. ER图可视化
from src.visualization.relationship_visualizer import RelationshipVisualizer

visualizer = RelationshipVisualizer([create_customer_table(), create_bond_table()])
visualizer.generate_mermaid('output/er_diagram.mmd')  # 生成Mermaid ER图

# 3. 进度监控
from src.core.progress_monitor import ProgressMonitor, simple_progress_bar_callback

monitor = ProgressMonitor()
monitor.add_callback(simple_progress_bar_callback)
monitor.start(100, 'customer')
# ... 数据生成过程 ...
monitor.complete()
```

### 专业版功能亮点 ✨

启动 `webapp_pro.py` 后，您可以体验以下企业级功能：

1. **数据生成**（主页）
   - 4步向导式操作：连接数据库 → 选择表 → 配置参数 → 预览和导出
   - 支持5种数据库类型（MySQL、PostgreSQL、Oracle、SQL Server、SQLite）
   - **DDL导入** 🆕：支持从CREATE TABLE语句直接导入表结构
     - 粘贴SQL DDL即可自动解析表结构
     - 实时预览解析结果
     - 支持多表批量导入
   - 实时数据预览和质量报告
   - 配置保存和重用

2. **数据仪表板**（/dashboard）
   - **统计卡片**：展示关键指标（已分析表数、生成记录数、平均质量分等）
   - **历史趋势图**：7天操作历史折线图
   - **质量概览图**：最近10次分析的质量柱状图
   - **完整性分布**：字段完整性饼图
   - **质量雷达图**：多维度质量评分

3. **批量处理**（/batch）
   - 一次创建多个表的数据生成任务
   - 实时进度追踪（进度条和百分比）
   - 任务管理（查看详情、取消运行中任务、删除任务）
   - 每个表的处理结果详情
   - 自动刷新（每5秒）

4. **定时任务**（/tasks）
   - 创建自动化数据生成任务
   - 4种调度模式：
     - 一次性：指定具体执行时间
     - 每日：每天指定时间执行
     - 每周：每周指定星期和时间执行
     - 每月：每月指定日期和时间执行
   - 任务控制（暂停、恢复、删除）
   - 显示下次执行和上次执行时间
   - 执行历史追踪

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
│   │   └── schemas.py     # 预定义金融实体（8个表）
│   ├── validators/        # 数据验证模块
│   │   └── data_validator.py   # 数据验证器
│   ├── output/            # 数据输出模块
│   │   └── exporter.py    # 数据导出器
│   ├── analysis/          # 依赖分析模块 🆕
│   │   └── dependency_analyzer.py   # 表依赖关系分析器
│   ├── visualization/     # 可视化模块 🆕
│   │   └── relationship_visualizer.py  # 关系图可视化器
│   └── core/              # 核心应用模块
│       ├── app.py         # 主应用类
│       └── progress_monitor.py  # 进度监控器 🆕
├── sql/                   # SQL脚本 🆕
│   ├── schema.sql         # 数据库表结构定义
│   ├── test_data.sql      # 测试数据
│   ├── full_setup.sql     # 完整安装脚本
│   ├── sample_ddl.sql     # DDL导入示例（电商系统）🆕
│   └── README.md          # SQL使用说明
├── docker/                # Docker配置
│   └── README.md          # Docker使用指南
├── tools/                 # 工具脚本
│   └── generate_sql_inserts.py  # Python数据转SQL工具
├── examples/              # 示例代码
│   ├── basic_example.py   # 基础示例
│   ├── new_entities_example.py  # 新实体示例 🆕
│   ├── custom_table_example.py  # 自定义表示例
│   └── visualization_example.py  # 可视化和依赖分析示例 🆕
├── tests/                 # 单元测试
│   ├── test_new_entities.py  # 新实体测试
│   └── test_new_features.py  # 新功能测试 🆕
├── output/                # 输出目录
├── webapp.py              # Web应用基础版
├── webapp_pro.py          # Web应用专业版 🆕
├── cli.py                 # 命令行工具
├── docker-compose.yml     # Docker Compose配置
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

### ✅ 已完成功能

**核心功能**：
- [x] 元数据驱动的数据生成引擎
- [x] 8种预定义金融实体（客户、账户、交易、贷款、信用卡、债券、基金、衍生品）
- [x] 数据库连接和元数据提取（支持5种主流数据库）
- [x] 数据质量分析和profiling
- [x] 多格式导出（CSV、JSON、Excel）
- [x] **SQL DDL导入** 🆕 - 从CREATE TABLE语句导入表结构，支持：
  - 解析标准SQL DDL语法（MySQL、PostgreSQL等）
  - 自动映射SQL类型到系统字段类型
  - 提取约束（主键、外键、唯一键）
  - Web界面DDL导入功能
  - 支持单表和多表批量导入
- [x] **增量数据生成** 🆕 - 在现有数据基础上智能追加新数据，支持：
  - 自动分析现有数据特征（ID范围、日期范围、数值分布）
  - ID自动递增（从最大值继续）
  - 日期自动延续（在最近日期之后）
  - 数值范围智能扩展
  - 保持数据连续性和一致性

**Web界面**：
- [x] 基础版Web界面（快速开始）
- [x] 专业版Web应用（完整功能）
- [x] 用户认证系统（注册、登录、会话管理）
- [x] 配置保存和管理
- [x] 历史记录追踪和统计

**高级功能（专业版）**：
- [x] **批量处理系统** - 支持同时处理多个表，包括：
  - 后台任务处理引擎
  - 实时进度追踪
  - 任务管理UI（创建、查看、取消、删除）
  - 每表结果详情

- [x] **数据可视化仪表板** - 多维度数据质量可视化，包括：
  - 折线图：7天操作历史趋势
  - 柱状图：数据质量概览
  - 饼图：字段完整性分布
  - 雷达图：多维质量评分
  - 统计卡片：关键指标展示

- [x] **定时任务调度** - 灵活的自动化任务系统，包括：
  - APScheduler集成
  - 4种调度模式（一次性、每日、每周、每月）
  - 任务管理UI（创建、暂停、恢复、删除）
  - 执行历史记录

**数据质量规则**（已实现12种规则）：
- [x] 完整性规则、唯一性规则、范围规则
- [x] 模式规则、一致性规则、引用完整性规则
- [x] **时序规则** 🆕 - 验证日期/时间字段的先后顺序
- [x] **长度规则** 🆕 - 验证字符串长度范围
- [x] **格式规则** 🆕 - 验证特定格式（邮箱、电话、身份证等）
- [x] **枚举规则** 🆕 - 验证值是否在允许列表中
- [x] **分布规则** 🆕 - 验证数值字段的统计分布
- [x] **关联性规则** 🆕 - 验证字段间的相关性（正相关、负相关、无关）

**工具和部署**：
- [x] Docker Compose一键部署
- [x] SQL脚本和测试数据
- [x] 交互式命令行工具
- [x] Python转SQL工具

### 📋 计划中功能

**数据增强**：
- [ ] 支持自定义数据生成策略
- [ ] 智能数据模式识别
- [ ] 数据模板库

**可视化增强**：
- [ ] 数据关系图可视化
- [ ] 表间关系依赖分析
- [ ] 生成过程实时监控

**协作功能**：
- [ ] API令牌认证
- [ ] 团队协作功能
- [ ] 权限管理系统
- [ ] 数据导入功能

**集成和通知**：
- [ ] Webhook通知
- [ ] 邮件报告
- [ ] 更多导出格式支持

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请提交Issue。
