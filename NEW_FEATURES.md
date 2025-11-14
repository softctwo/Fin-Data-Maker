# 新功能说明

本次更新添加了三个主要新功能，提升了系统的灵活性、易用性和安全性。

## 1. 高优先级：自定义数据生成策略

### 功能概述
允许用户创建和管理自定义数据生成策略，提供更灵活的数据生成方式，满足各种复杂的业务场景。

### 核心文件
- `src/strategies/` - 策略模块目录
  - `strategy.py` - 策略基类和注册表
  - `builtin_strategies.py` - 8种内置策略实现
  - `strategy_manager.py` - 策略管理器

### 内置策略类型

1. **顺序生成 (Sequential)** - 生成递增的序列值
2. **随机范围 (RandomRange)** - 在指定范围内生成随机值
3. **加权选择 (WeightedChoice)** - 根据权重从选项中随机选择
4. **条件生成 (Conditional)** - 根据条件生成不同的值
5. **依赖字段 (DependentField)** - 根据其他字段的值生成数据
6. **日期范围 (DateRange)** - 在指定日期范围内生成日期
7. **自定义函数 (CustomFunction)** - 使用Python表达式自定义生成逻辑
8. **分布生成 (Distribution)** - 根据统计分布生成数据（正态、均匀、指数、泊松）

### API接口

- `GET /api/strategies/types` - 获取所有可用的策略类型
- `GET /api/strategies` - 列出用户的所有策略
- `POST /api/strategies` - 创建新策略
- `PUT /api/strategies/<name>` - 更新策略
- `DELETE /api/strategies/<name>` - 删除策略

### UI界面

访问 `/strategies` 页面管理自定义策略：
- 创建新策略
- 编辑现有策略
- 删除策略
- 预览策略配置

### 使用示例

```python
from src.strategies.strategy_manager import StrategyManager
from src.strategies.strategy import StrategyContext

# 创建策略管理器
manager = StrategyManager()

# 创建顺序生成策略
manager.create_strategy(
    strategy_type='sequential',
    name='id_generator',
    description='生成ID序列',
    config={'start': 1000, 'step': 1, 'format': 'USR{:05d}'}
)

# 应用策略
context = StrategyContext(row_index=0, total_rows=100)
value = manager.apply_strategy('id_generator', context)
# 输出: USR01000
```

---

## 2. 中优先级：数据关系图可视化

### 功能概述
分析数据库表之间的关系（外键等），生成可视化的关系图，帮助用户更好地理解数据库结构。

### 核心文件
- `src/visualization/` - 可视化模块目录
  - `relationship_graph.py` - 关系图生成器

### 主要功能

1. **关系分析** - 自动识别表之间的外键关系
2. **图数据生成** - 生成适用于D3.js等库的图数据结构
3. **依赖分析** - 分析特定表的依赖和被依赖关系
4. **统计信息** - 提供关系统计、连通分量分析等
5. **层次结构** - 生成树状层次结构数据

### API接口

- `POST /api/relationships/graph` - 获取完整的数据关系图
- `GET /api/relationships/table/<table_name>` - 获取特定表的关系
- `GET /api/relationships/statistics` - 获取关系统计信息
- `POST /api/relationships/hierarchy` - 获取层次结构数据

### 使用示例

```python
from src.visualization.relationship_graph import RelationshipGraphGenerator

# 创建关系图生成器
graph_gen = RelationshipGraphGenerator()

# 添加表定义
graph_gen.add_table(customer_table)
graph_gen.add_table(order_table)
graph_gen.add_table(order_item_table)

# 生成图数据
graph_data = graph_gen.generate_graph_data()
# 返回: {'nodes': [...], 'links': [...], 'metadata': {...}}

# 获取统计信息
stats = graph_gen.get_statistics()
# 返回: {'table_count': 3, 'relationship_count': 2, ...}
```

### 返回的图数据格式

```json
{
  "nodes": [
    {
      "id": "customer",
      "name": "customer",
      "fields": [...],
      "field_count": 12,
      "primary_key": "id"
    }
  ],
  "links": [
    {
      "source": "order",
      "target": "customer",
      "source_field": "customer_id",
      "target_field": "id",
      "type": "foreign_key"
    }
  ],
  "metadata": {
    "table_count": 3,
    "relationship_count": 2
  }
}
```

---

## 3. 低优先级：API令牌认证

### 功能概述
为API接口提供基于令牌的身份认证机制，支持权限管理和过期控制，适用于企业级集成场景。

### 核心文件
- `src/web/models.py` - 添加了 `APIToken` 模型
- `src/web/auth.py` - 添加了 `token_required` 装饰器和令牌验证功能
- `sql/migration_add_api_tokens.sql` - 数据库迁移脚本

### 主要功能

1. **令牌管理** - 创建、查看、删除、启用/禁用令牌
2. **权限控制** - 基于scope的细粒度权限管理
3. **过期控制** - 支持设置令牌过期时间
4. **使用追踪** - 记录令牌最后使用时间

### 可用权限范围

- `data:generate` - 允许生成测试数据
- `data:export` - 允许导出生成的数据
- `table:read` - 允许读取表结构和元数据
- `table:write` - 允许修改表结构
- `config:read` - 允许读取配置信息
- `config:write` - 允许创建和修改配置

### API接口

- `GET /api/tokens` - 列出用户的所有令牌
- `POST /api/tokens` - 创建新令牌
- `DELETE /api/tokens/<id>` - 删除令牌
- `POST /api/tokens/<id>/toggle` - 启用/禁用令牌
- `GET /api/tokens/scopes` - 获取可用的权限范围

### 使用令牌的API示例

```bash
# 使用令牌调用API
curl -X POST http://localhost:5000/api/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"table": "customer", "count": 1000}'
```

### 在代码中使用令牌认证

```python
from src.web.auth import token_required, get_user_from_token

@app.route('/api/v1/my-endpoint', methods=['POST'])
@token_required(scopes=['data:generate', 'data:export'])
def my_api_endpoint():
    """需要 data:generate 和 data:export 权限"""
    user = get_user_from_token()
    # 处理请求...
    return jsonify({'success': True})
```

### 令牌创建示例

```python
from src.web.models import APIToken
from datetime import datetime, timedelta

# 创建一个30天后过期的令牌
token = APIToken(
    user_id=1,
    name='生产环境令牌',
    token=APIToken.generate_token(),
    description='用于生产环境数据生成',
    scopes=json.dumps(['data:generate', 'data:export']),
    expires_at=datetime.utcnow() + timedelta(days=30)
)
db.session.add(token)
db.session.commit()
```

---

## 安装和使用

### 1. 数据库迁移

如果使用SQLite（默认），Flask-SQLAlchemy会自动创建新表。如果需要手动迁移：

```bash
# 执行迁移脚本
sqlite3 fin_data_maker.db < sql/migration_add_api_tokens.sql
```

### 2. 启动应用

```bash
python webapp_pro.py
```

### 3. 访问新功能

- 策略管理：http://localhost:5000/strategies
- 令牌管理：通过API接口管理（UI待开发）
- 关系图：通过API接口获取数据（UI待开发）

---

## 待完善功能

以下功能的后端逻辑已完成，但UI界面尚未实现：

1. **关系图可视化UI** - 使用D3.js绘制交互式关系图
2. **令牌管理UI** - 在Web界面管理API令牌

这些UI可以在后续版本中完善。

---

## 技术特点

### 自定义策略模块
- **可扩展** - 易于添加新的策略类型
- **类型安全** - 使用枚举和类型注解
- **灵活配置** - 支持JSON格式的策略配置
- **状态管理** - 自动重置策略状态

### 关系图生成器
- **智能分析** - 自动识别外键关系
- **多种输出** - 支持图、矩阵、树等多种数据格式
- **性能优化** - 使用DFS算法高效分析连通分量
- **统计完整** - 提供丰富的关系统计信息

### API令牌认证
- **安全可靠** - 使用secrets模块生成高强度令牌
- **权限细粒度** - 基于scope的灵活权限控制
- **易于集成** - 简单的装饰器API
- **审计追踪** - 记录令牌使用历史

---

## 更新日志

**版本**: v1.1.0
**日期**: 2025-01-XX

### 新增
- ✅ 自定义数据生成策略系统（8种内置策略）
- ✅ 数据关系图分析和生成
- ✅ API令牌认证和权限管理
- ✅ 策略管理UI界面
- ✅ 完整的API文档和示例

### 改进
- 增强了字段生成器，支持策略上下文传递
- 优化了表生成器，支持行级上下文信息
- 扩展了数据库模型，添加APIToken表

### 待办
- ⏳ 关系图可视化UI（使用D3.js）
- ⏳ 令牌管理UI界面
- ⏳ 更多内置策略类型
- ⏳ 策略模板库

---

## 联系和反馈

如有问题或建议，请通过GitHub Issues反馈。
