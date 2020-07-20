# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTrigger(models.Model):

    _name = "sync.trigger"
    _description = "Sync Trigger"

    task_id = fields.Many2one("sync.task")
    type = fields.Selection([
        ('cron', 'By Cron Schedule'),
        ('db', 'On Database Updates'),
        ('webhook', 'On Webhook request'),
        ('button', 'Manually'),
    ], string="Trigger Type", required=True)

    # TODO: add fields to configure the trigger
