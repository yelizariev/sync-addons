# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncProject(models.Model):

    _name = 'sync.project'
    _description = 'Sync Project'
