# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import Warning


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def _inverse_attributes(self):
        for rec in self:
            autor = rec.author_id
            editorial = rec.editorial_id
            collection = rec.collection_id
            rec._set_attribute_value(autor, 'Autor')
            rec._set_attribute_value(editorial, 'Editorial')
            rec._set_attribute_value(collection, 'Colección')

    @api.multi
    def _set_attribute_value(self, field_value, attribute_name):
        self.ensure_one()
        attribute = self.env['product.attribute'].search(
            [('name', '=', attribute_name)], limit=1)
        if not attribute:
            raise Warning(_('Attribute %s not found'), (attribute.name))
        attibute_line = self.env['product.attribute.line'].search(
            [('attribute_id', '=', attribute.id),
             ('product_tmpl_id', '=', self.id)], limit=1)
        if not field_value:
            if attibute_line:
                attibute_line.value_ids = [(5, 0, 0)]
        elif attibute_line:
            attibute_line.value_ids = [(6, 0, [field_value.id])]
        else:
            attibute_line.create({
                'product_tmpl_id': self.id,
                'attribute_id': attribute.id,
                'value_ids': [(4, field_value.id)]
            })

    author_id = fields.Many2one(
        'product.attribute.value',
        compute='_compute_attributes',
        inverse='_inverse_attributes',
        store=True,
        domain=[('attribute_id.name', '=', 'Autor')],
        string='Autor')

    editorial_id = fields.Many2one(
        'product.attribute.value',
        compute='_compute_attributes',
        inverse='_inverse_attributes',
        store=True,
        domain=[('attribute_id.name', '=', 'Editorial')],
        string='Editorial')

    collection_id = fields.Many2one(
        'product.attribute.value',
        compute='_compute_attributes',
        inverse='_inverse_attributes',
        store=True,
        domain=[('attribute_id.name', '=', 'Colección')],
        string='Coleccion')

    @api.multi
    @api.depends(
        # 'attribute_line_ids',
        # 'attribute_line_ids.value_ids',
        'attribute_line_ids.value_ids.name',
        # 'attribute_line_ids.value_ids.attribute_id',
        'attribute_line_ids.value_ids.attribute_id.name',
    )
    def _compute_attributes(self):
        def get_value(rec, attribute_name):
            lines = rec.env['product.attribute.line'].search([
                ('attribute_id.name', '=', attribute_name),
                ('product_tmpl_id', '=', rec.id)], limit=1)
            return lines.value_ids and lines.value_ids[0] or False
        for rec in self:
            rec.author_id = get_value(rec, 'Autor')
            rec.editorial_id = get_value(rec, 'Editorial')
            rec.collection_id = get_value(rec, 'Colección')


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    def name_get(self, cr, uid, ids, context=None):
        """Este metodo lo sobreescribimos porque no nos esta pasando en el
        contexto el show_attribute False, supongo que debe tener que ver con un
        error de la nueva api
        """
        if not context:
            context = {}
        new_context = context.copy()
        new_context['show_attribute'] = False
        return super(ProductAttributeValue, self).name_get(
            cr, uid, ids, context=new_context)
