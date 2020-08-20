# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncTriggerButton(models.Model):

    _name = "sync.trigger.button"
    _inherit = "sync.trigger.mixin"
    _description = "Manual Trigger"
    _sync_handler = "handle_button"

    name = fields.Char("Description")
    sync_task_id = fields.Many2one("sync.task")
    sync_project_id = fields.Many2one(
        "sync.project", related="sync_task_id.project_id", readonly=True
    )
    active = fields.Boolean(default=True)

    def run(self):
        job = self.sync_task_id.start(self)
        return job  # just to prevent lint errors for a while
        # TODO: redirect to logs created during the run
