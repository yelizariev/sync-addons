# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class IrLogging(models.Model):
    _inherit = 'ir.logging'

    sync_job_id = fields.Many2one("sync.job")
