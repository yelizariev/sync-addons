# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.tools.translate import _

from ..hooks import MODULE


class SyncTriggerCron(models.Model):

    _name = "sync.trigger.cron"
    _inherit = ["sync.trigger.mixin", "sync.trigger.mixin.model_id"]
    _description = "Cron Trigger"
    _sync_handler = "handle_cron"

    cron_id = fields.Many2one(
        "ir.cron", delegate=True, required=True, ondelete="cascade"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("name", vals.get("trigger_name", "Sync"))
        records = super(SyncTriggerCron, self).create(vals_list)
        for r in records:
            r.code = r.get_code()
            # create ir.model.data record to safely remove base.automation records on module uninstallation
            self.env["ir.model.data"].create(
                {
                    "module": MODULE,
                    "model": "ir.cron",
                    "res_id": r.cron_id.id,
                    "name": "_auto__ir_cron_%s" % r.cron_id.id,
                }
            )
        return records

    def start_button(self):
        job = self.start(force=True)
        return {
            "name": "Job triggered by clicking Button",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sync.job",
            "res_id": job.id,
            "target": "self",
        }

    def start(self, force=False):
        return self.sync_task_id.start(self, with_delay=True, force=force)

    def get_code(self):
        return (
            """
env["sync.trigger.cron"].browse(%s).start()
"""
            % self.id
        )

    def name_get(self):
        result = []
        for r in self:
            name = _("%s: every %s %s") % (
                r.trigger_name,
                r.interval_number,
                r.interval_type,
            )
            if r.numbercall > 0:
                name += " (%s times)" % r.numbercall
            result.append((r.id, name))
        return result
