# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.tools.translate import _


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
        return super(SyncTriggerCron, self).create(vals_list)

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
