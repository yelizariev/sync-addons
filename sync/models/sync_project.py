# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import json
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr

from ..tools import safe_eval_imports, test_python_expr_imports

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
        "Name", help="e.g. Legacy Migration or eCommerce Synchronization"
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

    def _compute_secret_code_readonly(self):
        for r in self:
            r.secret_code_readonly = r.sudo().secret_code

    def _compute_network_access_readonly(self):
        for r in self:
            r.network_access_readonly = r.sudo().network_access

    @api.constrains("secret_code", "common_code")
    def _check_python_code(self):
        for r in self.sudo().filtered("secret_code"):
            msg = test_python_expr_imports(expr=r.secret_code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

        for r in self.sudo().filtered("common_code"):
            msg = test_python_expr(expr=r.common_code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def _get_eval_context(self, trigger):
        """Executed Secret and Common codes and return "exported" variables and functions"""
        self.ensure_one()

        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute(
                    """
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        self.env.uid,
                        "server",
                        self._cr.dbname,
                        __name__,
                        level,
                        message,
                        trigger._name,
                        trigger.id,
                        trigger.trigger_name,
                    ),
                )

        params = AttrDict()
        for p in self.param_ids:
            params[p.key] = p.value

        secrets = AttrDict()
        for p in self.sudo().secret_ids:
            secrets[p.key] = p.value

        webhooks = AttrDict()
        for w in self.task_ids.mapped("webhook_ids"):
            webhooks[w.trigger_name] = "TODO: get url"

        def log_transmission(recipient_str, data_str):
            # TODO
            log("{}: {}".format(recipient_str, data_str))

        # TODO: add links functions
        eval_context = {
            "env": self.env,
            "log": log,
            "log_transmission": log_transmission,
            "LOG_DEBUG": "debug",
            "LOG_INFO": "info",
            "LOG_WARNING": "warning",
            "LOG_ERROR": "error",
            "LOG_CRITICAL": "critical",
            "params": params,
            "secrets": secrets,
            "webhooks": webhooks,
            "user": self.env.user,
            "trigger_name": trigger.trigger_name,
            "async": "TODO",
            "json": json,
        }

        safe_eval_imports(
            self.secret_code_readonly.strip(), eval_context, mode="exec", nocopy=True
        )
        del eval_context["secrets"]
        cleanup_eval_context(eval_context)

        safe_eval(self.common_code.strip(), eval_context, mode="exec", nocopy=True)
        cleanup_eval_context(eval_context)
        return eval_context


class SyncProjectParamMixin(models.AbstractModel):

    _name = "sync.project.param.mixin"
    _description = "Template model for Parameters"
    _rec_name = "key"

    key = fields.Char("Key")
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