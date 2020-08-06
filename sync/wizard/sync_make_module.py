# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncMakeModule(models.TransientModel):
    _name = "sync.make.module"
    _description = "Generating XML data file for a module"

    name = fields.Char("File Name", readonly=True, default="sync_project_data.xml")
    data = fields.Binary("File", readonly=True, attachment=False)
    copyright_years = fields.Char("Copyright Years", default="2020")
    author_name = fields.Char("Author Name", help="e.g. Ivan Yelizariev")
    author_url = fields.Char("Author URL", help="e.g. https://twitter.com/yelizariev")
    license = fields.Char("License", default="License MIT (https://opensource.org/licenses/MIT).")
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    project_id = fields.Many2one("sync.project")

    @api.multi
    def act_makefile(self):
        data = TODO

        self.write({'state': 'get', 'data': data})
