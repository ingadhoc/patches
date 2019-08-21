[![Runbot Status](http://runbot.adhoc.com.ar/runbot/badge/flat/37/11.0.svg)](http://runbot.adhoc.com.ar/runbot/repo/github-com-ingadhoc-patches-37)
[![Build Status](https://travis-ci.org/ingadhoc/patches.svg?branch=11.0)](https://travis-ci.org/ingadhoc/patches)
[![Coverage Status](https://coveralls.io/repos/ingadhoc/patches/badge.png?branch=11.0)](https://coveralls.io/r/ingadhoc/patches?branch=11.0)
[![Code Climate](https://codeclimate.com/github/ingadhoc/patches/badges/gpa.svg)](https://codeclimate.com/github/ingadhoc/patches)

# ADHOC Odoo Patches

Odoo patches, fixes, modules overwrite and other stuff that should be deleted :) Edit

account_analytic_default:
    * backport from odoo v12 to have support for analytic tags (with a fix, search for "# fix/patch" on the module)

web_pdf_preview:
    * backport from https://bitbucket.org/biosbillingsoftware/odoo-web-pdf-preview-print/overview
    * con algunos cambios en js para que no de error
    * con dependencia con report_custom_filename para que no de error y tmb para que no mande a descargar si custom file name

web_m2x_options:
    en este commit https://github.com/OCA/web/commit/e37db6412aa4ca85c8ad1635c49e9150a202f5af que hace que si se desactiva el create edit de manera global, no importa que en los pickings se fuerce que permita, no te deja crear registro, por ejemplo esto pasaba en boggio

mgmtsystem_nonconformity:
    agregado desde este PR https://github.com/OCA/management-system/pull/217/files
    TODO borrar cuando se apruebe el PR

auth_brute_force:
    disable this module by adding a 1 on res_users methods. This is till we fix the module compatibility with saas_client and auth_oauth. We also hide de menu for now because it is not being used for nothing.

website_sale_breadcrumb:
    modulo agregado desde https://www.odoo.com/apps/modules/11.0/website_sale_breadcrumb/

[//]: # (addons)
[//]: # (end addons)

----

<img alt="ADHOC" src="http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png" />
**Adhoc SA** - www.adhoc.com.ar
