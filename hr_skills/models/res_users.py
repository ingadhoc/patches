# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class User(models.Model):
    _inherit = ['res.users']

    employee_id = fields.Many2one('hr.employee', string="Company employee",
        compute='_compute_company_employee', search='_search_company_employee', store=False)

    resume_line_ids = fields.One2many(related='employee_id.resume_line_ids', readonly=False)
    employee_skill_ids = fields.One2many(related='employee_id.employee_skill_ids', readonly=False)

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        hr_skills_fields = [
            'resume_line_ids',
            'employee_skill_ids',
        ]
        init_res = super(User, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + hr_skills_fields
        type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + hr_skills_fields
        return init_res

    @api.depends('employee_ids')
    # @api.depends_context('force_company')
    def _compute_company_employee(self):
        for user in self:
            user.employee_id = self.env['hr.employee'].search([('id', 'in', user.employee_ids.ids), ('company_id', '=', self.env.company.id)], limit=1)

    def _search_company_employee(self, operator, value):
        employees = self.env['hr.employee'].search([
            ('name', operator, value),
            '|',
            ('company_id', '=', self.env.company.id),
            ('company_id', '=', False)
        ], order='company_id ASC')
        return [('id', 'in', employees.mapped('user_id').ids)]
