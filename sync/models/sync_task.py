# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import time
import traceback
from io import StringIO

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr

from odoo.addons.queue_job.job import job

from .ir_logging import LOG_CRITICAL, LOG_DEBUG


class SyncTask(models.Model):

    _name = "sync.task"
    _description = "Sync Task"

    project_id = fields.Many2one("sync.project")
    name = fields.Char("Name", help="e.g. Sync Products", required=True)
    code = fields.Text("Code")
    active = fields.Boolean(default=True)
    cron_ids = fields.One2many("sync.trigger.cron", "sync_task_id")
    automation_ids = fields.One2many("sync.trigger.automation", "sync_task_id")
    webhook_ids = fields.One2many("sync.trigger.webhook", "sync_task_id")
    button_ids = fields.One2many("sync.trigger.button", "sync_task_id")
    active_cron_ids = fields.Many2many(
        "sync.trigger.cron",
        string="Enabled Crons",
        compute="_compute_active_triggers",
        inverse="_inverse_active_triggers",
        context={"active_test": False},
    )
    active_automation_ids = fields.Many2many(
        "sync.trigger.automation",
        string="Enabled DB Triggers",
        compute="_compute_active_triggers",
        inverse="_inverse_active_triggers",
        context={"active_test": False},
    )
    active_webhook_ids = fields.Many2many(
        "sync.trigger.webhook",
        string="Enabled Webhooks",
        compute="_compute_active_triggers",
        inverse="_inverse_active_triggers",
        context={"active_test": False},
    )
    active_button_ids = fields.Many2many(
        "sync.trigger.button",
        string="Enabled Buttons",
        compute="_compute_active_triggers",
        inverse="_inverse_active_triggers",
        context={"active_test": False},
    )

    @api.constrains("code")
    def _check_python_code(self):
        for r in self.sudo().filtered("code"):
            msg = test_python_expr(expr=r.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def _compute_active_triggers(self):
        for r in self:
            r.active_cron_ids = r.cron_ids
            r.active_automation_ids = r.automation_ids
            r.active_webhook_ids = r.webhook_ids
            r.active_button_ids = r.button_ids

    def _inverse_active_triggers(self):
        for r in self:
            (r.active_cron_ids - r.cron_ids).write({"active": True})
            (r.cron_ids - r.active_cron_ids).write({"active": False})

            (r.active_automation_ids - r.automation_ids).write({"active": True})
            (r.automation_ids - r.active_automation_ids).write({"active": False})

            (r.active_webhook_ids - r.webhook_ids).write({"active": True})
            (r.webhook_ids - r.active_webhook_ids).write({"active": False})

            (r.active_button_ids - r.button_ids).write({"active": True})
            (r.button_ids - r.active_button_ids).write({"active": False})

    def start(self, trigger, args=None, with_delay=False, force=False):
        self.ensure_one()
        if not force and not (self.active and self.project_id.active):
            return None

        job = self.env["sync.job"].create_trigger_job(trigger)
        run = self.with_delay().run if with_delay else self.run
        if not with_delay and self.env.context.get("new_cursor_logs") is not False:
            # log records are created via new cursor and they use job.id value for sync_job_id field
            self.env.cr.commit()  # pylint: disable=invalid-commit

        queue_job_or_none = run(job, trigger._sync_handler, args)
        if with_delay:
            job.queue_job_id = queue_job_or_none.db_record()

        return job

    @job
    def run(self, job, function, args=None, kwargs=None):
        log = self.project_id._get_log_function(job, function)
        try:
            eval_context = self.project_id._get_eval_context(job, log)
            code = self.code.strip()
            start_time = time.time()
            result = self._eval(code, function, args, eval_context)
            log(
                "Executing {}: {:05.3f} sec".format(function, time.time() - start_time),
                LOG_DEBUG,
            )
            start_time = time.time()
            has_post_handler = job.post_handler(args, kwargs, result)
            if has_post_handler:
                log(
                    "Executing _sync_post_handler: %05.3f sec"
                    % (time.time() - start_time),
                    LOG_DEBUG,
                )
            log("Job finished")
        except Exception:
            buff = StringIO()
            traceback.print_exc(file=buff)
            log(buff.getvalue(), LOG_CRITICAL)
            raise

    @api.model
    def _eval(self, code, function, args, eval_context):
        ARGS = "EXECUTION_ARGS_"
        RESULT = "EXECUTION_RESULT_"

        code += """
{RESULT} = {function}(*{ARGS})
        """.format(
            RESULT=RESULT, function=function, ARGS=ARGS
        )

        eval_context[ARGS] = args or ()

        safe_eval(
            code, eval_context, mode="exec", nocopy=True
        )  # nocopy allows to return RESULT
        return eval_context[RESULT]

    def name_get(self):
        if not self.env.context.get("name_with_project"):
            return super(SyncTask, self).name_get()
        result = []
        for r in self:
            name = r.project_id.name + ": " + r.name
            result.append((r.id, name))
        return result
