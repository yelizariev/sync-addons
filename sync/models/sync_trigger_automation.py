# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models

from ..hooks import MODULE


class SyncTriggerAutomation(models.Model):

    _name = "sync.trigger.automation"
    _inherit = "sync.trigger.mixin"
    _description = "DB Trigger"
    _sync_handler = "handle_db"

    automation_id = fields.Many2one(
        "base.automation", delegate=True, required=True, ondelete="cascade"
    )

    @api.model
    def default_get(self, fields):
        vals = super(SyncTriggerAutomation, self).default_get(fields)
        vals["state"] = "code"
        return vals

    @api.model
    def create(self, vals):
        record = super(SyncTriggerAutomation, self).create(vals)
        record.code = record.get_code()
        # create ir.model.data record to safely remove base.automation records on module uninstallation
        self.env["ir.model.data"].create(
            {
                "module": MODULE,
                "model": "base.automation",
                "res_id": record.automation_id.id,
                "name": "_auto__base_automation_%s" % record.automation_id.id,
            }
        )

        return record

    def run(self, records):
        self.sync_task_id.run(self, args=(records,))

    def get_code(self):
        return (
            """
env["sync.trigger.automation"].browse(%s).run(records)
"""
            % self.id
        )
