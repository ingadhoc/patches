# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Skills Management',
    'category': 'Hidden',
    'version': '11.0.1.0.0',
    'summary': 'Manage skills, knowledge and resumé of your employees',
    'depends': [
        'hr',
        'resource',
    ],
    'data': [
        # from hr
        'views/hr_employee_public_views.xml',

        # from hr_skills
        'security/ir.model.access.csv',
        'security/hr_skills_security.xml',
        'views/hr_views.xml',
        'views/hr_templates.xml',
        'data/hr_resume_data.xml',
    ],
    'demo': [
        'data/hr_resume_demo.xml',
        'data/hr.employee.skill.csv',
        'data/hr.resume.line.csv',
    ],
    'qweb': [
        'static/src/xml/resume_templates.xml',
        'static/src/xml/skills_templates.xml',
    ],
    'installable': True,
    'application': True,
}
