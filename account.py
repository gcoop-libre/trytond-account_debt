# This file is part of account_debt module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import fields, ModelView
from trytond.pool import Pool
from trytond.wizard import Wizard, StateView, Button, StateReport
from trytond.transaction import Transaction
from trytond.report import Report

from decimal import Decimal


__all__ = ['AccountDebt', 'AccountDebtStart', 'AccountDebtReport']


class AccountDebtStart(ModelView):
    'Account Debt Start'
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
    def get_context(cls, records, data):
        report_context = super(AccountDebtReport, cls).get_context(records, data)
        records =[]
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
                ('type', 'in', ['out_invoice', 'out_credit_note']),
                ('company', '=', data['company']),
                ('party', '=', party.id),
            ], order=[('number', 'ASC')])
            reparto = {}
            reparto['party'] = party
            invoices_amount_to_pay = _ZERO
            for invoice in invoices:
                if invoice.type in ['out_credit_note']:
                    invoice.amount_to_pay *= -1
                    invoice.total_amount *= -1
                invoices_amount_to_pay += invoice.amount_to_pay
            reparto['party_credit'] = party.receivable - invoices_amount_to_pay
            reparto['party_receivable'] = party.receivable
            reparto['invoices'] = invoices
            repartos.append(reparto)

        report_context = super(AccountDebtReport, cls).get_context(records, data)
        report_context['repartos'] = repartos
        return report_context
