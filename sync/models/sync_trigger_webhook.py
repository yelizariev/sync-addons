# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.http import request

from ..hooks import MODULE


class SyncTriggerWebhook(models.Model):

    _name = "sync.trigger.webhook"
    _inherit = ["sync.trigger.mixin", "sync.trigger.mixin.model_id"]
    _description = "Webhook Trigger"
    _sync_handler = "handle_webhook"
    _default_name = "Webhook"

    action_server_id = fields.Many2one(
        "ir.actions.server", delegate=True, required=True, ondelete="cascade"
    )
    active = fields.Boolean(default=True)
    webhook_type = fields.Selection(
        [("http", "application/x-www-form-urlencoded"), ("json", "application/json")],
        string="Webhook Type",
        default="json",
    )
    website_url = fields.Char("Website URL", compute="_compute_website_url")

    @api.depends(
        "webhook_type",
        "action_server_id.state",
        "action_server_id.website_published",
        "action_server_id.website_path",
        "action_server_id.xml_id",
    )
    def _compute_website_url(self):
        for r in self:
            website_url = r.action_server_id.website_url
            if not website_url:
                continue
            if r.webhook_type == "json":
                website_url = website_url.replace(
                    "/website/action/", "/website/action-json/"
                )
            r.website_url = website_url

    @api.model
    def default_get(self, fields):
        vals = super(SyncTriggerWebhook, self).default_get(fields)
        vals["state"] = "code"
        vals["website_published"] = True
        return vals

    @api.model
    def create(self, vals):
        record = super(SyncTriggerWebhook, self).create(vals)
        record.code = record.get_code()
        # create ir.model.data record to safely remove ir.actions.server records on module uninstallation
        self.env["ir.model.data"].create(
            {
                "module": MODULE,
                "model": "ir.actions.server",
                "res_id": record.action_server_id.id,
                "name": "_auto__ir_action_server_%s" % record.action_server_id.id,
            }
        )

        return record

    def start(self):
        record = self.sudo()
        # import wdb; wdb.set_trace()
        if record.active:
            record.sync_task_id.start(record, args=(request.httprequest,))
        else:
            request.make_response("This webhook is disabled")

    def get_code(self):
        return (
            """
env["sync.trigger.webhook"].browse(%s).start()
"""
            % self.id
        )

    @api.model
    def _sync_post_handler(self, args, result):
        if not result:
            result = "OK"
        data_str = None
        headers = []
        if isinstance(result, tuple):
            data_str, headers = result
        else:
            data_str = result

        # odoo_1                    | ValueError: <class 'AttributeError'>: "'JsonRequest' object has no attribute 'make_response'" while evaluating
        request.make_response(data_str, headers)
        return True
