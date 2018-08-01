# © 2010-2013 Odoo s.a. (<http://odoo.com>).
# © 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Dashboard Tile",
    "summary": "Add Tiles to Dashboard",
    "version": "11.0.1.0.0",
    "depends": [
        'web',
        'board',
        'mail',
        'web_widget_color',
    ],
    'author': 'initOS GmbH & Co. KG, '
              'GRAP, '
              'Odoo Community Association (OCA)',
    "category": "web",
    'license': 'AGPL-3',
    'contributors': [
        'initOS GmbH & Co. KG',
        'GRAP',
        'Iván Todorovich <ivan.todorovich@gmail.com>'
    ],
    'data': [
        'views/tile_tile_views.xml',
        'views/tile_tile_templates.xml',
        'security/ir.model.access.csv',
        'security/web_dashboard_tile_security.xml',
    ],
    'demo': [
        'demo/res_groups.yml',
        'demo/tile_category.yml',
        'demo/tile_tile.yml',
    ],
    'qweb': [
        'static/src/xml/custom_xml.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
