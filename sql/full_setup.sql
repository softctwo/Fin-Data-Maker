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
-- ============================================================
-- 金融数据生成系统 - 测试数据
-- Fin-Data-Maker Test Data
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 客户数据 (Customer)
-- ============================================================
INSERT INTO customer (customer_id, customer_name, id_card_no, gender, birth_date, phone, email, address, customer_type, customer_level, registration_date, status) VALUES
('CUST00000001', '张伟', '110101198001011234', '男', '1980-01-01', '13800138001', 'zhangwei@example.com', '北京市朝阳区建国路88号', '个人', '金卡', '2020-01-15', '正常'),
('CUST00000002', '李娜', '110101198502021235', '女', '1985-02-02', '13800138002', 'lina@example.com', '北京市海淀区中关村大街1号', '个人', '白金卡', '2020-02-20', '正常'),
('CUST00000003', '王强', '110101197503031236', '男', '1975-03-03', '13800138003', 'wangqiang@example.com', '上海市浦东新区陆家嘴环路1000号', '个人', '钻石卡', '2019-05-10', '正常'),
('CUST00000004', '中国石油天然气集团', '91110000100000001X', '男', '1988-09-17', '01088888888', 'cnpc@cnpc.com.cn', '北京市东城区东直门外小街6号', '企业', '钻石卡', '2018-03-01', '正常'),
('CUST00000005', '中国工商银行', '91110000100000002Y', '男', '1984-01-01', '95588', 'service@icbc.com.cn', '北京市西城区复兴门内大街55号', '企业', '钻石卡', '2017-01-01', '正常'),
('CUST00000006', '刘芳', '110101199006061237', '女', '1990-06-06', '13800138006', 'liufang@example.com', '深圳市福田区福华路1号', '个人', '金卡', '2021-03-15', '正常'),
('CUST00000007', '陈明', '110101198807071238', '男', '1988-07-07', '13800138007', 'chenming@example.com', '广州市天河区珠江新城花城大道66号', '个人', '银卡', '2021-06-20', '正常'),
('CUST00000008', '腾讯科技有限公司', '91440300100000003Z', '男', '1998-11-11', '0755-86013388', 'service@tencent.com', '广东省深圳市南山区科技园', '企业', '钻石卡', '2019-01-10', '正常'),
('CUST00000009', '阿里巴巴集团', '91330100100000004A', '男', '1999-09-09', '0571-85022088', 'service@alibaba.com', '浙江省杭州市余杭区文一西路969号', '企业', '钻石卡', '2019-02-15', '正常'),
('CUST00000010', '赵敏', '110101199208081239', '女', '1992-08-08', '13800138010', 'zhaomin@example.com', '成都市锦江区红星路二段70号', '个人', '普通', '2022-01-01', '正常');

-- ============================================================
-- 2. 债券数据 (Bond)
-- ============================================================
INSERT INTO bond (bond_id, issuer_id, bond_code, bond_name, bond_type, face_value, coupon_rate, issue_price, issue_amount, issue_date, maturity_date, payment_frequency, credit_rating, listing_date, status) VALUES
('BOND00000001', 'CUST00000004', '019547', '20国债01', '国债', 100.00, 3.27, 100.00, 50000000.00, '2020-03-01', '2030-03-01', '半年付', 'AAA', '2020-03-15', '正常交易'),
('BOND00000002', 'CUST00000004', '019548', '20国债02', '国债', 100.00, 3.50, 100.00, 80000000.00, '2020-06-01', '2040-06-01', '半年付', 'AAA', '2020-06-15', '正常交易'),
('BOND00000003', 'CUST00000005', '108601', '20工行01', '金融债', 100.00, 3.85, 100.00, 30000000.00, '2020-08-10', '2023-08-10', '年付', 'AAA', '2020-08-20', '正常交易'),
('BOND00000004', 'CUST00000005', '108602', '20工行02', '金融债', 100.00, 4.20, 100.00, 50000000.00, '2021-01-15', '2026-01-15', '年付', 'AAA', '2021-01-25', '正常交易'),
('BOND00000005', 'CUST00000008', '143258', '21腾讯01', '公司债', 100.00, 4.50, 100.00, 10000000.00, '2021-03-20', '2024-03-20', '年付', 'AAA', '2021-04-01', '正常交易'),
('BOND00000006', 'CUST00000008', '143259', '21腾讯02', '公司债', 100.00, 4.75, 100.00, 15000000.00, '2021-09-10', '2026-09-10', '年付', 'AAA', '2021-09-20', '正常交易'),
('BOND00000007', 'CUST00000009', '143360', '22阿里01', '公司债', 100.00, 4.60, 100.00, 20000000.00, '2022-05-15', '2027-05-15', '年付', 'AAA', '2022-05-25', '正常交易'),
('BOND00000008', 'CUST00000004', '012003', '20石油CP001', '短期融资券', 100.00, 2.80, 100.00, 50000000.00, '2020-09-01', '2021-09-01', '到期一次还本付息', 'AA+', '2020-09-10', '已到期'),
('BOND00000009', 'CUST00000004', '102101', '21石油MTN001', '中期票据', 100.00, 4.00, 100.00, 80000000.00, '2021-06-01', '2024-06-01', '年付', 'AAA', '2021-06-15', '正常交易'),
('BOND00000010', 'CUST00000005', '113536', '工行转债', '可转债', 100.00, 1.50, 100.00, 60000000.00, '2020-12-01', '2026-12-01', '年付', 'AAA', '2020-12-15', '正常交易');

-- ============================================================
-- 3. 基金数据 (Fund)
-- ============================================================
INSERT INTO fund (fund_id, fund_code, fund_name, fund_type, fund_manager, fund_manager_id, custodian, net_value, accumulated_net_value, fund_size, establishment_date, management_fee_rate, custodian_fee_rate, subscription_rate, redemption_rate, risk_level, status) VALUES
('FUND00000001', '000001', '华夏成长混合', '混合型', '华夏基金管理有限公司', 'CUST00000003', '中国工商银行', 1.5240, 3.2150, 125.50, '2001-12-18', 1.50, 0.25, 1.20, 0.50, '中高风险', '运作中'),
('FUND00000002', '110022', '易方达消费行业股票', '股票型', '易方达基金管理有限公司', 'CUST00000003', '中国建设银行', 3.8620, 3.8620, 235.80, '2010-08-20', 1.50, 0.25, 1.50, 0.50, '高风险', '运作中'),
('FUND00000003', '163402', '兴全趋势投资混合', '混合型', '兴全基金管理有限公司', 'CUST00000006', '中国工商银行', 1.2580, 5.9460, 89.30, '2005-11-03', 1.50, 0.25, 1.50, 0.50, '中高风险', '运作中'),
('FUND00000004', '040004', '华安宝利配置混合', '混合型', '华安基金管理有限公司', 'CUST00000006', '中国银行', 1.3750, 4.5690, 52.60, '2004-08-24', 1.50, 0.25, 1.20, 0.50, '中等风险', '运作中'),
('FUND00000005', '050002', '博时裕富沪深300指数', '指数型', '博时基金管理有限公司', 'CUST00000007', '中国建设银行', 1.4280, 3.5120, 156.70, '2003-08-26', 1.00, 0.20, 1.20, 0.50, '中高风险', '运作中'),
('FUND00000006', '510050', '华夏上证50ETF', 'ETF', '华夏基金管理有限公司', 'CUST00000003', '中国工商银行', 3.0560, 3.5280, 482.30, '2004-12-30', 0.50, 0.10, 0.00, 0.00, '中高风险', '运作中'),
('FUND00000007', '161725', '招商中证白酒指数分级', 'LOF', '招商基金管理有限公司', 'CUST00000007', '中国银行', 1.0860, 1.8540, 67.90, '2015-05-27', 1.00, 0.20, 1.20, 0.50, '高风险', '运作中'),
('FUND00000008', '270008', '广发核心精选混合', '混合型', '广发基金管理有限公司', 'CUST00000006', '中国工商银行', 4.3670, 4.9850, 92.40, '2008-07-16', 1.50, 0.25, 1.50, 0.50, '中高风险', '运作中'),
('FUND00000009', '000041', '华夏全球精选股票QDII', 'QDII', '华夏基金管理有限公司', 'CUST00000003', '中国建设银行', 1.0280, 1.0280, 28.50, '2007-10-09', 1.80, 0.35, 1.60, 0.50, '高风险', '运作中'),
('FUND00000010', '006098', '易方达货币市场基金A', '货币型', '易方达基金管理有限公司', 'CUST00000003', '中国工商银行', 1.0000, 1.0000, 1250.60, '2012-05-18', 0.33, 0.10, 0.00, 0.00, '低风险', '运作中');

-- ============================================================
-- 4. 衍生品数据 (Derivative)
-- ============================================================
INSERT INTO derivative (derivative_id, contract_code, contract_name, derivative_type, underlying_asset_type, underlying_asset_code, underlying_asset_name, contract_size, strike_price, option_type, contract_unit, listing_date, expiry_date, delivery_month, settlement_method, margin_rate, exchange, status) VALUES
('DERIV0000001', 'IF2312', '沪深300股指期货2312', '期货', '股指', '000300', '沪深300指数', 300.00, NULL, '不适用', '点', '2023-01-01', '2023-12-15', '202312', '现金交割', 12.00, '中国金融期货交易所', '交易中'),
('DERIV0000002', 'IC2312', '中证500股指期货2312', '期货', '股指', '000905', '中证500指数', 200.00, NULL, '不适用', '点', '2023-01-01', '2023-12-15', '202312', '现金交割', 15.00, '中国金融期货交易所', '交易中'),
('DERIV0000003', 'IH2312', '上证50股指期货2312', '期货', '股指', '000016', '上证50指数', 300.00, NULL, '不适用', '点', '2023-01-01', '2023-12-15', '202312', '现金交割', 12.00, '中国金融期货交易所', '交易中'),
('DERIV0000004', 'AU2312', '黄金期货2312', '期货', '商品', 'AU', '黄金', 1000.00, NULL, '不适用', '克', '2023-01-01', '2023-12-15', '202312', '实物交割', 8.00, '上海期货交易所', '交易中'),
('DERIV0000005', 'CU2312', '铜期货2312', '期货', '商品', 'CU', '铜', 5.00, NULL, '不适用', '吨', '2023-01-01', '2023-12-15', '202312', '实物交割', 10.00, '上海期货交易所', '交易中'),
('DERIV0000006', 'A2401', '豆一期货2401', '期货', '商品', 'A', '黄大豆1号', 10.00, NULL, '不适用', '吨', '2023-01-01', '2024-01-15', '202401', '实物交割', 8.00, '大连商品交易所', '交易中'),
('DERIV0000007', 'M2401', '豆粕期货2401', '期货', '商品', 'M', '豆粕', 10.00, NULL, '不适用', '吨', '2023-01-01', '2024-01-15', '202401', '实物交割', 8.00, '大连商品交易所', '交易中'),
('DERIV0000008', 'SR401', '白糖期货2401', '期货', '商品', 'SR', '白糖', 10.00, NULL, '不适用', '吨', '2023-01-01', '2024-01-15', '202401', '实物交割', 7.00, '郑州商品交易所', '交易中'),
('DERIV0000009', '510050C2312M04200', '50ETF购12月4200', '期权', '股票', '510050', '上证50ETF', 10000.00, 4.2000, '看涨', '份', '2023-06-01', '2023-12-27', '202312', '实物交割', 12.00, '上海证券交易所', '交易中'),
('DERIV0000010', '510050P2312M04000', '50ETF沽12月4000', '期权', '股票', '510050', '上证50ETF', 10000.00, 4.0000, '看跌', '份', '2023-06-01', '2023-12-27', '202312', '实物交割', 12.00, '上海证券交易所', '交易中'),
('DERIV0000011', '510300C2312M04500', '300ETF购12月4500', '期权', '股票', '510300', '沪深300ETF', 10000.00, 4.5000, '看涨', '份', '2023-06-01', '2023-12-27', '202312', '实物交割', 12.00, '上海证券交易所', '交易中'),
('DERIV0000012', 'T2312', '10年期国债期货2312', '期货', '债券', 'T', '10年期国债', 10000.00, NULL, '不适用', '手', '2023-01-01', '2023-12-15', '202312', '实物交割', 2.00, '中国金融期货交易所', '交易中'),
('DERIV0000013', 'TF2312', '5年期国债期货2312', '期货', '债券', 'TF', '5年期国债', 10000.00, NULL, '不适用', '手', '2023-01-01', '2023-12-15', '202312', '实物交割', 1.50, '中国金融期货交易所', '交易中'),
('DERIV0000014', 'TS2312', '2年期国债期货2312', '期货', '债券', 'TS', '2年期国债', 20000.00, NULL, '不适用', '手', '2023-01-01', '2023-12-15', '202312', '实物交割', 0.50, '中国金融期货交易所', '交易中'),
('DERIV0000015', 'IRS-SHIBOR-3M', 'SHIBOR 3个月利率互换', '互换', '利率', 'SHIBOR3M', 'SHIBOR 3个月', 100000000.00, NULL, '不适用', '元', '2022-01-01', '2025-01-01', NULL, '现金交割', 5.00, '上海证券交易所', '交易中');

-- ============================================================
-- 5. 账户数据 (Account) - 示例数据
-- ============================================================
INSERT INTO account (account_id, customer_id, account_no, account_type, currency, balance, available_balance, open_date, branch_code, status) VALUES
('ACCT00000001', 'CUST00000001', '6222021001234567890', '储蓄账户', 'CNY', 58750.50, 58750.50, '2020-01-16', 'BJ001', '正常'),
('ACCT00000002', 'CUST00000002', '6222021001234567891', '储蓄账户', 'CNY', 123456.78, 120000.00, '2020-02-21', 'BJ002', '正常'),
('ACCT00000003', 'CUST00000003', '6222021001234567892', '储蓄账户', 'CNY', 2500000.00, 2500000.00, '2019-05-11', 'SH001', '正常');

-- ============================================================
-- 数据插入完成
-- ============================================================

SET FOREIGN_KEY_CHECKS = 1;

-- 验证数据
SELECT '客户数据' AS '表名', COUNT(*) AS '记录数' FROM customer
UNION ALL
SELECT '债券数据', COUNT(*) FROM bond
UNION ALL
SELECT '基金数据', COUNT(*) FROM fund
UNION ALL
SELECT '衍生品数据', COUNT(*) FROM derivative
UNION ALL
SELECT '账户数据', COUNT(*) FROM account;
