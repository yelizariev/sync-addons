# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTriggerWebhook(models.Model):

    _name = "sync.trigger.webhook"
    _description = "Webhook Trigger"

    action_server_id = fields.Many2one('ir.actions.server', delegate=True, required=True, ondelete='cascade')
