"""
金融业务数据生成模块
预定义金融行业常用的数据模型
"""

from .schemas import (
    create_customer_table,
    create_account_table,
    create_transaction_table,
    create_loan_table,
    create_credit_card_table,
)

__all__ = [
    'create_customer_table',
    'create_account_table',
    'create_transaction_table',
    'create_loan_table',
    'create_credit_card_table',
]
