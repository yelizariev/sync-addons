# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTriggerCron(models.Model):

    _name = "sync.trigger.cron"
    _inherit = "sync.trigger.mixin"
    _description = "Cron Trigger"

    cron_id = fields.Many2one('ir.cron', delegate=True, required=True, ondelete='cascade')
