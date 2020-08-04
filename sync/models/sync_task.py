# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTask(models.Model):

    _name = "sync.task"
    _description = "Sync Task"

    project_id = fields.Many2one("sync.project")
    name = fields.Char("Name", help="e.g. Sync Products")
    code = fields.Text("Code")
    cron_ids = fields.One2many("sync.trigger.cron", "sync_task_id")
    automation_ids = fields.One2many("sync.trigger.automation", "sync_task_id")
    webhook_ids = fields.One2many("sync.trigger.webhook", "sync_task_id")
    button_ids = fields.One2many("sync.trigger.button", "sync_task_id")
