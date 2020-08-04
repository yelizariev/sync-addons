# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncProject(models.Model):

    _name = "sync.project"
    _description = "Sync Project"

    name = fields.Char("Name", help="e.g. Legacy Migration or eCommerce Synchronization")
    secret_code = fields.Text(
        "Protected Code",
        groups="sync.sync_group_manager",
        help="""First code to eval.

        Secret Params and package importing are available here only.

        Any variables and functions that don't start with underscore symbol will be available in Common Code and task's code.

        To log transmitted data, use log_transmission(receiver, data) function.
        """)

    secret_code_readonly = fields.Text("Protected Code", compute="_compute_secret_code_readonly")
    common_code = fields.Text(
        "Common Code", help="""
        A place for helpers and constants.

        You can add here a function or variable, that don't start with underscore and then reuse it in task's code.
    """)
    param_ids = fields.One2many("sync.project.param", "project_id")
    secret_ids = fields.One2many("sync.project.secret", "project_id")
    task_ids = fields.One2many("sync.task", "project_id")

    def _compute_secret_code_readonly(self):
        for r in self:
            r.secret_code_readonly = r.sudo().secret_code

    def _compute_network_access_readonly(self):
        for r in self:
            r.network_access_readonly = r.sudo().network_access


class SyncProjectParamMixin(models.AbstractModel):

    _name = "sync.project.param.mixin"
    _rec_name = "key"

    key = fields.Char("Key")
    value = fields.Char("Value")
    description = fields.Char("Description", translate=True)
    project_id = fields.Many2one("sync.project")

    _sql_constraints = [
        ("key_uniq", "unique (key)", "Key must be unique.")
    ]


class SyncProjectParam(models.Model):

    _name = "sync.project.param"
    _inherit = "sync.project.param.mixin"

    value = fields.Char("Value", translate=True)


class SyncProjectSecret(models.Model):

    _name = "sync.project.secret"
    _inherit = "sync.project.param.mixin"

    value = fields.Char(groups="sync.sync_group_manager")
