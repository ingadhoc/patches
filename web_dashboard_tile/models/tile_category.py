# © 2018 Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class TileCategory(models.Model):
    _name = 'tile.category'
    _description = 'Dashboard Tile Category'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer(
        help="Used to order the tile categories",
        default=0)
    fold = fields.Boolean('Folded by default')
