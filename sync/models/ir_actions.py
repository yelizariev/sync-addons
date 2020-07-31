# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    sync_task_id = fields.Many2one("sync.task")

    @api.model
    def _get_links_functions(self):
        TODO


class Link():

    def __len__(self):
        # Is used for ``elinks.length`` and for ``bool(elinks)``
        TODO
