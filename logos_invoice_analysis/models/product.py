from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('barcode')
    def _compute_isbn(self):
        isbn = False
        for rec in self:
            if rec.barcode:
                barcode = rec.barcode.replace(' ', '').replace('-', '')
                if len(barcode) == 13 and barcode[0:3] == '978':
                    isbn = rec.barcode[3:12]
                    check_digit = rec.calculate_control_digit_isbn(isbn)
                    isbn += check_digit
            rec.isbn = isbn

    def calculate_control_digit_isbn(self, str_partial_isbn):
        if not str_partial_isbn:
            return None
        if len(str_partial_isbn) != 9:
            return None
        try:
            int(str_partial_isbn)
        except Exception:
            return None

        val = 0
        for i in range(len(str_partial_isbn)):
            val += int(str_partial_isbn[i]) * (int(i) + 1)
        if val % 11 == 10:
            ret = 'X'
        else:
            ret = str(val % 11)
        return ret

    isbn = fields.Char(
        compute='_compute_isbn',
        string='ISBN',
        store=True)

    @api.model
    def name_search(
            self, name, args=None, operator='ilike', limit=100):
        res = super(ProductTemplate, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        if len(res) < limit:
            products = self.search(
                [('isbn', operator, name)] + (args or []),
                limit=limit)
            res += products.name_get()
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(
            self, name, args=None, operator='ilike', limit=100):
        res = super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        if len(res) < limit:
            products = self.search(
                [('isbn', operator, name)] + (args or []),
                limit=limit)
            res += products.name_get()
        return res
