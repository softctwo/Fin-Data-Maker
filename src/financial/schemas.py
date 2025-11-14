"""
金融业务数据模型定义
定义客户、账户、交易等常见金融实体的数据结构
"""

from ..metadata.table import Table
from ..metadata.field import Field, FieldType


def create_customer_table() -> Table:
    """
    创建客户表定义
    包含客户基本信息
    """
    table = Table(
        name="customer",
        description="客户信息表",
        primary_key="customer_id",
    )

    fields = [
        Field(
            name="customer_id",
            field_type=FieldType.ID,
            description="客户唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="customer_name",
            field_type=FieldType.STRING,
            description="客户姓名",
            required=True,
            min_length=2,
            max_length=50,
        ),
        Field(
            name="id_card_no",
            field_type=FieldType.ID_CARD,
            description="身份证号",
            required=True,
            unique=True,
        ),
        Field(
            name="gender",
            field_type=FieldType.ENUM,
            description="性别",
            required=True,
            enum_values=["男", "女"],
        ),
        Field(
            name="birth_date",
            field_type=FieldType.DATE,
            description="出生日期",
            required=True,
        ),
        Field(
            name="phone",
            field_type=FieldType.PHONE,
            description="手机号码",
            required=True,
        ),
        Field(
            name="email",
            field_type=FieldType.EMAIL,
            description="电子邮箱",
            required=False,
        ),
        Field(
            name="address",
            field_type=FieldType.STRING,
            description="联系地址",
            required=False,
            max_length=200,
        ),
        Field(
            name="customer_type",
            field_type=FieldType.ENUM,
            description="客户类型",
            required=True,
            enum_values=["个人", "企业"],
        ),
        Field(
            name="customer_level",
            field_type=FieldType.ENUM,
            description="客户等级",
            required=True,
            enum_values=["普通", "银卡", "金卡", "白金卡", "钻石卡"],
        ),
        Field(
            name="registration_date",
            field_type=FieldType.DATE,
            description="注册日期",
            required=True,
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="客户状态",
            required=True,
            enum_values=["正常", "冻结", "注销"],
            default_value="正常",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_account_table() -> Table:
    """
    创建账户表定义
    包含银行账户信息
    """
    table = Table(
        name="account",
        description="账户信息表",
        primary_key="account_id",
    )

    fields = [
        Field(
            name="account_id",
            field_type=FieldType.ID,
            description="账户唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="customer_id",
            field_type=FieldType.ID,
            description="客户ID",
            required=True,
            length=20,
            reference_table="customer",
            reference_field="customer_id",
        ),
        Field(
            name="account_no",
            field_type=FieldType.BANK_CARD,
            description="账号",
            required=True,
            unique=True,
        ),
        Field(
            name="account_type",
            field_type=FieldType.ENUM,
            description="账户类型",
            required=True,
            enum_values=["储蓄账户", "支票账户", "定期账户", "信用账户"],
        ),
        Field(
            name="currency",
            field_type=FieldType.ENUM,
            description="币种",
            required=True,
            enum_values=["CNY", "USD", "EUR", "GBP", "JPY", "HKD"],
            default_value="CNY",
        ),
        Field(
            name="balance",
            field_type=FieldType.AMOUNT,
            description="账户余额",
            required=True,
            min_value=0,
            max_value=10000000,
            precision=2,
        ),
        Field(
            name="available_balance",
            field_type=FieldType.AMOUNT,
            description="可用余额",
            required=True,
            min_value=0,
            max_value=10000000,
            precision=2,
        ),
        Field(
            name="open_date",
            field_type=FieldType.DATE,
            description="开户日期",
            required=True,
        ),
        Field(
            name="branch_code",
            field_type=FieldType.STRING,
            description="开户网点代码",
            required=True,
            length=10,
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="账户状态",
            required=True,
            enum_values=["正常", "冻结", "销户"],
            default_value="正常",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_transaction_table() -> Table:
    """
    创建交易表定义
    包含交易流水信息
    """
    table = Table(
        name="transaction",
        description="交易流水表",
        primary_key="transaction_id",
    )

    fields = [
        Field(
            name="transaction_id",
            field_type=FieldType.ID,
            description="交易唯一标识",
            required=True,
            unique=True,
            length=32,
        ),
        Field(
            name="account_id",
            field_type=FieldType.ID,
            description="账户ID",
            required=True,
            length=20,
            reference_table="account",
            reference_field="account_id",
        ),
        Field(
            name="transaction_type",
            field_type=FieldType.ENUM,
            description="交易类型",
            required=True,
            enum_values=["存款", "取款", "转账", "消费", "还款", "利息"],
        ),
        Field(
            name="amount",
            field_type=FieldType.AMOUNT,
            description="交易金额",
            required=True,
            min_value=0.01,
            max_value=1000000,
            precision=2,
        ),
        Field(
            name="balance_after",
            field_type=FieldType.AMOUNT,
            description="交易后余额",
            required=True,
            min_value=0,
            precision=2,
        ),
        Field(
            name="transaction_time",
            field_type=FieldType.DATETIME,
            description="交易时间",
            required=True,
        ),
        Field(
            name="channel",
            field_type=FieldType.ENUM,
            description="交易渠道",
            required=True,
            enum_values=["柜台", "ATM", "网银", "手机银行", "第三方支付"],
        ),
        Field(
            name="counterparty_account",
            field_type=FieldType.STRING,
            description="对方账户",
            required=False,
            max_length=30,
        ),
        Field(
            name="counterparty_name",
            field_type=FieldType.STRING,
            description="对方户名",
            required=False,
            max_length=100,
        ),
        Field(
            name="remark",
            field_type=FieldType.STRING,
            description="备注",
            required=False,
            max_length=200,
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="交易状态",
            required=True,
            enum_values=["成功", "失败", "处理中", "已撤销"],
            default_value="成功",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_loan_table() -> Table:
    """
    创建贷款表定义
    包含贷款信息
    """
    table = Table(
        name="loan",
        description="贷款信息表",
        primary_key="loan_id",
    )

    fields = [
        Field(
            name="loan_id",
            field_type=FieldType.ID,
            description="贷款唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="customer_id",
            field_type=FieldType.ID,
            description="客户ID",
            required=True,
            length=20,
            reference_table="customer",
            reference_field="customer_id",
        ),
        Field(
            name="loan_type",
            field_type=FieldType.ENUM,
            description="贷款类型",
            required=True,
            enum_values=["个人消费贷款", "住房贷款", "汽车贷款", "经营性贷款", "信用贷款"],
        ),
        Field(
            name="loan_amount",
            field_type=FieldType.AMOUNT,
            description="贷款金额",
            required=True,
            min_value=10000,
            max_value=10000000,
            precision=2,
        ),
        Field(
            name="outstanding_balance",
            field_type=FieldType.AMOUNT,
            description="未还余额",
            required=True,
            min_value=0,
            precision=2,
        ),
        Field(
            name="interest_rate",
            field_type=FieldType.DECIMAL,
            description="年利率（%）",
            required=True,
            min_value=0.1,
            max_value=24.0,
            precision=2,
        ),
        Field(
            name="loan_term",
            field_type=FieldType.INTEGER,
            description="贷款期限（月）",
            required=True,
            min_value=1,
            max_value=360,
        ),
        Field(
            name="disbursement_date",
            field_type=FieldType.DATE,
            description="放款日期",
            required=True,
        ),
        Field(
            name="maturity_date",
            field_type=FieldType.DATE,
            description="到期日期",
            required=True,
        ),
        Field(
            name="repayment_method",
            field_type=FieldType.ENUM,
            description="还款方式",
            required=True,
            enum_values=["等额本息", "等额本金", "先息后本", "一次性还本付息"],
        ),
        Field(
            name="overdue_days",
            field_type=FieldType.INTEGER,
            description="逾期天数",
            required=True,
            min_value=0,
            max_value=1000,
            default_value=0,
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="贷款状态",
            required=True,
            enum_values=["正常", "逾期", "核销", "结清"],
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_credit_card_table() -> Table:
    """
    创建信用卡表定义
    包含信用卡信息
    """
    table = Table(
        name="credit_card",
        description="信用卡信息表",
        primary_key="card_id",
    )

    fields = [
        Field(
            name="card_id",
            field_type=FieldType.ID,
            description="信用卡唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="customer_id",
            field_type=FieldType.ID,
            description="客户ID",
            required=True,
            length=20,
            reference_table="customer",
            reference_field="customer_id",
        ),
        Field(
            name="card_no",
            field_type=FieldType.BANK_CARD,
            description="卡号",
            required=True,
            unique=True,
        ),
        Field(
            name="card_type",
            field_type=FieldType.ENUM,
            description="卡片类型",
            required=True,
            enum_values=["普卡", "金卡", "白金卡", "钻石卡"],
        ),
        Field(
            name="credit_limit",
            field_type=FieldType.AMOUNT,
            description="信用额度",
            required=True,
            min_value=1000,
            max_value=1000000,
            precision=2,
        ),
        Field(
            name="available_limit",
            field_type=FieldType.AMOUNT,
            description="可用额度",
            required=True,
            min_value=0,
            precision=2,
        ),
        Field(
            name="outstanding_balance",
            field_type=FieldType.AMOUNT,
            description="未还款金额",
            required=True,
            min_value=0,
            precision=2,
        ),
        Field(
            name="issue_date",
            field_type=FieldType.DATE,
            description="发卡日期",
            required=True,
        ),
        Field(
            name="expiry_date",
            field_type=FieldType.DATE,
            description="有效期",
            required=True,
        ),
        Field(
            name="billing_day",
            field_type=FieldType.INTEGER,
            description="账单日",
            required=True,
            min_value=1,
            max_value=28,
        ),
        Field(
            name="payment_due_day",
            field_type=FieldType.INTEGER,
            description="还款日",
            required=True,
            min_value=1,
            max_value=28,
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="卡片状态",
            required=True,
            enum_values=["正常", "冻结", "挂失", "注销"],
            default_value="正常",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_bond_table() -> Table:
    """
    创建债券表定义
    包含债券信息
    """
    table = Table(
        name="bond",
        description="债券信息表",
        primary_key="bond_id",
    )

    fields = [
        Field(
            name="bond_id",
            field_type=FieldType.ID,
            description="债券唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="issuer_id",
            field_type=FieldType.ID,
            description="发行人ID（客户ID）",
            required=True,
            length=20,
            reference_table="customer",
            reference_field="customer_id",
        ),
        Field(
            name="bond_code",
            field_type=FieldType.STRING,
            description="债券代码",
            required=True,
            unique=True,
            length=10,
        ),
        Field(
            name="bond_name",
            field_type=FieldType.STRING,
            description="债券名称",
            required=True,
            min_length=2,
            max_length=100,
        ),
        Field(
            name="bond_type",
            field_type=FieldType.ENUM,
            description="债券类型",
            required=True,
            enum_values=["国债", "地方政府债", "政策性金融债", "企业债", "公司债", "可转债", "短期融资券", "中期票据"],
        ),
        Field(
            name="face_value",
            field_type=FieldType.AMOUNT,
            description="票面金额",
            required=True,
            min_value=100,
            max_value=10000,
            precision=2,
            default_value=100,
        ),
        Field(
            name="coupon_rate",
            field_type=FieldType.DECIMAL,
            description="票面利率（%）",
            required=True,
            min_value=0.5,
            max_value=15.0,
            precision=2,
        ),
        Field(
            name="issue_price",
            field_type=FieldType.AMOUNT,
            description="发行价格",
            required=True,
            min_value=50,
            max_value=10000,
            precision=2,
        ),
        Field(
            name="issue_amount",
            field_type=FieldType.AMOUNT,
            description="发行总额（万元）",
            required=True,
            min_value=1000,
            max_value=10000000,
            precision=2,
        ),
        Field(
            name="issue_date",
            field_type=FieldType.DATE,
            description="发行日期",
            required=True,
        ),
        Field(
            name="maturity_date",
            field_type=FieldType.DATE,
            description="到期日期",
            required=True,
        ),
        Field(
            name="payment_frequency",
            field_type=FieldType.ENUM,
            description="付息频率",
            required=True,
            enum_values=["年付", "半年付", "季付", "月付", "到期一次还本付息"],
        ),
        Field(
            name="credit_rating",
            field_type=FieldType.ENUM,
            description="信用评级",
            required=True,
            enum_values=["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"],
        ),
        Field(
            name="listing_date",
            field_type=FieldType.DATE,
            description="上市日期",
            required=False,
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="债券状态",
            required=True,
            enum_values=["发行中", "正常交易", "停牌", "已到期", "已违约"],
            default_value="正常交易",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_fund_table() -> Table:
    """
    创建基金表定义
    包含基金产品信息
    """
    table = Table(
        name="fund",
        description="基金信息表",
        primary_key="fund_id",
    )

    fields = [
        Field(
            name="fund_id",
            field_type=FieldType.ID,
            description="基金唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="fund_code",
            field_type=FieldType.STRING,
            description="基金代码",
            required=True,
            unique=True,
            length=10,
        ),
        Field(
            name="fund_name",
            field_type=FieldType.STRING,
            description="基金名称",
            required=True,
            min_length=2,
            max_length=100,
        ),
        Field(
            name="fund_type",
            field_type=FieldType.ENUM,
            description="基金类型",
            required=True,
            enum_values=["股票型", "债券型", "混合型", "货币型", "指数型", "QDII", "ETF", "LOF", "FOF"],
        ),
        Field(
            name="fund_manager",
            field_type=FieldType.STRING,
            description="基金管理人",
            required=True,
            min_length=2,
            max_length=100,
        ),
        Field(
            name="fund_manager_id",
            field_type=FieldType.ID,
            description="基金经理ID（客户ID）",
            required=True,
            length=20,
            reference_table="customer",
            reference_field="customer_id",
        ),
        Field(
            name="custodian",
            field_type=FieldType.STRING,
            description="托管银行",
            required=True,
            min_length=2,
            max_length=100,
        ),
        Field(
            name="net_value",
            field_type=FieldType.DECIMAL,
            description="单位净值",
            required=True,
            min_value=0.1,
            max_value=100.0,
            precision=4,
        ),
        Field(
            name="accumulated_net_value",
            field_type=FieldType.DECIMAL,
            description="累计净值",
            required=True,
            min_value=0.1,
            max_value=1000.0,
            precision=4,
        ),
        Field(
            name="fund_size",
            field_type=FieldType.AMOUNT,
            description="基金规模（亿元）",
            required=True,
            min_value=0.01,
            max_value=10000,
            precision=2,
        ),
        Field(
            name="establishment_date",
            field_type=FieldType.DATE,
            description="成立日期",
            required=True,
        ),
        Field(
            name="management_fee_rate",
            field_type=FieldType.DECIMAL,
            description="管理费率（%）",
            required=True,
            min_value=0.0,
            max_value=3.0,
            precision=2,
        ),
        Field(
            name="custodian_fee_rate",
            field_type=FieldType.DECIMAL,
            description="托管费率（%）",
            required=True,
            min_value=0.0,
            max_value=1.0,
            precision=2,
        ),
        Field(
            name="subscription_rate",
            field_type=FieldType.DECIMAL,
            description="认购费率（%）",
            required=True,
            min_value=0.0,
            max_value=5.0,
            precision=2,
        ),
        Field(
            name="redemption_rate",
            field_type=FieldType.DECIMAL,
            description="赎回费率（%）",
            required=True,
            min_value=0.0,
            max_value=5.0,
            precision=2,
        ),
        Field(
            name="risk_level",
            field_type=FieldType.ENUM,
            description="风险等级",
            required=True,
            enum_values=["低风险", "中低风险", "中等风险", "中高风险", "高风险"],
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="基金状态",
            required=True,
            enum_values=["募集中", "运作中", "暂停申购", "暂停赎回", "暂停交易", "已清盘"],
            default_value="运作中",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table


def create_derivative_table() -> Table:
    """
    创建衍生品表定义
    包含金融衍生品信息
    """
    table = Table(
        name="derivative",
        description="金融衍生品信息表",
        primary_key="derivative_id",
    )

    fields = [
        Field(
            name="derivative_id",
            field_type=FieldType.ID,
            description="衍生品唯一标识",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="contract_code",
            field_type=FieldType.STRING,
            description="合约代码",
            required=True,
            unique=True,
            length=20,
        ),
        Field(
            name="contract_name",
            field_type=FieldType.STRING,
            description="合约名称",
            required=True,
            min_length=2,
            max_length=100,
        ),
        Field(
            name="derivative_type",
            field_type=FieldType.ENUM,
            description="衍生品类型",
            required=True,
            enum_values=["期货", "期权", "互换", "远期", "结构化产品", "权证"],
        ),
        Field(
            name="underlying_asset_type",
            field_type=FieldType.ENUM,
            description="标的资产类型",
            required=True,
            enum_values=["股票", "股指", "债券", "商品", "货币", "利率", "信用"],
        ),
        Field(
            name="underlying_asset_code",
            field_type=FieldType.STRING,
            description="标的资产代码",
            required=True,
            max_length=20,
        ),
        Field(
            name="underlying_asset_name",
            field_type=FieldType.STRING,
            description="标的资产名称",
            required=True,
            min_length=2,
            max_length=100,
        ),
        Field(
            name="contract_size",
            field_type=FieldType.DECIMAL,
            description="合约乘数/规模",
            required=True,
            min_value=1,
            max_value=1000000,
            precision=2,
        ),
        Field(
            name="strike_price",
            field_type=FieldType.DECIMAL,
            description="行权价格/执行价格",
            required=False,
            min_value=0.01,
            max_value=1000000,
            precision=2,
        ),
        Field(
            name="option_type",
            field_type=FieldType.ENUM,
            description="期权类型",
            required=False,
            enum_values=["看涨", "看跌", "不适用"],
        ),
        Field(
            name="contract_unit",
            field_type=FieldType.STRING,
            description="合约单位",
            required=True,
            max_length=20,
        ),
        Field(
            name="listing_date",
            field_type=FieldType.DATE,
            description="上市日期",
            required=True,
        ),
        Field(
            name="expiry_date",
            field_type=FieldType.DATE,
            description="到期日期",
            required=True,
        ),
        Field(
            name="delivery_month",
            field_type=FieldType.STRING,
            description="交割月份",
            required=False,
            length=6,
        ),
        Field(
            name="settlement_method",
            field_type=FieldType.ENUM,
            description="结算方式",
            required=True,
            enum_values=["实物交割", "现金交割", "混合交割"],
        ),
        Field(
            name="margin_rate",
            field_type=FieldType.DECIMAL,
            description="保证金比例（%）",
            required=True,
            min_value=5.0,
            max_value=100.0,
            precision=2,
        ),
        Field(
            name="exchange",
            field_type=FieldType.ENUM,
            description="交易所",
            required=True,
            enum_values=["上海期货交易所", "大连商品交易所", "郑州商品交易所", "中国金融期货交易所", "上海证券交易所", "深圳证券交易所"],
        ),
        Field(
            name="status",
            field_type=FieldType.ENUM,
            description="合约状态",
            required=True,
            enum_values=["交易中", "停牌", "已到期", "已交割"],
            default_value="交易中",
        ),
    ]

    for field in fields:
        table.add_field(field)

    return table
