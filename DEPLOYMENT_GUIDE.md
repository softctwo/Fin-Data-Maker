# 🚀 Fin-Data-Maker 部署指南

**版本**: v2.0
**更新日期**: 2025-11-14
**适用环境**: 开发/测试/生产

---

## 📋 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [完整安装](#完整安装)
4. [Web应用部署](#web应用部署)
5. [数据库配置](#数据库配置)
6. [生产环境配置](#生产环境配置)
7. [故障排查](#故障排查)

---

## 📦 系统要求

### 最小要求（核心功能）

| 组件 | 要求 |
|------|------|
| Python | 3.8+ |
| 内存 | 512MB |
| 磁盘 | 100MB |

**依赖包**:
```
faker>=20.0.0
pyyaml>=6.0
pandas>=2.0.0
openpyxl>=3.1.0
python-dateutil>=2.8.0
```

### 完整要求（所有功能）

| 组件 | 要求 |
|------|------|
| Python | 3.8+ |
| 内存 | 2GB+ |
| 磁盘 | 500MB |
| 数据库 | MySQL 5.7+ / PostgreSQL 10+ (可选) |

**完整依赖**:
```
所有核心依赖 +
sqlalchemy>=2.0.0
pymysql>=1.1.0 (MySQL)
psycopg2-binary>=2.9.0 (PostgreSQL)
flask>=3.0.0
flask-cors>=4.0.0
flask-login>=0.6.3
flask-sqlalchemy>=3.1.0
werkzeug>=3.0.0
apscheduler>=3.10.0
```

---

## 🚀 快速开始

### 方式一：Docker部署（推荐）

**适用场景**: 快速测试、演示、开发环境

```bash
# 1. 克隆项目
git clone https://github.com/your-org/Fin-Data-Maker.git
cd Fin-Data-Maker

# 2. 启动服务
docker-compose up -d

# 3. 访问服务
# MySQL: localhost:3306 (root/findata123)
# Adminer: http://localhost:8080

# 4. 验证数据
docker exec -it fin-data-mysql mysql -uroot -pfindata123 fin_data_maker \
  -e "SELECT COUNT(*) as bond_count FROM bond;"
```

### 方式二：Python脚本

**适用场景**: 自动化、集成测试、CI/CD

```bash
# 1. 安装核心依赖
pip install faker pyyaml pandas openpyxl python-dateutil

# 2. 运行示例
python examples/new_entities_example.py

# 3. 查看输出
ls -lh output/
```

### 方式三：SQL直接导入

**适用场景**: 已有数据库、快速数据导入

```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE fin_data_maker CHARACTER SET utf8mb4;"

# 2. 导入数据
mysql -u root -p fin_data_maker < sql/full_setup.sql

# 3. 验证
mysql -u root -p fin_data_maker -e "SHOW TABLES;"
```

---

## 🔧 完整安装

### Step 1: 环境准备

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### Step 2: 安装依赖

#### 2.1 安装核心依赖（必需）

```bash
pip install faker pyyaml pandas openpyxl python-dateutil
```

#### 2.2 安装Web功能依赖（可选）

```bash
pip install flask flask-cors flask-login flask-sqlalchemy werkzeug
```

#### 2.3 安装数据库驱动（可选）

根据使用的数据库选择：

```bash
# MySQL
pip install pymysql sqlalchemy

# PostgreSQL
pip install psycopg2-binary sqlalchemy

# Oracle
pip install cx-Oracle sqlalchemy

# SQL Server
pip install pyodbc sqlalchemy

# SQLite（Python自带，无需安装）
```

#### 2.4 一次性安装所有依赖

```bash
pip install -r requirements.txt
```

**注意**: 如果遇到依赖冲突：

```bash
# 方法1: 忽略已安装的系统包
pip install -r requirements.txt --ignore-installed

# 方法2: 使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: 验证安装

```bash
# 运行测试
python tests/test_new_entities.py

# 预期输出
# Ran 19 tests in 0.3s
# OK
```

---

## 🌐 Web应用部署

### 基础版Web应用 (webapp.py)

**适用场景**: 单用户、内网使用、演示

#### 开发模式

```bash
# 启动应用
python webapp.py

# 访问地址
# http://localhost:5000
```

#### 生产模式（使用Gunicorn）

```bash
# 1. 安装Gunicorn
pip install gunicorn

# 2. 启动应用（4个worker进程）
gunicorn -w 4 -b 0.0.0.0:5000 webapp:app

# 3. 后台运行
nohup gunicorn -w 4 -b 0.0.0.0:5000 webapp:app > logs/webapp.log 2>&1 &
```

#### 使用systemd管理（Linux）

创建服务文件 `/etc/systemd/system/fin-data-maker.service`:

```ini
[Unit]
Description=Fin-Data-Maker Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Fin-Data-Maker
Environment="PATH=/opt/Fin-Data-Maker/venv/bin"
ExecStart=/opt/Fin-Data-Maker/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 webapp:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable fin-data-maker
sudo systemctl start fin-data-maker
sudo systemctl status fin-data-maker
```

### 专业版Web应用 (webapp_pro.py)

**适用场景**: 多用户、需要认证、配置管理

#### 初始化数据库

```bash
# 首次运行会自动创建SQLite数据库
python webapp_pro.py

# 数据库文件: instance/app.db
```

#### 配置环境变量

创建 `.env` 文件：

```bash
# Flask配置
FLASK_APP=webapp_pro.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-in-production

# 数据库配置
DATABASE_URL=sqlite:///instance/app.db

# 其他配置
MAX_CONTENT_LENGTH=16777216  # 16MB
```

#### 启动专业版

```bash
# 开发模式
python webapp_pro.py

# 生产模式
gunicorn -w 4 -b 0.0.0.0:5001 webapp_pro:app
```

### 使用Nginx反向代理

创建Nginx配置 `/etc/nginx/sites-available/fin-data-maker`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 基础版应用
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 专业版应用
    location /pro {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件
    location /static {
        alias /opt/Fin-Data-Maker/static;
        expires 30d;
    }

    # 上传文件大小限制
    client_max_body_size 16M;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/fin-data-maker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🗄️ 数据库配置

### MySQL配置

#### 1. 创建数据库和用户

```sql
-- 创建数据库
CREATE DATABASE fin_data_maker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'findata'@'localhost' IDENTIFIED BY 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON fin_data_maker.* TO 'findata'@'localhost';
FLUSH PRIVILEGES;
```

#### 2. 导入表结构

```bash
mysql -u findata -p fin_data_maker < sql/schema.sql
```

#### 3. 导入测试数据

```bash
mysql -u findata -p fin_data_maker < sql/test_data.sql
```

### PostgreSQL配置

#### 1. 创建数据库

```bash
# 切换到postgres用户
sudo -u postgres psql

# 执行SQL
CREATE DATABASE fin_data_maker ENCODING 'UTF8';
CREATE USER findata WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fin_data_maker TO findata;
\q
```

#### 2. 连接配置

```python
from src.datasource.db_connector import DatabaseConnector, DatabaseType

connector = DatabaseConnector(
    db_type=DatabaseType.POSTGRESQL,
    host='localhost',
    port=5432,
    database='fin_data_maker',
    username='findata',
    password='your_password'
)
```

### SQLite配置（用于专业版Web应用）

```bash
# 自动创建，无需手动配置
# 数据库位置: instance/app.db

# 查看数据库
sqlite3 instance/app.db ".tables"

# 备份数据库
cp instance/app.db instance/app.db.backup
```

---

## 🏭 生产环境配置

### 安全配置

#### 1. 修改默认密码

**Docker环境**:

编辑 `docker-compose.yml`:

```yaml
environment:
  MYSQL_ROOT_PASSWORD: your-strong-password
  MYSQL_PASSWORD: another-strong-password
```

**Web应用**:

编辑 `.env`:

```bash
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

#### 2. 启用HTTPS

使用Let's Encrypt:

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

Nginx配置更新:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... 其他配置
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 性能优化

#### 1. Gunicorn配置

创建 `gunicorn.conf.py`:

```python
# 绑定地址
bind = "127.0.0.1:5000"

# Worker进程数（建议：CPU核心数 * 2 + 1）
workers = 5

# Worker类型
worker_class = "sync"

# 超时时间
timeout = 120

# 日志
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程名
proc_name = "fin-data-maker"

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50
```

启动:

```bash
gunicorn -c gunicorn.conf.py webapp:app
```

#### 2. Nginx缓存配置

```nginx
# 缓存路径
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

server {
    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API响应缓存（谨慎使用）
    location /api {
        proxy_cache my_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

### 监控和日志

#### 1. 日志配置

创建日志目录:

```bash
mkdir -p logs
chmod 755 logs
```

应用日志配置:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. 日志轮转

创建 `/etc/logrotate.d/fin-data-maker`:

```
/opt/Fin-Data-Maker/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload fin-data-maker
    endscript
}
```

### 备份策略

#### 1. 数据库备份

创建备份脚本 `scripts/backup_db.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/fin-data-maker"

# 创建备份目录
mkdir -p $BACKUP_DIR

# MySQL备份
mysqldump -u findata -p'your_password' fin_data_maker \
  | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 保留最近30天的备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

设置cron任务:

```bash
# 每天凌晨2点备份
0 2 * * * /opt/Fin-Data-Maker/scripts/backup_db.sh
```

#### 2. 配置文件备份

```bash
# 备份配置
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env \
  nginx.conf \
  gunicorn.conf.py

# 上传到远程服务器（可选）
scp config_backup_*.tar.gz backup@remote:/backup/
```

---

## 🔍 故障排查

### 常见问题

#### 问题1: 依赖安装失败

**错误**:
```
ERROR: Cannot uninstall blinker 1.7.0
```

**解决方案**:
```bash
pip install --upgrade --ignore-installed blinker flask werkzeug
```

#### 问题2: PyMySQL导入错误

**错误**:
```
ModuleNotFoundError: No module named '_cffi_backend'
```

**解决方案**:
```bash
# 使用纯Python的MySQL驱动
pip uninstall pymysql
pip install pymysql

# 或者安装依赖
apt-get install python3-cffi
```

#### 问题3: Web应用无法启动

**错误**:
```
Address already in use
```

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5000

# 杀死进程
kill -9 <PID>

# 或使用不同端口
python webapp.py --port 5001
```

#### 问题4: 数据库连接失败

**错误**:
```
Can't connect to MySQL server
```

**解决方案**:
```bash
# 检查数据库是否运行
systemctl status mysql

# 检查防火墙
sudo ufw allow 3306

# 检查bind-address配置
grep bind-address /etc/mysql/mysql.conf.d/mysqld.cnf
# 应该是: bind-address = 0.0.0.0
```

#### 问题5: 权限错误

**错误**:
```
Permission denied: 'output/data.csv'
```

**解决方案**:
```bash
# 创建输出目录
mkdir -p output

# 设置权限
chmod 755 output
chown www-data:www-data output
```

### 调试模式

启用Flask调试:

```python
# webapp.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**警告**: 生产环境务必关闭debug=False

### 日志检查

```bash
# 查看应用日志
tail -f logs/app.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看systemd日志
journalctl -u fin-data-maker -f
```

---

## 📚 参考资料

### 相关文档

- [README.md](Readme.md) - 项目主文档
- [COMPREHENSIVE_TEST_REPORT.md](COMPREHENSIVE_TEST_REPORT.md) - 测试报告
- [TEST_REPORT.md](TEST_REPORT.md) - 详细测试结果
- [docker/README.md](docker/README.md) - Docker使用指南
- [sql/README.md](sql/README.md) - SQL脚本说明

### 外部资源

- [Flask文档](https://flask.palletsprojects.com/)
- [Gunicorn文档](https://docs.gunicorn.org/)
- [Nginx文档](https://nginx.org/en/docs/)
- [Docker文档](https://docs.docker.com/)

---

## 🆘 获取帮助

### 问题反馈

如遇到问题，请提供以下信息：

1. 操作系统和Python版本
2. 完整的错误信息
3. 相关配置文件
4. 复现步骤

提交Issue: https://github.com/your-org/Fin-Data-Maker/issues

### 社区支持

- 📧 Email: support@example.com
- 💬 Slack: [加入频道]
- 📖 Wiki: [文档中心]

---

**最后更新**: 2025-11-14
**维护者**: Development Team
**许可证**: MIT
