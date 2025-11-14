# SQL 脚本使用说明

本目录包含用于创建金融数据测试环境的SQL脚本。

## 📁 文件说明

### 1. `schema.sql` - 数据库表结构定义
包含所有表的DDL语句，定义了8个金融实体表：

| 表名 | 说明 | 字段数 |
|------|------|--------|
| customer | 客户信息表 | 12 |
| account | 账户信息表 | 10 |
| transaction | 交易流水表 | 11 |
| loan | 贷款信息表 | 12 |
| credit_card | 信用卡信息表 | 12 |
| **bond** | **债券信息表** | 15 |
| **fund** | **基金信息表** | 17 |
| **derivative** | **衍生品信息表** | 18 |

### 2. `test_data.sql` - 测试数据
包含完整的测试数据INSERT语句：

- **10条** 客户数据（个人和企业）
- **10条** 债券数据（国债、公司债、金融债等）
- **10条** 基金数据（股票型、混合型、货币型等）
- **15条** 衍生品数据（期货、期权、互换）
- **3条** 账户数据（示例）

### 3. `full_setup.sql` - 完整安装脚本
= `schema.sql` + `test_data.sql` 的合并版本，适合一次性执行。

## 🚀 快速开始

### 方式一：使用完整脚本（推荐）
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS fin_data_maker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行完整安装脚本
mysql -u root -p fin_data_maker < full_setup.sql
```

### 方式二：分步执行
```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS fin_data_maker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. 创建表结构
mysql -u root -p fin_data_maker < schema.sql

# 3. 插入测试数据
mysql -u root -p fin_data_maker < test_data.sql
```

### 方式三：使用Docker MySQL
```bash
# 启动MySQL容器
docker run --name fin-mysql \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=fin_data_maker \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 等待MySQL启动完成（约10秒）
sleep 10

# 导入SQL脚本
docker exec -i fin-mysql mysql -uroot -pyourpassword fin_data_maker < full_setup.sql

# 验证数据
docker exec -it fin-mysql mysql -uroot -pyourpassword fin_data_maker \
  -e "SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema='fin_data_maker';"
```

## 📊 数据验证

执行以下SQL验证数据是否导入成功：

```sql
-- 查看所有表的记录数
SELECT
    '客户数据' AS 表名, COUNT(*) AS 记录数 FROM customer
UNION ALL
SELECT '账户数据', COUNT(*) FROM account
UNION ALL
SELECT '交易数据', COUNT(*) FROM transaction
UNION ALL
SELECT '贷款数据', COUNT(*) FROM loan
UNION ALL
SELECT '信用卡数据', COUNT(*) FROM credit_card
UNION ALL
SELECT '债券数据', COUNT(*) FROM bond
UNION ALL
SELECT '基金数据', COUNT(*) FROM fund
UNION ALL
SELECT '衍生品数据', COUNT(*) FROM derivative;
```

预期输出：
```
+--------------+----------+
| 表名         | 记录数   |
+--------------+----------+
| 客户数据     |       10 |
| 账户数据     |        3 |
| 交易数据     |        0 |
| 贷款数据     |        0 |
| 信用卡数据   |        0 |
| 债券数据     |       10 |
| 基金数据     |       10 |
| 衍生品数据   |       15 |
+--------------+----------+
```

## 🔍 示例查询

### 查询债券信息
```sql
SELECT
    bond_code AS 债券代码,
    bond_name AS 债券名称,
    bond_type AS 债券类型,
    coupon_rate AS 票面利率,
    credit_rating AS 信用评级,
    status AS 状态
FROM bond
WHERE status = '正常交易'
ORDER BY credit_rating DESC, coupon_rate DESC;
```

### 查询基金信息
```sql
SELECT
    fund_code AS 基金代码,
    fund_name AS 基金名称,
    fund_type AS 基金类型,
    net_value AS 单位净值,
    fund_size AS 规模_亿元,
    risk_level AS 风险等级
FROM fund
WHERE status = '运作中'
ORDER BY fund_size DESC;
```

### 查询衍生品信息
```sql
SELECT
    contract_code AS 合约代码,
    contract_name AS 合约名称,
    derivative_type AS 衍生品类型,
    underlying_asset_type AS 标的资产类型,
    exchange AS 交易所,
    status AS 状态
FROM derivative
WHERE status = '交易中'
ORDER BY derivative_type, exchange;
```

### 关联查询：债券发行人信息
```sql
SELECT
    b.bond_code AS 债券代码,
    b.bond_name AS 债券名称,
    b.bond_type AS 债券类型,
    c.customer_name AS 发行人,
    c.customer_type AS 发行人类型,
    b.coupon_rate AS 票面利率,
    b.credit_rating AS 信用评级
FROM bond b
JOIN customer c ON b.issuer_id = c.customer_id
WHERE b.status = '正常交易'
ORDER BY b.credit_rating DESC, b.coupon_rate DESC;
```

### 关联查询：基金经理信息
```sql
SELECT
    f.fund_code AS 基金代码,
    f.fund_name AS 基金名称,
    f.fund_type AS 基金类型,
    c.customer_name AS 基金经理,
    f.net_value AS 单位净值,
    f.fund_size AS 规模_亿元,
    f.risk_level AS 风险等级
FROM fund f
JOIN customer c ON f.fund_manager_id = c.customer_id
WHERE f.status = '运作中'
ORDER BY f.fund_size DESC;
```

## 🛠️ 数据库兼容性

- **MySQL**: 5.7+ (推荐 8.0+)
- **MariaDB**: 10.3+
- **字符集**: UTF-8MB4（支持中文和emoji）
- **存储引擎**: InnoDB（支持外键约束和事务）

## 📝 注意事项

1. **外键约束**: 表之间存在外键关系，删除数据时需要注意顺序
2. **字符集**: 确保数据库字符集为 `utf8mb4` 以正确显示中文
3. **数据清理**: `schema.sql` 中包含 `DROP TABLE IF EXISTS` 语句，会删除同名表
4. **权限要求**: 执行用户需要 CREATE、INSERT、SELECT 权限

## 🔄 数据清理

如需重新导入数据，执行以下命令：

```sql
-- 方式一：删除所有表
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS derivative;
DROP TABLE IF EXISTS fund;
DROP TABLE IF EXISTS bond;
DROP TABLE IF EXISTS credit_card;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS transaction;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS customer;
SET FOREIGN_KEY_CHECKS = 1;

-- 然后重新执行 full_setup.sql

-- 方式二：删除整个数据库
DROP DATABASE IF EXISTS fin_data_maker;
CREATE DATABASE fin_data_maker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📚 相关文档

- [Fin-Data-Maker 主文档](../Readme.md)
- [新实体使用示例](../examples/new_entities_example.py)
- [实体定义源码](../src/financial/schemas.py)

## 💡 扩展建议

如需更多测试数据，可以：

1. **使用Python脚本生成**:
   ```bash
   cd ..
   PYTHONPATH=. python examples/new_entities_example.py
   ```

2. **使用在线SQL生成工具**:
   - [Mockaroo](https://www.mockaroo.com/)
   - [GenerateData](https://www.generatedata.com/)

3. **修改测试数据脚本**:
   复制 `test_data.sql` 中的INSERT语句，修改数据后重新执行

## 🐛 问题排查

### 问题1: 字符集错误
```
Error: Incorrect string value: '\xE5\x80\xBA\xE5\x88\xB8...'
```
**解决方案**: 确保数据库使用 UTF8MB4 字符集
```sql
ALTER DATABASE fin_data_maker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题2: 外键约束错误
```
Error: Cannot add or update a child row: a foreign key constraint fails
```
**解决方案**: 确保先插入父表数据（customer），再插入子表数据（bond, fund）

### 问题3: 表已存在
```
Error: Table 'bond' already exists
```
**解决方案**: 脚本已包含 `DROP TABLE IF EXISTS`，如仍有问题，手动删除表或数据库

## 📞 支持

如有问题，请提交 Issue 到 [GitHub仓库](https://github.com/softctwo/Fin-Data-Maker/issues)
