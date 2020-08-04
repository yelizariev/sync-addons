# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTriggerButton(models.Model):

    _name = "sync.trigger.button"
    _inherit = "sync.trigger.mixin"
    _description = "Manual Trigger"

    name = fields.Char("Description")
    sync_task_id = fields.Many2one("sync.task")

    def run(self):
        raise NotImplementedError()
