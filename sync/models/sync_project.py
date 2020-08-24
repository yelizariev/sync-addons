# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import json
import logging
import time

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.translate import _

from ..tools import safe_eval_extra, test_python_expr_extra
from .ir_logging import LOG_CRITICAL, LOG_DEBUG, LOG_ERROR, LOG_INFO, LOG_WARNING

_logger = logging.getLogger(__name__)


def cleanup_eval_context(eval_context):
    delete = [k for k in eval_context if k.startswith("_")]
    for k in delete:
        del eval_context[k]
    return eval_context


class SyncProject(models.Model):

    _name = "sync.project"
    _description = "Sync Project"

    name = fields.Char(
        "Name", help="e.g. Legacy Migration or eCommerce Synchronization", required=True
    )
    active = fields.Boolean(default=True)
    secret_code = fields.Text(
        "Protected Code",
        groups="sync.sync_group_manager",
        help="""First code to eval.

        Secret Params and package importing are available here only.

        Any variables and functions that don't start with underscore symbol will be available in Common Code and task's code.

        To log transmitted data, use log_transmission(receiver, data) function.
        """,
    )

    secret_code_readonly = fields.Text(
        "Protected Code (Readonly)", compute="_compute_secret_code_readonly"
    )
    common_code = fields.Text(
        "Common Code",
        help="""
        A place for helpers and constants.

        You can add here a function or variable, that don't start with underscore and then reuse it in task's code.
    """,
    )
    param_ids = fields.One2many("sync.project.param", "project_id")
    secret_ids = fields.One2many("sync.project.secret", "project_id")
    task_ids = fields.One2many("sync.task", "project_id")
    task_count = fields.Integer(compute="_compute_task_count")
    active_task_ids = fields.Many2many(
        "sync.task",
        string="Enabled Tasks",
        compute="_compute_active_task_ids",
        inverse="_inverse_active_task_ids",
        context={"active_test": False},
    )
    trigger_cron_count = fields.Integer(
        compute="_compute_triggers", help="Enabled Crons"
    )
    trigger_automation_count = fields.Integer(
        compute="_compute_triggers", help="Enabled DB Triggers"
    )
    trigger_webhook_count = fields.Integer(
        compute="_compute_triggers", help="Enabled Webhooks"
    )
    trigger_button_count = fields.Integer(
        compute="_compute_triggers", help="Enabled Buttons"
    )
    trigger_button_ids = fields.Many2many(
        "sync.trigger.button", compute="_compute_triggers"
    )
    job_ids = fields.One2many("sync.job", "project_id")
    job_count = fields.Integer(compute="_compute_job_count")
    log_ids = fields.One2many("ir.logging", "sync_project_id")
    log_count = fields.Integer(compute="_compute_log_count")

    def _compute_secret_code_readonly(self):
        for r in self:
            r.secret_code_readonly = (r.sudo().secret_code or "").strip()

    def _compute_network_access_readonly(self):
        for r in self:
            r.network_access_readonly = r.sudo().network_access

    @api.depends("task_ids")
    def _compute_task_count(self):
        for r in self:
            r.task_count = len(r.with_context(active_test=False).task_ids)

    @api.depends("job_ids")
    def _compute_job_count(self):
        for r in self:
            r.job_count = len(r.job_ids)

    @api.depends("log_ids")
    def _compute_log_count(self):
        for r in self:
            r.log_count = len(r.log_ids)

    def _compute_triggers(self):
        for r in self:
            r.trigger_cron_count = len(r.mapped("task_ids.cron_ids"))
            r.trigger_automation_count = len(r.mapped("task_ids.automation_ids"))
            r.trigger_webhook_count = len(r.mapped("task_ids.webhook_ids"))
            r.trigger_button_count = len(r.mapped("task_ids.button_ids"))
            r.trigger_button_ids = r.mapped("task_ids.button_ids")

    def _compute_active_task_ids(self):
        for r in self:
            r.active_task_ids = r.task_ids

    def _inverse_active_task_ids(self):
        for r in self:
            (r.active_task_ids - r.task_ids).write({"active": True})
            (r.task_ids - r.active_task_ids).write({"active": False})

    @api.constrains("secret_code", "common_code")
    def _check_python_code(self):
        for r in self.sudo().filtered("secret_code"):
            msg = test_python_expr_extra(
                expr=(r.secret_code or "").strip(), mode="exec"
            )
            if msg:
                raise ValidationError(msg)

        for r in self.sudo().filtered("common_code"):
            msg = test_python_expr(expr=(r.common_code or "").strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def _get_log_function(self, job, function):
        self.ensure_one()

        def _log(cr, message, level):
            cr.execute(
                """
                INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func, sync_job_id)
                VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    self.env.uid,
                    "server",
                    self._cr.dbname,
                    "Sync Studio Log",
                    level,
                    message,
                    "sync.job",
                    job.id,
                    function,
                    job.id,
                ),
            )

        def log(message, level=LOG_INFO):
            if self.env.context.get("new_cursor_logs") is False:
                return _log(self.env.cr, message, level)

            with self.env.registry.cursor() as cr:
                return _log(cr, message, level)

        return log

    def _get_eval_context(self, job, log):
        """Executed Secret and Common codes and return "exported" variables and functions"""
        self.ensure_one()
        log("Job started", LOG_DEBUG)
        start_time = time.time()

        def call_async(function, **options):
            if callable(function):
                function = function.__name__

            def f(*args, **kwargs):
                sub_job = self.env["sync.job"].create({"parent_job_id": job.id})
                queue_job = job.task_id.with_delay(**options).run(
                    sub_job, function, args, kwargs
                )
                sub_job.queue_job_id = queue_job.db_record()
                log(
                    "call_async: %s(*%s, **%s). See %s"
                    % (function, args, kwargs, sub_job),
                    level=LOG_INFO,
                )

            return f

        params = AttrDict()
        for p in self.param_ids:
            params[p.key] = p.value

        secrets = AttrDict()
        for p in self.sudo().secret_ids:
            secrets[p.key] = p.value

        webhooks = AttrDict()
        for w in self.task_ids.mapped("webhook_ids"):
            webhooks[w.trigger_name] = w.website_url

        def log_transmission(recipient_str, data_str):
            # TODO
            log("{}: {}".format(recipient_str, data_str))

        def safe_getattr(o, k, d=None):
            if k.startswith("_"):
                raise ValidationError(_("You cannot use %s with getattr") % k)
            return getattr(o, k, d)

        def safe_setattr(o, k, v):
            if k.startswith("_"):
                raise ValidationError(_("You cannot use %s with setattr") % k)
            return setattr(o, k, v)

        # TODO: add links functions
        eval_context = {
            "env": self.env,
            "log": log,
            "log_transmission": log_transmission,
            "LOG_DEBUG": LOG_DEBUG,
            "LOG_INFO": LOG_INFO,
            "LOG_WARNING": LOG_WARNING,
            "LOG_ERROR": LOG_ERROR,
            "LOG_CRITICAL": LOG_CRITICAL,
            "params": params,
            "secrets": secrets,
            "webhooks": webhooks,
            "user": self.env.user,
            "trigger_name": job.trigger_name,
            "call_async": call_async,
            "json": json,
            "UserError": UserError,
            "getattr": safe_getattr,
            "setattr": safe_setattr,
        }
        log("Reading project data: %05.3f sec" % (time.time() - start_time), LOG_DEBUG)

        start_time = time.time()
        safe_eval_extra(
            self.secret_code_readonly, eval_context, mode="exec", nocopy=True
        )
        log(
            "Executing Protected Code: %05.3f sec" % (time.time() - start_time),
            LOG_DEBUG,
        )
        del eval_context["secrets"]
        cleanup_eval_context(eval_context)

        start_time = time.time()
        safe_eval(
            (self.common_code or "").strip(), eval_context, mode="exec", nocopy=True
        )
        log("Executing Common Code: %05.3f sec" % (time.time() - start_time), LOG_DEBUG)
        cleanup_eval_context(eval_context)
        return eval_context


class SyncProjectParamMixin(models.AbstractModel):

    _name = "sync.project.param.mixin"
    _description = "Template model for Parameters"
    _rec_name = "key"

    key = fields.Char("Key", required=True)
    value = fields.Char("Value")
    description = fields.Char("Description", translate=True)
    project_id = fields.Many2one("sync.project")

    _sql_constraints = [("key_uniq", "unique (project_id, key)", "Key must be unique.")]


class SyncProjectParam(models.Model):

    _name = "sync.project.param"
    _description = "Project Parameter"
    _inherit = "sync.project.param.mixin"

    value = fields.Char("Value", translate=True)


class SyncProjectSecret(models.Model):

    _name = "sync.project.secret"
    _description = "Project Secret Parameter"
    _inherit = "sync.project.param.mixin"

    value = fields.Char(groups="sync.sync_group_manager")


# see https://stackoverflow.com/a/14620633/222675
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
