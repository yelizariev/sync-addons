# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.tools.translate import _

from odoo.addons.queue_job.job import DONE, ENQUEUED, FAILED, PENDING, STARTED

from .ir_logging import LOG_CRITICAL, LOG_ERROR, LOG_WARNING

DONE_WARNING = "done_warning"
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
    _rec_name = "trigger_name"
    _order = "id desc"

    trigger_name = fields.Char(compute="_compute_trigger_name", store=True)
    trigger_cron_id = fields.Many2one("sync.trigger.cron", readonly=True)
    trigger_automation_id = fields.Many2one("sync.trigger.automation", readonly=True)
    trigger_webhook_id = fields.Many2one("sync.trigger.webhook", readonly=True)
    trigger_button_id = fields.Many2one("sync.trigger.button", readonly=True)
    task_id = fields.Many2one("sync.task", compute="_compute_sync_task_id", store=True)
    project_id = fields.Many2one(
        "sync.project", related="task_id.project_id", readonly=True
    )
    parent_job_id = fields.Many2one("sync.job", readonly=True)
    job_ids = fields.One2many("sync.job", "parent_job_id", "Sub jobs", readonly=True)
    log_ids = fields.One2many("ir.logging", "sync_job_id", readonly=True)
    log_count = fields.Integer(compute="_compute_log_count")
    queue_job_id = fields.Many2one("queue.job", string="Queue Job", readonly=True)
    func_string = fields.Char(related="queue_job_id.func_string", readonly=True)
    retry = fields.Integer(related="queue_job_id.retry", readonly=True)
    max_retries_str = fields.Char(compute="_compute_max_retries_str")
    state = fields.Selection(
        [
            (PENDING, "Pending"),
            (ENQUEUED, "Enqueued"),
            (STARTED, "Started"),
            (DONE, "Done"),
            (DONE_WARNING, "Done With Warnings"),
            (FAILED, "Failed"),
        ],
        compute="_compute_state",
    )
    in_progress = fields.Boolean(compute="_compute_state",)

    @api.depends("queue_job_id.max_retries")
    def _compute_max_retries_str(self):
        for r in self:
            max_retries = r.queue_job_id.max_retries
            if not max_retries:
                r.max_retries_str = _("infinity")
            else:
                r.max_retries_str = str(max_retries)

    @api.depends("queue_job_id", "job_ids.queue_job_id.state", "log_ids.level")
    def _compute_state(self):
        for r in self:
            jobs = r + r.job_ids
            states = [q.state for q in jobs.mapped("queue_job_id")]
            levels = {log.level for log in jobs.mapped("log_ids")}
            computed_state = DONE
            has_errors = any(lev in [LOG_CRITICAL, LOG_ERROR] for lev in levels)
            has_warnings = any(lev == LOG_WARNING for lev in levels)
            if jobs:
                for s in [FAILED, STARTED, ENQUEUED, PENDING]:
                    if any(s == ss for ss in states):
                        computed_state = s
                        break
            else:
                if has_errors:
                    computed_state = FAILED

            if computed_state == DONE and has_warnings:
                computed_state = DONE_WARNING

            r.state = computed_state
            r.in_progress = any(s in [PENDING, ENQUEUED, STARTED] for s in states)

    @api.depends("log_ids")
    def _compute_log_count(self):
        for r in self:
            r.log_count = len(r.log_ids)

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
                r.trigger_name = "SUB_" + (r.parent_job_id.trigger_name or "")
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

    def refresh_button(self):
        # magic empty method to refresh form content
        pass