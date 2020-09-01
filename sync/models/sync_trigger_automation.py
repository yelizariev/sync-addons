# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncTriggerAutomation(models.Model):

    _name = "sync.trigger.automation"
    _inherit = ["sync.trigger.mixin", "sync.trigger.mixin.actions"]
    _description = "DB Trigger"
    _sync_handler = "handle_db"
    _default_name = "DB Trigger"

    automation_id = fields.Many2one(
        "base.automation", delegate=True, required=True, ondelete="cascade"
    )

    def start(self, records):
        if self.active:
            self.sync_task_id.start(self, args=(records,))

    def get_code(self):
        return (
            """
env["sync.trigger.automation"].browse(%s).start(records)
"""
            % self.id
        )
