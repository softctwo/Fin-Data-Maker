
# 高级功能指南

## 概述

Fin-Data-Maker专业版新增了以下高级功能：

1. ✅ **用户认证系统** - 安全的用户登录和权限管理
2. ✅ **配置保存** - 保存和重用数据生成配置
3. ✅ **历史记录** - 完整的操作历史追踪
4. 🚧 **批量处理** - 同时处理多个表（下个版本）
5. 🚧 **可视化图表** - 数据质量可视化展示（下个版本）
6. 🚧 **定时任务** - 自动化数据生成（下个版本）

## 1. 用户认证系统

### 功能特点

- **用户注册**：支持新用户自助注册
- **安全登录**：密码加密存储（使用Werkzeug）
- **会话管理**：基于Flask-Login的会话管理
- **记住我**：可选择长期保持登录状态

### 使用方法

#### 注册新账户

```bash
# 访问注册页面
http://localhost:5000/auth/register

# 填写信息
- 用户名：至少3个字符
- 邮箱：有效的邮箱地址
- 密码：至少6个字符
- 确认密码：必须与密码一致
```

#### 登录系统

```bash
# 访问登录页面
http://localhost:5000/auth/login

# 使用默认管理员账户
用户名：admin
密码：admin123

# 或使用自己注册的账户
```

#### 登出系统

点击界面右上角的"登出"按钮即可安全退出。

### 数据模型

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
```

### API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/register` | POST | 注册新用户 |
| `/auth/login` | POST | 用户登录 |
| `/auth/logout` | GET | 用户登出 |

## 2. 配置保存和管理

### 功能特点

- **配置保存**：保存数据库连接和生成参数
- **配置重用**：一键加载已保存的配置
- **配置管理**：查看、编辑、删除配置
- **多配置支持**：为不同场景创建多个配置

### 使用方法

#### 保存配置

```javascript
// 在完成数据源连接和表选择后
POST /api/configs
{
    "name": "生产环境MySQL",
    "description": "生产数据库配置",
    "db_config": {
        "type": "mysql",
        "host": "prod.db.example.com",
        "port": 3306,
        "database": "production"
    },
    "table_name": "customers",
    "generation_config": {
        "count": 1000,
        "validate": true,
        "seed": 42
    }
}
```

#### 加载配置

```javascript
// 获取所有配置
GET /api/configs

// 返回示例
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "生产环境MySQL",
            "description": "生产数据库配置",
            "created_at": "2024-01-15T10:30:00",
            ...
        }
    ]
}
```

#### 删除配置

```javascript
DELETE /api/configs/1
```

### 数据模型

```python
class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    db_config = db.Column(db.Text)  # JSON
    table_name = db.Column(db.String(100))
    generation_config = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
```

### 配置示例

```json
{
    "name": "客户表测试数据配置",
    "description": "用于UAT环境的客户测试数据",
    "db_config": {
        "type": "mysql",
        "host": "uat-db.company.com",
        "port": 3306,
        "database": "uat_crm",
        "username": "test_user"
    },
    "table_name": "customers",
    "generation_config": {
        "count": 5000,
        "seed": 42,
        "validate": true,
        "sample_size": 1000,
        "strictness": "medium"
    }
}
```

## 3. 历史记录查看

### 功能特点

- **完整记录**：记录所有操作（连接、生成、导出等）
- **详细信息**：包含操作时间、状态、详情
- **统计分析**：按类型和日期统计
- **分页查看**：支持大量历史记录

### 使用方法

#### 查看历史记录

```javascript
// 获取历史记录（分页）
GET /api/histories?page=1&per_page=20

// 返回示例
{
    "success": true,
    "data": [
        {
            "id": 100,
            "operation_type": "generate",
            "table_name": "customers",
            "record_count": 1000,
            "status": "success",
            "created_at": "2024-01-15T14:30:00"
        }
    ],
    "total": 150,
    "page": 1,
    "per_page": 20
}
```

#### 查看统计信息

```javascript
// 获取最近7天统计
GET /api/histories/stats

// 返回示例
{
    "success": true,
    "data": {
        "by_type": {
            "connect": 15,
            "generate": 50,
            "export": 50
        },
        "by_date": {
            "2024-01-15": 20,
            "2024-01-14": 18,
            "2024-01-13": 15
        }
    }
}
```

### 数据模型

```python
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    operation_type = db.Column(db.String(50))
    table_name = db.Column(db.String(100))
    record_count = db.Column(db.Integer)
    status = db.Column(db.String(20))
    details = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime)
```

### 操作类型

| 类型 | 说明 |
|------|------|
| `connect` | 数据库连接 |
| `extract` | 提取表结构 |
| `profile` | 数据质量分析 |
| `generate` | 生成测试数据 |
| `export` | 导出数据 |

## 4. 批量处理多个表（计划中）

### 功能设计

```python
# 批量处理接口
POST /api/batch/process
{
    "tables": ["customers", "orders", "products"],
    "operation": "generate",
    "config": {
        "count": 1000,
        "validate": true
    }
}

# 批量进度查询
GET /api/batch/status/{batch_id}
```

### 使用场景

- 一次性生成多个关联表的数据
- 保持表间关系的一致性
- 提高批量处理效率

## 5. 数据质量可视化图表（计划中）

### 功能设计

使用Chart.js实现可视化：

```html
<!-- 完整性趋势图 -->
<canvas id="completenessChart"></canvas>

<!-- 唯一性分布图 -->
<canvas id="uniquenessChart"></canvas>

<!-- 数据质量雷达图 -->
<canvas id="qualityRadarChart"></canvas>
```

### 图表类型

- **柱状图**：各字段完整性对比
- **折线图**：数据质量趋势
- **饼图**：数据分布统计
- **雷达图**：综合质量评分

## 6. 定时任务调度（计划中）

### 功能设计

使用APScheduler实现定时任务：

```python
class ScheduledTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    config_id = db.Column(db.Integer)
    schedule_type = db.Column(db.String(20))  # once, daily, weekly
    schedule_time = db.Column(db.String(50))
    status = db.Column(db.String(20))
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
```

### 使用场景

- **每日生成**：定时生成测试数据
- **定期更新**：按计划更新测试环境
- **自动备份**：定时导出数据备份

### 调度示例

```python
# 每天凌晨2点生成数据
scheduler.add_job(
    func=generate_data_task,
    trigger=CronTrigger(hour=2, minute=0),
    id='daily_generation',
    replace_existing=True
)
```

## 数据库架构

```
┌─────────────┐
│    User     │
│  (用户表)   │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│   Config    │  │   History   │
│  (配置表)   │  │ (历史记录)  │
└──────┬──────┘  └─────────────┘
       │
       ▼
┌─────────────┐
│ScheduledTask│
│ (定时任务)  │
└─────────────┘
```

## 安全考虑

### 密码安全

- ✅ 使用Werkzeug加密存储
- ✅ 密码长度限制（最少6个字符）
- ✅ 密码哈希算法：pbkdf2:sha256

### 会话安全

- ✅ 使用Flask-Login管理会话
- ✅ 支持"记住我"功能
- ✅ 自动会话过期

### 建议措施

对于生产环境，建议：

1. 使用HTTPS加密传输
2. 设置强密码策略
3. 启用双因素认证
4. 定期更换密钥
5. 限制登录尝试次数
6. 记录所有操作日志

## 性能优化

### 数据库索引

```sql
-- 为常用查询添加索引
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_config_user ON configs(user_id);
CREATE INDEX idx_history_user_created ON histories(user_id, created_at);
```

### 缓存策略

```python
# 使用Flask-Caching缓存配置
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def get_user_configs(user_id):
    return Config.query.filter_by(user_id=user_id).all()
```

## 故障排查

### 数据库连接问题

```bash
# 检查数据库文件
ls -la fin_data_maker.db

# 重新创建数据库
python -c "from webapp_pro import app, db; app.app_context().push(); db.create_all()"
```

### 认证问题

```bash
# 重置管理员密码
python -c "from webapp_pro import app, db, User; \
app.app_context().push(); \
admin = User.query.filter_by(username='admin').first(); \
admin.set_password('new_password'); \
db.session.commit()"
```

## 下一步计划

- [ ] 完善批量处理功能
- [ ] 添加可视化图表
- [ ] 实现定时任务调度
- [ ] 添加数据导入功能
- [ ] 支持自定义规则配置
- [ ] 添加API令牌认证
- [ ] 实现团队协作功能

## 反馈和建议

如有问题或建议，请通过以下方式反馈：
- GitHub Issues
- 邮件：support@findatamaker.com
