# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTriggerButton(models.Model):

    _name = "sync.trigger.Button"
    _description = "Manual Trigger"

    name = fields.Char("Name")
    data = fields.Char("Data", help="JSON data to be passed to the handler")
    sync_task_id = fields.Many2one("sync.task")

    def run(self):
        raise NotImplementedError()
