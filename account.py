# This file is part of account_debt module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal

from trytond.model import fields, ModelView
from trytond.wizard import Wizard, StateView, Button, StateReport
from trytond.report import Report
from trytond.pool import Pool
from trytond.transaction import Transaction


class AccountDebtStart(ModelView):
    'Account Debt'
    __name__ = 'account.debt.start'

    company = fields.Many2One('company.company', 'Company', required=True)
    parties = fields.Many2Many('party.party', None, None, 'Entidades',
        help="Si se deja vacio, consulta por todas las entidades.")

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class AccountDebt(Wizard):
    'Account Debt'
    __name__ = 'account.debt'

    start = StateView('account.debt.start',
        'account_debt.account_debt_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'print_', 'tryton-print', True),
            ])
    print_ = StateReport('account.debt.report')

    def do_print_(self, action):
        data = {
            'company': self.start.company.id,
            }
        if self.start.parties:
            data.update({
                'parties': [p.id for p in self.start.parties],
                })
        return action, data


class AccountDebtReport(Report):
    'Account Debt Report'
    __name__ = 'account.debt.report'

    @classmethod
    def get_context(cls, records, header, data):
        report_context = super().get_context(records, header, data)
        records = []
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Party = pool.get('party.party')
        _ZERO = Decimal('0')

        domain = [('receivable', '>', _ZERO)]
        if 'parties' in data:
            domain.append(('id', 'in', data['parties']))
        parties = Party.search(domain, order=[('name', 'ASC')])

        repartos = []
        for party in parties:
            invoices = Invoice.search([
                ('state', '=', 'posted'),
                ('type', '=', 'out'),
                ('company', '=', data['company']),
                ('party', '=', party.id),
            ], order=[('number', 'ASC')])
            reparto = {}
            reparto['party'] = party
            invoices_amount_to_pay = _ZERO
            for invoice in invoices:
                invoices_amount_to_pay += invoice.amount_to_pay
            reparto['party_credit'] = party.receivable - invoices_amount_to_pay
            reparto['party_receivable'] = party.receivable
            reparto['invoices'] = invoices
            repartos.append(reparto)

        report_context['repartos'] = repartos
        return report_context
