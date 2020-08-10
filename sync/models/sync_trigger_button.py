# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncTriggerButton(models.Model):

    _name = "sync.trigger.button"
    _inherit = "sync.trigger.mixin"
    _description = "Manual Trigger"
    _sync_handler = "handle_button"

    name = fields.Char("Description")
    sync_task_id = fields.Many2one("sync.task")

    def run(self):
        self.sync_task_id.run(self)
        # TODO: redirect to logs created during the run
