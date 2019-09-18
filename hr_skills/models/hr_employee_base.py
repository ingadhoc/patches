# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from pytz import timezone, UTC
import babel
# from odoo.tools import format_time  redefine here because does not exist in 11


POSIX_TO_LDML = {
    'a': 'E',
    'A': 'EEEE',
    'b': 'MMM',
    'B': 'MMMM',
    #'c': '',
    'd': 'dd',
    'H': 'HH',
    'I': 'hh',
    'j': 'DDD',
    'm': 'MM',
    'M': 'mm',
    'p': 'a',
    'S': 'ss',
    'U': 'w',
    'w': 'e',
    'W': 'w',
    'y': 'yy',
    'Y': 'yyyy',
    # see comments above, and babel's format_datetime assumes an UTC timezone
    # for naive datetime objects
    #'z': 'Z',
    #'Z': 'z',
}


def posix_to_ldml(fmt, locale):
    """ Converts a posix/strftime pattern into an LDML date format pattern.

    :param fmt: non-extended C89/C90 strftime pattern
    :param locale: babel locale used for locale-specific conversions (e.g. %x and %X)
    :return: unicode
    """
    buf = []
    pc = False
    quoted = []

    for c in fmt:
        # LDML date format patterns uses letters, so letters must be quoted
        if not pc and c.isalpha():
            quoted.append(c if c != "'" else "''")
            continue
        if quoted:
            buf.append("'")
            buf.append(''.join(quoted))
            buf.append("'")
            quoted = []

        if pc:
            if c == '%': # escaped percent
                buf.append('%')
            elif c == 'x': # date format, short seems to match
                buf.append(locale.date_formats['short'].pattern)
            elif c == 'X': # time format, seems to include seconds. short does not
                buf.append(locale.time_formats['medium'].pattern)
            else: # look up format char in static mapping
                buf.append(POSIX_TO_LDML[c])
            pc = False
        elif c == '%':
            pc = True
        else:
            buf.append(c)

    # flush anything remaining in quoted buffer
    if quoted:
        buf.append("'")
        buf.append(''.join(quoted))
        buf.append("'")

    return ''.join(buf)


def format_time(env, value, tz=False, time_format='medium', lang_code=False):
    """ Format the given time (hour, minute and second) with the current user preference (language, format, ...)

        :param value: the time to format
        :type value: `datetime.time` instance. Could be timezoned to display tzinfo according to format (e.i.: 'full' format)
        :param format: one of “full”, “long”, “medium”, or “short”, or a custom date/time pattern
        :param lang_code: ISO

        :rtype str
    """
    if not value:
        return ''

    lang = env['res.lang']._lang_get(lang_code or env.context.get('lang') or 'en_US')
    locale = babel.Locale.parse(lang.code)
    if not time_format:
        time_format = posix_to_ldml(lang.time_format, locale=locale)

    return babel.dates.format_time(value, format=time_format, locale=locale)

class Employee(models.Model):

    _inherit = "hr.employee"
    # _description = 'Public Employee'
    # _order = 'name'
    # _auto = False
    # _log_access = True # Include magic fields

    name = fields.Char()
    active = fields.Boolean("Active")
    color = fields.Integer('Color Index', default=0)
    department_id = fields.Many2one('hr.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_id = fields.Many2one('hr.job', 'Job Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_title = fields.Char("Job Title")
    company_id = fields.Many2one('res.company', 'Company')
    address_id = fields.Many2one('res.partner', 'Work Address', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    work_phone = fields.Char('Work Phone')
    mobile_phone = fields.Char('Work Mobile')
    work_email = fields.Char('Work Email')
    work_location = fields.Char('Work Location')
    user_id = fields.Many2one('res.users')
    resource_id = fields.Many2one('resource.resource')
    resource_calendar_id = fields.Many2one('resource.calendar', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    tz = fields.Selection(
        string='Timezone', related='resource_id.tz', readonly=False,
        help="This field is used in order to define in which timezone the resources will work.")
    hr_presence_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('to_define', 'To Define')], compute='_compute_presence_state', default='to_define')
    last_activity = fields.Date(compute="_compute_last_activity")
    last_activity_time = fields.Char(compute="_compute_last_activity")

    # from skill module
    resume_line_ids = fields.One2many('hr.resume.line', 'employee_id', string="Resumé lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills")

    @api.depends('user_id.im_status')
    def _compute_presence_state(self):
        """
        This method is overritten in several other modules which add additional
        presence criterions. e.g. hr_attendance, hr_holidays
        """
        # Check on login
        check_login = self.env['ir.config_parameter'].sudo().get_param('hr.hr_presence_control_login')
        for employee in self:
            state = 'to_define'
            if check_login:
                if employee.user_id.im_status == 'online':
                    state = 'present'
                elif employee.user_id.im_status == 'offline':
                    state = 'absent'
            employee.hr_presence_state = state

    @api.depends('user_id')
    def _compute_last_activity(self):
        presences = self.env['bus.presence'].search_read([('user_id', 'in', self.mapped('user_id').ids)], ['user_id', 'last_presence'])
        # transform the result to a dict with this format {user.id: last_presence}
        presences = {p['user_id']: p['last_presence'] for p in presences}

        for employee in self:
            tz = employee.tz
            last_presence = presences.get(employee.user_id.id, False)
            if last_presence:
                last_activity_datetime = last_presence.replace(tzinfo=UTC).astimezone(timezone(tz)).replace(tzinfo=None)
                employee.last_activity = last_activity_datetime.date()
                if employee.last_activity == fields.Date.today():
                    employee.last_activity_time = format_time(self.env, last_activity_datetime, time_format='short')
                else:
                    employee.last_activity_time = False
            else:
                employee.last_activity = False
                employee.last_activity_time = False

    @api.model
    def create(self, vals):
        res = super().create(vals)
        resume_lines_values = []
        for employee in res:
            line_type = self.env.ref('hr_skills.resume_type_experience', raise_if_not_found=False)
            resume_lines_values.append({
                'employee_id': employee.id,
                'name': employee.company_id.name or '',
                'date_start': employee.create_date.date(),
                'description': employee.job_title or '',
                'line_type_id': line_type and line_type.id,
            })
        self.env['hr.resume.line'].create(resume_lines_values)
        return res


class EmployeePublic(models.Model):

    _name = "hr.employee.public"
    _inherit = ["hr.employee"]
    _description = 'Public Employee'
    _order = 'name'
    _auto = False
    _log_access = True # Include magic fields

    # hr.employee.public specific fields
    parent_id = fields.Many2one('hr.employee.public', 'Manager', readonly=True)
    child_ids = fields.One2many('hr.employee.public', 'parent_id', string='Direct subordinates', readonly=True)

    # image_1920 = fields.Binary("Original Image", compute='_compute_image', compute_sudo=True)
    # image_1024 = fields.Binary("Image 1024", compute='_compute_image', compute_sudo=True)
    # image_512 = fields.Binary("Image 512", compute='_compute_image', compute_sudo=True)
    # image_256 = fields.Binary("Image 256", compute='_compute_image', compute_sudo=True)
    # image_128 = fields.Binary("Image 128", compute='_compute_image', compute_sudo=True)
    # image_64 = fields.Binary("Image 64", compute='_compute_image', compute_sudo=True)

    coach_id = fields.Many2one('hr.employee.public', 'Coach', readonly=True)

    image = fields.Binary("Image", compute='_compute_image', compute_sudo=True)
    image_medium = fields.Binary("Image Medium", compute='_compute_image', compute_sudo=True)
    image_small = fields.Binary("Image small", compute='_compute_image', compute_sudo=True)

    def _compute_image(self):
        for employee in self:
            # We have to be in sudo to have access to the images
            employee_id = self.sudo().env['hr.employee'].browse(employee.id)
            # employee.image_1920 = employee_id.image_1920
            # employee.image_1024 = employee_id.image_1024
            # employee.image_512 = employee_id.image_512
            # employee.image_256 = employee_id.image_256
            # employee.image_128 = employee_id.image_128
            # employee.image_64 = employee_id.image_64

            employee.image = employee_id.image
            employee.image_medium = employee_id.image_medium
            employee.image_small = employee_id.image_small

    @api.model
    def _get_fields(self):
        return ','.join(
            'emp.%s' % name for name, field in self._fields.items()
            if field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT
                %s
            FROM hr_employee emp
        )""" % (self._table, self._get_fields()))
