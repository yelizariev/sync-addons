# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr

from odoo.addons.queue_job.job import job


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

    def start(self, trigger, args=None, with_delay=False):
        self.ensure_one()
        if not self.active or not self.project_id.active:
            return None

        job = self.env["sync.job"].create_trigger_job(trigger)
        run = self.with_delay().run if with_delay else self.run
        run(job, trigger._sync_handler, args)

        return job

    @job
    def run(self, job, function, args=None, kwargs=None):
        eval_context = self.project_id._get_eval_context(job)

        code = self.code.strip()
        result = self._eval(code, function, args, eval_context)

        job.post_handler(args, kwargs, result)

        return job

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
