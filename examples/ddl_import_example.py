"""
DDL导入示例

演示如何使用DDL解析器从SQL DDL语句导入表结构
"""

from src.parsers.ddl_parser import DDLParser, parse_ddl_to_table
from src.core.app import DataMakerApp


def example1_basic_ddl():
    """示例1: 解析基础的CREATE TABLE语句"""
    print("=" * 60)
    print("示例1: 解析基础DDL")
    print("=" * 60)

    ddl = """
    CREATE TABLE users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL,
        age INT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) COMMENT='用户表';
    """

    # 解析DDL
    table = parse_ddl_to_table(ddl)

    print(f"\n表名: {table.name}")
    print(f"描述: {table.description}")
    print(f"主键: {table.primary_key}")
    print(f"\n字段列表:")

    for field_name, field in table.fields.items():
        print(f"  - {field_name}: {field.field_type.value}")
        print(f"      必填: {field.required}, 唯一: {field.unique}")

    # 使用解析的表生成数据
    app = DataMakerApp(seed=42)
    app.add_table(table)

    data, report = app.generate_data('users', count=10)

    print(f"\n成功生成 {len(data)} 条数据")
    print(f"质量报告: {report['summary']}")


def example2_multiple_tables():
    """示例2: 解析包含多个表的DDL文件"""
    print("\n" + "=" * 60)
    print("示例2: 解析多表DDL")
    print("=" * 60)

    ddl = """
    CREATE TABLE customers (
        customer_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        email VARCHAR(100) UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) COMMENT='客户表';

    CREATE TABLE orders (
        order_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_id INT NOT NULL,
        order_amount DECIMAL(10,2) NOT NULL,
        order_status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
        order_date DATETIME NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ) COMMENT='订单表';
    """

    # 解析多个表
    parser = DDLParser()
    statements = parser._split_statements(ddl)

    tables = []
    for statement in statements:
        table = parser.parse_ddl(statement)
        tables.append(table)
        print(f"\n✓ 成功解析表: {table.name}")
        print(f"  字段数: {len(table.fields)}")
        print(f"  外键数: {len(table.foreign_keys)}")

    # 生成关联数据
    app = DataMakerApp(seed=42)

    # 添加所有表
    for table in tables:
        app.add_table(table)

    # 先生成客户数据
    customers, _ = app.generate_data('customers', count=10)
    print(f"\n生成了 {len(customers)} 个客户")

    # 生成订单数据（关联客户）
    customer_ids = [c['customer_id'] for c in customers]
    orders, _ = app.generate_with_relations(
        'orders',
        count=30,
        related_data={'customers': customer_ids}
    )
    print(f"生成了 {len(orders)} 个订单")


def example3_complex_types():
    """示例3: 解析包含复杂类型的DDL"""
    print("\n" + "=" * 60)
    print("示例3: 复杂数据类型")
    print("=" * 60)

    ddl = """
    CREATE TABLE products (
        product_id INT PRIMARY KEY AUTO_INCREMENT,
        product_code VARCHAR(50) NOT NULL UNIQUE,
        product_name VARCHAR(200) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        stock_quantity INT DEFAULT 0,
        category ENUM('electronics', 'clothing', 'food', 'books') NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        tags VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) COMMENT='产品表';
    """

    table = parse_ddl_to_table(ddl)

    print(f"\n表名: {table.name}")
    print(f"\n字段类型映射:")

    for field_name, field in table.fields.items():
        type_info = f"{field.field_type.value}"

        if field.enum_values:
            type_info += f" ({', '.join(field.enum_values)})"

        if field.max_length:
            type_info += f" (max_length={field.max_length})"

        if field.precision:
            type_info += f" (precision={field.precision})"

        print(f"  {field_name}: {type_info}")

    # 生成数据
    app = DataMakerApp(seed=42)
    app.add_table(table)

    data, report = app.generate_data('products', count=20)
    print(f"\n生成了 {len(data)} 个产品")

    # 显示第一条数据
    if data:
        print("\n示例数据:")
        for key, value in data[0].items():
            print(f"  {key}: {value}")


def example4_from_file():
    """示例4: 从SQL文件导入"""
    print("\n" + "=" * 60)
    print("示例4: 从SQL文件导入")
    print("=" * 60)

    # 创建示例SQL文件
    sql_content = """
    -- 用户表
    CREATE TABLE app_users (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        role ENUM('admin', 'user', 'guest') DEFAULT 'user',
        last_login DATETIME,
        is_active BOOLEAN DEFAULT TRUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- 用户配置表
    CREATE TABLE user_settings (
        setting_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        setting_key VARCHAR(50) NOT NULL,
        setting_value TEXT,
        FOREIGN KEY (user_id) REFERENCES app_users(user_id),
        UNIQUE KEY unique_user_setting (user_id, setting_key)
    );
    """

    # 保存到临时文件
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql_content)
        temp_file = f.name

    try:
        # 从文件解析
        parser = DDLParser()
        tables = parser.parse_ddl_file(temp_file)

        print(f"\n从文件解析了 {len(tables)} 个表:")

        for table in tables:
            print(f"\n✓ {table.name}")
            print(f"  - 字段数: {len(table.fields)}")
            print(f"  - 主键: {table.primary_key}")

            if table.foreign_keys:
                print(f"  - 外键:")
                for fk in table.foreign_keys:
                    print(f"      {fk['field_name']} -> {fk['reference_table']}.{fk['reference_field']}")

        # 生成数据
        app = DataMakerApp(seed=42)
        for table in tables:
            app.add_table(table)

        # 生成用户数据
        users, _ = app.generate_data('app_users', count=5)
        print(f"\n生成了 {len(users)} 个用户")

        # 生成用户配置数据
        user_ids = [u['user_id'] for u in users]
        settings, _ = app.generate_with_relations(
            'user_settings',
            count=15,
            related_data={'app_users': user_ids}
        )
        print(f"生成了 {len(settings)} 个用户配置项")

    finally:
        # 清理临时文件
        os.unlink(temp_file)


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("DDL导入功能演示")
    print("=" * 60)

    try:
        example1_basic_ddl()
        example2_multiple_tables()
        example3_complex_types()
        example4_from_file()

        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        print("\n提示: 您可以在Web界面中使用DDL导入功能")
        print("访问 http://localhost:5000 并选择'从DDL导入'标签")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
