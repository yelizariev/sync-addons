# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncJob(models.Model):

    # TODO: this model can be deleted
    _name = "sync.job"
    _description = "Sync Job"

    trigger_cron_id = fields.Many2one("sync.trigger.cron")
    trigger_automation_id = fields.Many2one("sync.trigger.automation")
    trigger_webhook_id = fields.Many2one("sync.trigger.webhook")
    trigger_button_id = fields.Many2one("sync.trigger.button")
