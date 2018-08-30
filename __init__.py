from trytond.pool import Pool

from . import account


def register():
    Pool.register(
        account.AccountDebtStart,
        module='account_debt', type_='model')
    Pool.register(
        account.AccountDebt,
        module='account_debt', type_='wizard')
    Pool.register(
        account.AccountDebtReport,
        module='account_debt', type_='report')
