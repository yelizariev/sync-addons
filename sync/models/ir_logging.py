# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class IrLogging(models.Model):
    _inherit = "ir.logging"

    # Don't use normal field, because log method can be used before another cursor commits the sync.job creation
    sync_job_id = fields.Many2one(
        "sync.job", compute="_compute_sync_job_id", search="_search_sync_job_id"
    )

    def _compute_sync_job_id(self):
        for r in self:
            if r.path == "sync.job":
                r.sync_job_id = self.env["sync.job"].browse(r.line)

    def _search_sync_job_id(self, operator, value):
        return [("path", "=", "sync.job"), ("line", operator, value)]
