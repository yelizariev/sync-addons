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

    @api.constrains("code")
    def _check_python_code(self):
        for r in self.sudo().filtered("code"):
            msg = test_python_expr(expr=r.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def start(self, trigger, args=None, with_delay=False):

        self.ensure_one()

        run = self.run.with_delay() if with_delay else self.run
        run(trigger, args)

        return job

    @job
    def run(self, trigger, args=None):
        eval_context = self.project_id._get_eval_context(trigger)

        function = trigger._sync_handler

        result = self._eval(function, args, eval_context)

        if hasattr(trigger, "_sync_post_handler"):
            trigger._sync_post_handler(args, result)

        return job

    def _eval(self, function, args, eval_context):
        ARGS = "EXECUTION_ARGS_"
        RESULT = "EXECUTION_RESULT_"

        code = self.code.strip()
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
