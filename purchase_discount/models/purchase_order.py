# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        hicimos backport of v10 improvements on purchase_discount
        Pero por alguna razon, cuando entrabamos en el metodo nativo de odoo,
        luego de llamar a "order.company_id.tax_calculation_rounding_method"
        el price_unit que devolvia era sin aplicar el descuento, cuestion que
        terminamos sobreescribiendo el metodo
        TODO analizar si en v10 es necesario o funciona bien
        """
        # Method copy-pasted from odoo/addons/purchase © Odoo S.A.
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if (
                    order.company_id.tax_calculation_rounding_method ==
                    'round_globally'
                ):
                    # purchase_discount modif below: price_unit uses discount
                    price_unit = line._get_discounted_price_unit()
                    taxes = line.taxes_id.compute_all(
                        price_unit, line.order_id.currency_id,
                        line.product_qty, product=line.product_id,
                        partner=line.order_id.partner_id)
                    amount_tax += sum(
                        t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount')
    def _compute_amount(self):
        for line in self:
            price_unit = line._get_discounted_price_unit()
            context_changed = False
            if price_unit != line.price_unit:
                prec = line.order_id.currency_id.decimal_places
                company = line.order_id.company_id
                if company.tax_calculation_rounding_method == 'round_globally':
                    prec += 5
                base = round(price_unit * line.product_qty, prec)
                obj = line.with_context(base_values=(base, base, base))
                context_changed = True
            else:
                obj = line

            super(PurchaseOrderLine, obj)._compute_amount()
            if context_changed:
                # We need to update results back, as each recordset has a
                # different environment and thus the values are not considered
                line.update({
                    'price_tax': obj.price_tax,
                    'price_total': obj.price_total,
                    'price_subtotal': obj.price_subtotal,
                })

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).
        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    @api.multi
    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability. We have to also switch temporarily the order
        state for avoiding an infinite recursion.
        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Parche de ADHOC. Por temas de performance sacamos el = 'purchase'
            # de abajo y entonces tmb sacamos esto ya que no es necesario.
            # ademas probamos poner if self.order_id.state != 'purchase' abajo
            # pero no ayudo mucho
            # Only change value if it's different
            # self.order_id.state = 'draft'
            price_unit = self.price_unit
            self.price_unit = price
        price = super(PurchaseOrderLine, self)._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
            # self.order_id.state = 'purchase'
        return price
