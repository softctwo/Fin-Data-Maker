# Docker 快速启动指南

使用Docker Compose快速启动MySQL测试环境，并自动导入测试数据。

## 🚀 快速开始

### 1. 启动服务

```bash
# 在项目根目录执行
docker-compose up -d
```

这将启动：
- **MySQL 8.0** 数据库服务（端口 3306）
- **Adminer** Web管理界面（端口 8080）

### 2. 自动初始化

`docker-compose.yml` 配置了自动初始化：
- 自动执行 `sql/` 目录下的所有 `.sql` 文件
- 按字母顺序执行：`full_setup.sql` → `schema.sql` → `test_data.sql`

**注意**: 由于文件会按字母顺序执行，建议只保留 `full_setup.sql` 在 `sql/` 目录，或者重命名文件确保正确的执行顺序。

### 3. 验证数据

```bash
# 方式一：使用mysql命令行
docker exec -it fin-data-mysql mysql -uroot -pfindata123 fin_data_maker

# 进入MySQL后执行
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema='fin_data_maker';
```

```bash
# 方式二：使用Web界面
# 浏览器访问 http://localhost:8080
# 服务器: mysql
# 用户名: root
# 密码: findata123
# 数据库: fin_data_maker
```

## 🔧 配置说明

### 环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| MYSQL_ROOT_PASSWORD | findata123 | root用户密码 |
| MYSQL_DATABASE | fin_data_maker | 默认数据库名 |
| MYSQL_USER | finuser | 应用用户名 |
| MYSQL_PASSWORD | finpass123 | 应用用户密码 |

### 端口映射

| 服务 | 容器端口 | 主机端口 |
|------|---------|---------|
| MySQL | 3306 | 3306 |
| Adminer | 8080 | 8080 |

### 数据持久化

数据存储在Docker卷 `mysql_data` 中，即使容器删除，数据也不会丢失。

## 📝 常用命令

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看MySQL日志
docker-compose logs mysql

# 实时跟踪日志
docker-compose logs -f mysql
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启MySQL服务
docker-compose restart mysql
```

### 停止服务

```bash
# 停止但保留容器
docker-compose stop

# 停止并删除容器（保留数据卷）
docker-compose down

# 停止并删除所有（包括数据卷）
docker-compose down -v
```

### 连接到MySQL

```bash
# 使用root用户连接
docker exec -it fin-data-mysql mysql -uroot -pfindata123 fin_data_maker

# 使用应用用户连接
docker exec -it fin-data-mysql mysql -ufinuser -pfinpass123 fin_data_maker
```

### 导入额外的SQL文件

```bash
# 方式一：从主机导入
docker exec -i fin-data-mysql mysql -uroot -pfindata123 fin_data_maker < your_file.sql

# 方式二：复制到容器内再导入
docker cp your_file.sql fin-data-mysql:/tmp/
docker exec -it fin-data-mysql mysql -uroot -pfindata123 fin_data_maker -e "source /tmp/your_file.sql"
```

### 导出数据

```bash
# 导出整个数据库
docker exec fin-data-mysql mysqldump -uroot -pfindata123 fin_data_maker > backup.sql

# 导出特定表
docker exec fin-data-mysql mysqldump -uroot -pfindata123 fin_data_maker bond fund derivative > entities_backup.sql
```

## 🔍 使用Adminer管理界面

### 访问方式

1. 启动服务后，浏览器访问: http://localhost:8080
2. 登录信息：
   - **系统**: MySQL
   - **服务器**: mysql
   - **用户名**: root
   - **密码**: findata123
   - **数据库**: fin_data_maker

### 功能特性

- 📊 可视化表结构查看
- 🔍 SQL查询执行
- 📝 数据编辑（增删改查）
- 📤 数据导入/导出
- 🎨 美观的界面设计

## 🛠️ 故障排查

### 问题1: 端口已被占用

```
Error: bind: address already in use
```

**解决方案**: 修改 `docker-compose.yml` 中的端口映射

```yaml
ports:
  - "3307:3306"  # 使用3307代替3306
```

### 问题2: 容器无法启动

```bash
# 查看详细日志
docker-compose logs mysql

# 检查容器状态
docker ps -a | grep fin-data-mysql
```

### 问题3: 数据没有自动导入

```bash
# 检查sql目录是否正确挂载
docker inspect fin-data-mysql | grep Mounts -A 20

# 手动导入
docker exec -i fin-data-mysql mysql -uroot -pfindata123 fin_data_maker < sql/full_setup.sql
```

### 问题4: 字符集问题

```bash
# 检查字符集配置
docker exec -it fin-data-mysql mysql -uroot -pfindata123 \
  -e "SHOW VARIABLES LIKE 'character%';"

# 应该显示 utf8mb4
```

## 🔐 安全建议

### 生产环境配置

如果用于生产环境，请修改以下配置：

1. **修改密码**:
```yaml
environment:
  MYSQL_ROOT_PASSWORD: <strong_password>
  MYSQL_PASSWORD: <strong_password>
```

2. **限制网络访问**:
```yaml
ports:
  - "127.0.0.1:3306:3306"  # 只允许本地访问
```

3. **使用secrets管理密码** (Docker Swarm):
```yaml
secrets:
  mysql_root_password:
    external: true
  mysql_password:
    external: true
```

## 📚 相关文档

- [SQL脚本说明](../sql/README.md)
- [主项目文档](../Readme.md)
- [Docker官方文档](https://docs.docker.com/)
- [MySQL Docker镜像](https://hub.docker.com/_/mysql)

## 💡 高级用法

### 性能优化

在 `docker-compose.yml` 中添加性能参数：

```yaml
command:
  - --character-set-server=utf8mb4
  - --collation-server=utf8mb4_unicode_ci
  - --default-authentication-plugin=mysql_native_password
  - --max-connections=200
  - --innodb-buffer-pool-size=512M
  - --innodb-log-file-size=128M
```

### 使用自定义配置文件

创建 `docker/mysql.cnf`:
```ini
[mysqld]
max_connections=200
innodb_buffer_pool_size=512M
```

修改 `docker-compose.yml`:
```yaml
volumes:
  - ./docker/mysql.cnf:/etc/mysql/conf.d/custom.cnf:ro
```

### 主从复制配置

参考 [MySQL主从复制文档](https://dev.mysql.com/doc/refman/8.0/en/replication.html)

## 🐛 问题反馈

如有问题，请提交 Issue 到 [GitHub仓库](https://github.com/softctwo/Fin-Data-Maker/issues)
