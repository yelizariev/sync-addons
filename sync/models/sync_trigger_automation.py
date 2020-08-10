# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncTriggerAutomation(models.Model):

    _name = "sync.trigger.automation"
    _inherit = "sync.trigger.mixin"
    _description = "DB Trigger"
    _sync_handler = "handle_db"

    automation_id = fields.Many2one(
        "base.automation", delegate=True, required=True, ondelete="cascade"
    )
