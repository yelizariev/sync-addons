# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models

LOG_DEBUG = "debug"
LOG_INFO = "info"
LOG_WARNING = "warning"
LOG_ERROR = "error"
LOG_CRITICAL = "critical"


class IrLogging(models.Model):
    _inherit = "ir.logging"

    sync_job_id = fields.Many2one("sync.job")
    sync_task_id = fields.Many2one("sync.task", related="sync_job_id.task_id")
    sync_project_id = fields.Many2one(
        "sync.project", related="sync_job_id.task_id.project_id"
    )
