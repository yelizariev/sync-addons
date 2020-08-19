# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTriggerWebhook(models.Model):

    _name = "sync.trigger.webhook"
    _inherit = ["sync.trigger.mixin", "sync.trigger.mixin.model_id"]
    _description = "Webhook Trigger"
    _sync_handler = "handle_webhook"
    _default_name = "Webhook"

    action_server_id = fields.Many2one(
        "ir.actions.server", delegate=True, required=True, ondelete="cascade"
    )
    active = fields.Boolean(active=True)

    @api.model
    def _sync_post_handler(self, args, result):
        httprequest = args[0]
        if result:
            data_str = None
            headers = []
            if isinstance(result, tuple):
                data_str, headers = result
            else:
                data_str = result

            httprequest.make_response(data_str, headers)
