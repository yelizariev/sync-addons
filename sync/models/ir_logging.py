# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class IrLogging(models.Model):
    _inherit = "ir.logging"

    sync_job_id = fields.Many2one(
        "sync.job"
    )  # TODO make it computable (see log function)