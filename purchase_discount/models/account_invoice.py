# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"

#     @api.model
#     def new(self, values=None):
#         """
#         Apply the linked to a purchase.order.line.discount to the
#         account_invoice_line
#         """
#         values = {} if values is None else values
#         account_invoice_line = super(
#             AccountInvoiceLine, self).new(values=values)
#         if account_invoice_line.purchase_line_id:
#             account_invoice_line.discount =\
#                 account_invoice_line.purchase_line_id.discount
#         return account_invoice_line


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        # backport from v10, this fix onchange of quantity on account invoice
        # for invoices linked to purchase orders
        vals = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line)
        vals['discount'] = line.discount
        return vals
