# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

try:
    from trytond.modules.account_debt.tests.test_account_debt import suite
except ImportError:
    from .tests import suite

__all__ = ['suite']
