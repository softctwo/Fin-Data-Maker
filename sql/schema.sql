-- ============================================================
-- 金融数据生成系统 - 数据库表结构定义
-- Fin-Data-Maker SQL Schema
-- ============================================================

-- 清理已存在的表（按依赖顺序）
DROP TABLE IF EXISTS derivative;
DROP TABLE IF EXISTS fund;
DROP TABLE IF EXISTS bond;
DROP TABLE IF EXISTS credit_card;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS transaction;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS customer;

-- ============================================================
-- 1. 客户信息表 (Customer)
-- ============================================================
CREATE TABLE customer (
    customer_id VARCHAR(20) PRIMARY KEY COMMENT '客户唯一标识',
    customer_name VARCHAR(50) NOT NULL COMMENT '客户姓名',
    id_card_no VARCHAR(18) NOT NULL UNIQUE COMMENT '身份证号',
    gender ENUM('男', '女') NOT NULL COMMENT '性别',
    birth_date DATE NOT NULL COMMENT '出生日期',
    phone VARCHAR(20) NOT NULL COMMENT '手机号码',
    email VARCHAR(100) COMMENT '电子邮箱',
    address VARCHAR(200) COMMENT '联系地址',
    customer_type ENUM('个人', '企业') NOT NULL COMMENT '客户类型',
    customer_level ENUM('普通', '银卡', '金卡', '白金卡', '钻石卡') NOT NULL COMMENT '客户等级',
    registration_date DATE NOT NULL COMMENT '注册日期',
    status ENUM('正常', '冻结', '注销') NOT NULL DEFAULT '正常' COMMENT '客户状态',
    INDEX idx_customer_type (customer_type),
    INDEX idx_customer_level (customer_level),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户信息表';

-- ============================================================
-- 2. 账户信息表 (Account)
-- ============================================================
CREATE TABLE account (
    account_id VARCHAR(20) PRIMARY KEY COMMENT '账户唯一标识',
    customer_id VARCHAR(20) NOT NULL COMMENT '客户ID',
    account_no VARCHAR(19) NOT NULL UNIQUE COMMENT '账号',
    account_type ENUM('储蓄账户', '支票账户', '定期账户', '信用账户') NOT NULL COMMENT '账户类型',
    currency ENUM('CNY', 'USD', 'EUR', 'GBP', 'JPY', 'HKD') NOT NULL DEFAULT 'CNY' COMMENT '币种',
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00 COMMENT '账户余额',
    available_balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00 COMMENT '可用余额',
    open_date DATE NOT NULL COMMENT '开户日期',
    branch_code VARCHAR(10) NOT NULL COMMENT '开户网点代码',
    status ENUM('正常', '冻结', '销户') NOT NULL DEFAULT '正常' COMMENT '账户状态',
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_account_type (account_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账户信息表';

-- ============================================================
-- 3. 交易流水表 (Transaction)
-- ============================================================
CREATE TABLE transaction (
    transaction_id VARCHAR(32) PRIMARY KEY COMMENT '交易唯一标识',
    account_id VARCHAR(20) NOT NULL COMMENT '账户ID',
    transaction_type ENUM('存款', '取款', '转账', '消费', '还款', '利息') NOT NULL COMMENT '交易类型',
    amount DECIMAL(15, 2) NOT NULL COMMENT '交易金额',
    balance_after DECIMAL(15, 2) NOT NULL COMMENT '交易后余额',
    transaction_time DATETIME NOT NULL COMMENT '交易时间',
    channel ENUM('柜台', 'ATM', '网银', '手机银行', '第三方支付') NOT NULL COMMENT '交易渠道',
    counterparty_account VARCHAR(30) COMMENT '对方账户',
    counterparty_name VARCHAR(100) COMMENT '对方户名',
    remark VARCHAR(200) COMMENT '备注',
    status ENUM('成功', '失败', '处理中', '已撤销') NOT NULL DEFAULT '成功' COMMENT '交易状态',
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    INDEX idx_account_id (account_id),
    INDEX idx_transaction_time (transaction_time),
    INDEX idx_transaction_type (transaction_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易流水表';

-- ============================================================
-- 4. 贷款信息表 (Loan)
-- ============================================================
CREATE TABLE loan (
    loan_id VARCHAR(20) PRIMARY KEY COMMENT '贷款唯一标识',
    customer_id VARCHAR(20) NOT NULL COMMENT '客户ID',
    loan_type ENUM('个人消费贷款', '住房贷款', '汽车贷款', '经营性贷款', '信用贷款') NOT NULL COMMENT '贷款类型',
    loan_amount DECIMAL(15, 2) NOT NULL COMMENT '贷款金额',
    outstanding_balance DECIMAL(15, 2) NOT NULL COMMENT '未还余额',
    interest_rate DECIMAL(5, 2) NOT NULL COMMENT '年利率（%）',
    loan_term INT NOT NULL COMMENT '贷款期限（月）',
    disbursement_date DATE NOT NULL COMMENT '放款日期',
    maturity_date DATE NOT NULL COMMENT '到期日期',
    repayment_method ENUM('等额本息', '等额本金', '先息后本', '一次性还本付息') NOT NULL COMMENT '还款方式',
    overdue_days INT NOT NULL DEFAULT 0 COMMENT '逾期天数',
    status ENUM('正常', '逾期', '核销', '结清') NOT NULL COMMENT '贷款状态',
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_loan_type (loan_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='贷款信息表';

-- ============================================================
-- 5. 信用卡信息表 (Credit Card)
-- ============================================================
CREATE TABLE credit_card (
    card_id VARCHAR(20) PRIMARY KEY COMMENT '信用卡唯一标识',
    customer_id VARCHAR(20) NOT NULL COMMENT '客户ID',
    card_no VARCHAR(19) NOT NULL UNIQUE COMMENT '卡号',
    card_type ENUM('普卡', '金卡', '白金卡', '钻石卡') NOT NULL COMMENT '卡片类型',
    credit_limit DECIMAL(15, 2) NOT NULL COMMENT '信用额度',
    available_limit DECIMAL(15, 2) NOT NULL COMMENT '可用额度',
    outstanding_balance DECIMAL(15, 2) NOT NULL COMMENT '未还款金额',
    issue_date DATE NOT NULL COMMENT '发卡日期',
    expiry_date DATE NOT NULL COMMENT '有效期',
    billing_day INT NOT NULL COMMENT '账单日',
    payment_due_day INT NOT NULL COMMENT '还款日',
    status ENUM('正常', '冻结', '挂失', '注销') NOT NULL DEFAULT '正常' COMMENT '卡片状态',
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_card_type (card_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='信用卡信息表';

-- ============================================================
-- 6. 债券信息表 (Bond)
-- ============================================================
CREATE TABLE bond (
    bond_id VARCHAR(20) PRIMARY KEY COMMENT '债券唯一标识',
    issuer_id VARCHAR(20) NOT NULL COMMENT '发行人ID（客户ID）',
    bond_code VARCHAR(10) NOT NULL UNIQUE COMMENT '债券代码',
    bond_name VARCHAR(100) NOT NULL COMMENT '债券名称',
    bond_type ENUM('国债', '地方政府债', '政策性金融债', '企业债', '公司债', '可转债', '短期融资券', '中期票据') NOT NULL COMMENT '债券类型',
    face_value DECIMAL(15, 2) NOT NULL DEFAULT 100.00 COMMENT '票面金额',
    coupon_rate DECIMAL(5, 2) NOT NULL COMMENT '票面利率（%）',
    issue_price DECIMAL(15, 2) NOT NULL COMMENT '发行价格',
    issue_amount DECIMAL(15, 2) NOT NULL COMMENT '发行总额（万元）',
    issue_date DATE NOT NULL COMMENT '发行日期',
    maturity_date DATE NOT NULL COMMENT '到期日期',
    payment_frequency ENUM('年付', '半年付', '季付', '月付', '到期一次还本付息') NOT NULL COMMENT '付息频率',
    credit_rating ENUM('AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-') NOT NULL COMMENT '信用评级',
    listing_date DATE COMMENT '上市日期',
    status ENUM('发行中', '正常交易', '停牌', '已到期', '已违约') NOT NULL DEFAULT '正常交易' COMMENT '债券状态',
    FOREIGN KEY (issuer_id) REFERENCES customer(customer_id),
    INDEX idx_issuer_id (issuer_id),
    INDEX idx_bond_type (bond_type),
    INDEX idx_credit_rating (credit_rating),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='债券信息表';

-- ============================================================
-- 7. 基金信息表 (Fund)
-- ============================================================
CREATE TABLE fund (
    fund_id VARCHAR(20) PRIMARY KEY COMMENT '基金唯一标识',
    fund_code VARCHAR(10) NOT NULL UNIQUE COMMENT '基金代码',
    fund_name VARCHAR(100) NOT NULL COMMENT '基金名称',
    fund_type ENUM('股票型', '债券型', '混合型', '货币型', '指数型', 'QDII', 'ETF', 'LOF', 'FOF') NOT NULL COMMENT '基金类型',
    fund_manager VARCHAR(100) NOT NULL COMMENT '基金管理人',
    fund_manager_id VARCHAR(20) NOT NULL COMMENT '基金经理ID（客户ID）',
    custodian VARCHAR(100) NOT NULL COMMENT '托管银行',
    net_value DECIMAL(10, 4) NOT NULL COMMENT '单位净值',
    accumulated_net_value DECIMAL(10, 4) NOT NULL COMMENT '累计净值',
    fund_size DECIMAL(15, 2) NOT NULL COMMENT '基金规模（亿元）',
    establishment_date DATE NOT NULL COMMENT '成立日期',
    management_fee_rate DECIMAL(5, 2) NOT NULL COMMENT '管理费率（%）',
    custodian_fee_rate DECIMAL(5, 2) NOT NULL COMMENT '托管费率（%）',
    subscription_rate DECIMAL(5, 2) NOT NULL COMMENT '认购费率（%）',
    redemption_rate DECIMAL(5, 2) NOT NULL COMMENT '赎回费率（%）',
    risk_level ENUM('低风险', '中低风险', '中等风险', '中高风险', '高风险') NOT NULL COMMENT '风险等级',
    status ENUM('募集中', '运作中', '暂停申购', '暂停赎回', '暂停交易', '已清盘') NOT NULL DEFAULT '运作中' COMMENT '基金状态',
    FOREIGN KEY (fund_manager_id) REFERENCES customer(customer_id),
    INDEX idx_fund_manager_id (fund_manager_id),
    INDEX idx_fund_type (fund_type),
    INDEX idx_risk_level (risk_level),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金信息表';

-- ============================================================
-- 8. 金融衍生品信息表 (Derivative)
-- ============================================================
CREATE TABLE derivative (
    derivative_id VARCHAR(20) PRIMARY KEY COMMENT '衍生品唯一标识',
    contract_code VARCHAR(20) NOT NULL UNIQUE COMMENT '合约代码',
    contract_name VARCHAR(100) NOT NULL COMMENT '合约名称',
    derivative_type ENUM('期货', '期权', '互换', '远期', '结构化产品', '权证') NOT NULL COMMENT '衍生品类型',
    underlying_asset_type ENUM('股票', '股指', '债券', '商品', '货币', '利率', '信用') NOT NULL COMMENT '标的资产类型',
    underlying_asset_code VARCHAR(20) NOT NULL COMMENT '标的资产代码',
    underlying_asset_name VARCHAR(100) NOT NULL COMMENT '标的资产名称',
    contract_size DECIMAL(15, 2) NOT NULL COMMENT '合约乘数/规模',
    strike_price DECIMAL(15, 2) COMMENT '行权价格/执行价格',
    option_type ENUM('看涨', '看跌', '不适用') COMMENT '期权类型',
    contract_unit VARCHAR(20) NOT NULL COMMENT '合约单位',
    listing_date DATE NOT NULL COMMENT '上市日期',
    expiry_date DATE NOT NULL COMMENT '到期日期',
    delivery_month VARCHAR(6) COMMENT '交割月份',
    settlement_method ENUM('实物交割', '现金交割', '混合交割') NOT NULL COMMENT '结算方式',
    margin_rate DECIMAL(5, 2) NOT NULL COMMENT '保证金比例（%）',
    exchange ENUM('上海期货交易所', '大连商品交易所', '郑州商品交易所', '中国金融期货交易所', '上海证券交易所', '深圳证券交易所') NOT NULL COMMENT '交易所',
    status ENUM('交易中', '停牌', '已到期', '已交割') NOT NULL DEFAULT '交易中' COMMENT '合约状态',
    INDEX idx_derivative_type (derivative_type),
    INDEX idx_underlying_asset_type (underlying_asset_type),
    INDEX idx_exchange (exchange),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='金融衍生品信息表';

-- ============================================================
-- 表结构创建完成
-- ============================================================
