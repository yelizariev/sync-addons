# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncTask(models.Model):

    _name = 'sync.task'
    _description = 'Sync Task'

    project_id = fields.Many2one("sync.project")
