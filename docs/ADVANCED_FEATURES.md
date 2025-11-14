
# 高级功能指南

## 概述

Fin-Data-Maker专业版新增了以下高级功能：

1. ✅ **用户认证系统** - 安全的用户登录和权限管理
2. ✅ **配置保存** - 保存和重用数据生成配置
3. ✅ **历史记录** - 完整的操作历史追踪
4. ✅ **批量处理** - 同时处理多个表，支持进度追踪
5. ✅ **可视化图表** - 数据质量可视化展示，包含多种图表类型
6. ✅ **定时任务** - 自动化数据生成调度

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

## 4. 批量处理多个表

### 功能特点

- **批量任务管理**：创建、监控、取消批量处理任务
- **进度追踪**：实时查看批量处理进度
- **详细结果**：每个表的处理状态和结果
- **并发处理**：后台线程异步处理，不阻塞主线程
- **失败恢复**：单个表失败不影响其他表的处理

### 使用方法

#### 创建批量任务

```javascript
POST /api/batch/create
{
    "name": "批量生成测试数据",
    "description": "为UAT环境生成多个表的测试数据",
    "db_config": {
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "username": "user",
        "password": "password"
    },
    "tables": ["customers", "orders", "products"],
    "generation_config": {
        "count": 1000,
        "validate": true,
        "analyze_quality": false,
        "seed": 42
    }
}

// 返回示例
{
    "success": true,
    "message": "批量任务已创建",
    "data": {
        "id": 1,
        "name": "批量生成测试数据",
        "status": "running",
        "total_tables": 3,
        "completed_tables": 0,
        "progress": 0
    }
}
```

#### 查询批量任务进度

```javascript
GET /api/batch/status/{task_id}

// 返回示例
{
    "success": true,
    "data": {
        "id": 1,
        "status": "running",
        "total_tables": 3,
        "completed_tables": 1,
        "failed_tables": 0,
        "progress": 33,
        "results": {
            "customers": {
                "status": "success",
                "record_count": 1000,
                "validation_report": {
                    "total_rows": 1000,
                    "valid_rows": 1000,
                    "error_count": 0
                }
            },
            "orders": {
                "status": "running"
            },
            "products": {
                "status": "pending"
            }
        }
    }
}
```

#### 获取批量任务列表

```javascript
GET /api/batch/list?page=1&per_page=20
```

#### 取消批量任务

```javascript
POST /api/batch/cancel/{task_id}
```

#### 删除批量任务

```javascript
DELETE /api/batch/delete/{task_id}
```

### 数据模型

```python
class BatchTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    db_config = db.Column(db.Text)  # JSON
    tables = db.Column(db.Text)  # JSON数组
    generation_config = db.Column(db.Text)  # JSON
    status = db.Column(db.String(20))  # pending, running, completed, failed, cancelled
    total_tables = db.Column(db.Integer)
    completed_tables = db.Column(db.Integer)
    failed_tables = db.Column(db.Integer)
    progress = db.Column(db.Integer)  # 0-100
    results = db.Column(db.Text)  # JSON
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
```

### 使用场景

- 一次性生成多个关联表的数据
- 保持表间关系的一致性
- 提高批量处理效率
- 自动化测试数据准备

## 5. 数据质量可视化图表

### 功能特点

- **多种图表类型**：柱状图、折线图、饼图、雷达图
- **实时数据**：基于历史分析数据动态生成
- **交互式界面**：响应式设计，支持移动端
- **统计卡片**：关键指标一目了然
- **Chart.js驱动**：专业的图表渲染引擎

### 访问仪表板

```
http://localhost:5000/dashboard
```

### 可用图表

#### 1. 操作历史趋势图（折线图）

显示最近7天的操作统计，包括：
- 数据库连接次数
- 数据生成次数
- 数据导出次数
- 数据质量分析次数

```javascript
GET /api/charts/history-trend?days=7
```

#### 2. 数据质量总览（柱状图）

显示最近10次数据质量分析的综合得分：
- 完整性得分
- 唯一性得分
- 有效性得分

```javascript
GET /api/charts/quality-overview
```

#### 3. 字段完整性分布（饼图）

显示指定表各字段的完整性分布：

```javascript
GET /api/charts/field-completeness/{table_name}
```

#### 4. 数据质量雷达图

显示指定表的多维度质量评分：
- 完整性
- 唯一性
- 有效性
- 一致性
- 时效性

```javascript
GET /api/charts/quality-radar/{table_name}
```

### 统计卡片

仪表板顶部显示4个关键指标：
1. **已分析表数** - 总共分析过的表数量
2. **已生成记录数** - 总共生成的数据记录数
3. **平均质量得分** - 所有分析的平均质量分数
4. **批量任务数** - 创建的批量任务总数

### 图表特性

```html
<!-- 响应式设计 -->
<div class="chart-container">
    <canvas id="myChart"></canvas>
</div>

<!-- Chart.js配置 -->
<script>
new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        // ...更多配置
    }
});
</script>
```

### 使用场景

- 监控数据质量趋势
- 对比不同表的质量状况
- 发现数据质量问题
- 生成质量报告

## 6. 定时任务调度

### 功能特点

- **多种调度类型**：一次性、每日、每周、每月
- **自动执行**：基于APScheduler的后台调度
- **任务管理**：创建、暂停、恢复、删除任务
- **执行记录**：自动记录每次执行的结果
- **失败处理**：自动记录失败原因和堆栈信息
- **配置关联**：基于已保存的配置创建定时任务

### 使用方法

#### 创建定时任务

```javascript
POST /api/tasks/create
{
    "name": "每日生成客户数据",
    "config_id": 1,  // 关联的配置ID
    "schedule_type": "daily",  // once, daily, weekly, monthly
    "schedule_time": "02:00"   // 时间表达式
}

// 调度类型和时间格式：
// - once: "2024-12-31T23:59:59" (ISO格式)
// - daily: "HH:MM" (如 "02:00")
// - weekly: "weekday HH:MM" (如 "0 02:00" 表示周一凌晨2点)
// - monthly: "day HH:MM" (如 "1 02:00" 表示每月1号凌晨2点)

// 返回示例
{
    "success": true,
    "message": "定时任务已创建",
    "data": {
        "id": 1,
        "name": "每日生成客户数据",
        "schedule_type": "daily",
        "schedule_time": "02:00",
        "status": "active",
        "next_run": "2024-01-16T02:00:00"
    }
}
```

#### 获取任务列表

```javascript
GET /api/tasks/list?page=1&per_page=20

// 返回示例
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "每日生成客户数据",
            "status": "active",
            "last_run": "2024-01-15T02:00:00",
            "next_run": "2024-01-16T02:00:00"
        }
    ],
    "total": 1
}
```

#### 获取任务详情

```javascript
GET /api/tasks/{task_id}
```

#### 暂停任务

```javascript
POST /api/tasks/pause/{task_id}
```

#### 恢复任务

```javascript
POST /api/tasks/resume/{task_id}
```

#### 删除任务

```javascript
DELETE /api/tasks/delete/{task_id}
```

### 数据模型

```python
class ScheduledTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    config_id = db.Column(db.Integer, db.ForeignKey('configs.id'))
    schedule_type = db.Column(db.String(20))  # once, daily, weekly, monthly
    schedule_time = db.Column(db.String(50))  # 时间表达式
    status = db.Column(db.String(20))  # active, paused, completed, failed
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
```

### 任务执行流程

1. **创建任务** → 添加到调度器
2. **调度器触发** → 执行任务函数
3. **连接数据库** → 提取表结构
4. **生成数据** → 基于配置生成测试数据
5. **记录历史** → 保存执行结果
6. **更新状态** → 更新任务状态和下次运行时间

### 使用场景

- **每日生成**：定时生成测试数据，保持测试环境数据新鲜
- **定期更新**：按计划更新测试环境，自动化测试准备
- **自动备份**：定时导出数据备份
- **周期性测试**：定期生成数据用于性能测试
- **定时刷新**：定期刷新开发环境数据

### 调度器架构

系统使用APScheduler作为后台调度引擎：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 创建调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 添加任务
scheduler.add_job(
    func=execute_task,
    trigger=CronTrigger(hour=2, minute=0),
    id='task_1',
    replace_existing=True
)
```

### 注意事项

1. **时区设置**：所有时间使用UTC时区
2. **任务隔离**：每个任务在独立的上下文中执行
3. **失败重试**：目前不支持自动重试，需手动处理失败任务
4. **并发限制**：同一任务同时只能有一个实例运行
5. **持久化**：任务配置持久化到数据库，重启后自动加载

## 数据库架构

```
┌─────────────┐
│    User     │
│  (用户表)   │
└──────┬──────┘
       │
       ├────────────────┬────────────────┬────────────────┐
       │                │                │                │
       ▼                ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Config    │  │   History   │  │ScheduledTask│  │  BatchTask  │
│  (配置表)   │  │ (历史记录)  │  │ (定时任务)  │  │ (批量任务)  │
└──────┬──────┘  └─────────────┘  └──────┬──────┘  └─────────────┘
       │                                  │
       └──────────────────────────────────┘
                (外键关联)
```

### 表关系说明

- **User** ←→ **Config**: 一对多，一个用户可以有多个配置
- **User** ←→ **History**: 一对多，一个用户可以有多条历史记录
- **User** ←→ **ScheduledTask**: 一对多，一个用户可以有多个定时任务
- **User** ←→ **BatchTask**: 一对多，一个用户可以有多个批量任务
- **Config** ←→ **ScheduledTask**: 一对多，一个配置可以被多个定时任务使用

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

## 功能完成状态

**已完成** ✅：
- [x] 用户认证系统
- [x] 配置保存和管理
- [x] 历史记录追踪
- [x] 批量处理多个表
- [x] 数据质量可视化图表
- [x] 定时任务调度

**计划中** 📋：
- [ ] 批量处理UI界面
- [ ] 定时任务UI界面
- [ ] 数据导入功能
- [ ] 支持自定义规则配置界面
- [ ] 添加API令牌认证
- [ ] 实现团队协作功能
- [ ] 增强的权限管理
- [ ] 数据导出格式扩展
- [ ] Webhook通知
- [ ] 邮件报告

## 反馈和建议

如有问题或建议，请通过以下方式反馈：
- GitHub Issues
- 邮件：support@findatamaker.com
