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
