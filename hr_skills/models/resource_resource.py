from odoo import fields, models, api
from odoo.addons.base.res.res_partner import _tz_get


# Copy part of code from resource odoo/master branch


class ResourceResource(models.Model):

    _inherit = "resource.resource"

    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        default=lambda self: self._context.get('tz') or self.env.user.tz or 'UTC',
        help="This field is used in order to define in which timezone the resources will work.")
