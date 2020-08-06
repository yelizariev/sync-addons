# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTriggerCron(models.Model):

    _name = "sync.trigger.cron"
    _inherit = ["sync.trigger.mixin", "sync.trigger.mixin.model_id"]
    _description = "Cron Trigger"

    cron_id = fields.Many2one('ir.cron', delegate=True, required=True, ondelete='cascade')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("name", vals.get("trigger_name", "Sync"))
        return super(SyncTriggerCron, self).create(vals_list)
