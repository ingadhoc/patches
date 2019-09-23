# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Skills Management',
    'category': 'Hidden',
    'version': '11.0.1.0.0',
    'summary': 'Manage skills, knowledge and resumé of your employees',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_skills_security.xml',
        'views/hr_resume_line_view.xml',
        'views/hr_skill_view.xml',
        'views/hr_employee_views.xml',
        'data/hr_resume_data.xml',
    ],
    'demo': [
        'data/hr_resume_demo.xml',
        'data/hr.employee.skill.csv',
        'data/hr.resume.line.csv',
    ],
    'installable': True,
    'application': True,
}
