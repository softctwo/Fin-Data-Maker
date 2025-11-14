-- 示例DDL文件
-- 可用于测试DDL导入功能

-- 电商系统示例表

-- 商品类目表
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT,
    level INT DEFAULT 1,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    COMMENT '商品类目表'
);

-- 商品表
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_code VARCHAR(50) NOT NULL UNIQUE COMMENT '商品编码',
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称',
    category_id INT NOT NULL COMMENT '类目ID',
    description TEXT COMMENT '商品描述',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    cost_price DECIMAL(10,2) COMMENT '成本价',
    stock_quantity INT DEFAULT 0 COMMENT '库存数量',
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft' COMMENT '商品状态',
    brand VARCHAR(100) COMMENT '品牌',
    weight DECIMAL(8,2) COMMENT '重量(kg)',
    is_featured BOOLEAN DEFAULT FALSE COMMENT '是否精选',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    sale_count INT DEFAULT 0 COMMENT '销售数量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    COMMENT '商品表'
);

-- 客户表
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_code VARCHAR(50) NOT NULL UNIQUE COMMENT '客户编号',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    full_name VARCHAR(100) COMMENT '姓名',
    gender ENUM('male', 'female', 'other') COMMENT '性别',
    birthday DATE COMMENT '生日',
    id_card VARCHAR(18) COMMENT '身份证号',
    address TEXT COMMENT '地址',
    city VARCHAR(50) COMMENT '城市',
    province VARCHAR(50) COMMENT '省份',
    zipcode VARCHAR(10) COMMENT '邮编',
    customer_level ENUM('bronze', 'silver', 'gold', 'platinum', 'diamond') DEFAULT 'bronze' COMMENT '客户等级',
    total_amount DECIMAL(12,2) DEFAULT 0.00 COMMENT '累计消费金额',
    order_count INT DEFAULT 0 COMMENT '订单数量',
    is_vip BOOLEAN DEFAULT FALSE COMMENT '是否VIP',
    status ENUM('active', 'inactive', 'blocked') DEFAULT 'active' COMMENT '状态',
    last_login DATETIME COMMENT '最后登录时间',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    COMMENT '客户表'
);

-- 订单表
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(50) NOT NULL UNIQUE COMMENT '订单号',
    customer_id INT NOT NULL COMMENT '客户ID',
    order_amount DECIMAL(12,2) NOT NULL COMMENT '订单金额',
    discount_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '优惠金额',
    shipping_fee DECIMAL(8,2) DEFAULT 0.00 COMMENT '运费',
    total_amount DECIMAL(12,2) NOT NULL COMMENT '总金额',
    payment_method ENUM('alipay', 'wechat', 'card', 'cash') COMMENT '支付方式',
    payment_status ENUM('unpaid', 'paid', 'refunded') DEFAULT 'unpaid' COMMENT '支付状态',
    order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '订单状态',
    shipping_name VARCHAR(100) COMMENT '收货人',
    shipping_phone VARCHAR(20) COMMENT '收货电话',
    shipping_address TEXT COMMENT '收货地址',
    remark TEXT COMMENT '订单备注',
    order_date DATETIME NOT NULL COMMENT '下单时间',
    payment_date DATETIME COMMENT '支付时间',
    ship_date DATETIME COMMENT '发货时间',
    delivery_date DATETIME COMMENT '收货时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    COMMENT '订单表'
);

-- 订单明细表
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '商品ID',
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称',
    product_code VARCHAR(50) NOT NULL COMMENT '商品编码',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
    quantity INT NOT NULL COMMENT '数量',
    discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '折扣率(%)',
    subtotal DECIMAL(12,2) NOT NULL COMMENT '小计',
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    COMMENT '订单明细表'
);

-- 库存记录表
CREATE TABLE inventory_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL COMMENT '商品ID',
    change_type ENUM('in', 'out', 'adjust') NOT NULL COMMENT '变动类型',
    change_quantity INT NOT NULL COMMENT '变动数量',
    before_quantity INT NOT NULL COMMENT '变动前库存',
    after_quantity INT NOT NULL COMMENT '变动后库存',
    reference_no VARCHAR(100) COMMENT '关联单号',
    operator VARCHAR(50) COMMENT '操作人',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    COMMENT '库存记录表'
);

-- 客户地址表
CREATE TABLE customer_addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    receiver_name VARCHAR(100) NOT NULL COMMENT '收货人',
    receiver_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    province VARCHAR(50) NOT NULL COMMENT '省份',
    city VARCHAR(50) NOT NULL COMMENT '城市',
    district VARCHAR(50) COMMENT '区县',
    detail_address VARCHAR(200) NOT NULL COMMENT '详细地址',
    zipcode VARCHAR(10) COMMENT '邮编',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认地址',
    label VARCHAR(50) COMMENT '地址标签',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    COMMENT '客户地址表'
);
