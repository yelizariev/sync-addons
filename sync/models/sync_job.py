# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models

TRIGGER_MODEL2FIELD = {
    "sync.trigger.cron": "trigger_cron_id",
    "sync.trigger.automation": "trigger_automation_id",
    "sync.trigger.webhook": "trigger_webhook_id",
    "sync.trigger.button": "trigger_button_id",
}
TRIGGER_FIELDS = TRIGGER_MODEL2FIELD.values()


class SyncJob(models.Model):

    _name = "sync.job"
    _description = "Sync Job"

    trigger_name = fields.Char(compute="_compute_trigger_name")
    trigger_cron_id = fields.Many2one("sync.trigger.cron")
    trigger_automation_id = fields.Many2one("sync.trigger.automation")
    trigger_webhook_id = fields.Many2one("sync.trigger.webhook")
    trigger_button_id = fields.Many2one("sync.trigger.button")
    task_id = fields.Many2one("sync.task", compute="_compute_sync_task_id", store=True)
    project_id = fields.Many2one("sync.project", related="task_id.project_id")
    parent_job_id = fields.Many2one("sync.job")
    job_ids = fields.Many2one("queue.job", "Sub jobs")
    queue_job_id = fields.Many2one("queue.job")
    log_ids = fields.One2many("ir.logging", "sync_job_id")

    @api.depends("parent_job_id", *TRIGGER_FIELDS)
    def _compute_sync_task_id(self):
        for r in self:
            if r.parent_job_id:
                r.task_id = r.parent_job_id.task_id
            for f in TRIGGER_FIELDS:
                obj = getattr(r, f)
                if obj:
                    r.task_id = obj.sync_task_id
                    break

    @api.depends(*TRIGGER_FIELDS)
    def _compute_trigger_name(self):
        for r in self:
            if r.parent_job_id:
                r.trigger_name = "SUB_" + r.parent_job_id.trigger_name
                continue
            for f in TRIGGER_FIELDS:
                t = getattr(r, f)
                if t:
                    r.trigger_name = t.trigger_name
                    break

    def post_handler(self, args, kwargs, result):
        self.ensure_one()
        for f in TRIGGER_FIELDS:
            trigger = getattr(self, f)
            if not trigger:
                continue
            if hasattr(trigger, "_sync_post_handler"):
                return trigger._sync_post_handler(args, result)

    def create_trigger_job(self, trigger):
        return self.create({TRIGGER_MODEL2FIELD[trigger._name]: trigger.id})
