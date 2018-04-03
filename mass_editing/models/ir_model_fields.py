# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        model_domain = []
        for domain in args:
            if len(domain) > 2 and domain[0] == 'mass_editing_model_id':
                if isinstance(domain[2], basestring):
                    domain = ('model_id', 'in',
                              map(int, domain[2][1:-1].split(',')))
                else:
                    domain = ('model_id', 'in', domain[2])
            model_domain.append(domain)
        return super(IrModelFields, self).search(model_domain, offset=offset,
                                                 limit=limit, order=order,
                                                 count=count)
