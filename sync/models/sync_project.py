# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncProject(models.Model):

    _name = "sync.project"
    _description = "Sync Project"

    name = fields.Char("Name", help="e.g. Legacy Migration or eCommerce Synchronization")
    common_code = fields.Text("Common Code")
    secret_code = fields.Text("Protected Code", groups="sync.sync_group_manager")
    secret_code_readonly = fields.Text("Protected Code", compute="_compute_secret_code_readonly")
    network_access = fields.Boolean("Network Access", groups="sync.sync_group_manager")
    network_access_readonly = fields.Boolean("Network Access", compute="_compute_network_access_readonly")
    param_ids = fields.One2many("sync.project.param", "project_id")
    secret_ids = fields.One2many("sync.project.secret", "project_id")
    task_ids = fields.One2many("sync.task", "project_id")

    def _compute_secret_code_readonly(self):
        for r in self:
            r.secret_code_readonly = r.sudo().secret_code

    def _compute_network_access_readonly(self):
        for r in self:
            r.network_access_readonly = r.sudo().network_access


class SyncProjectParam(models.Model):

    _name = "sync.project.param"

    name = fields.Char("Key")
    value = fields.Char("Value")
    project_id = fields.Many2one("sync.project")


class SyncProjectSecret(models.Model):

    _name = "sync.project.secret"
    _inherit = "sync.project.param"

    value = fields.Char(groups="sync.sync_group_manager")
