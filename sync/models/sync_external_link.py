# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class SyncExternalLink(models.Model):

    _name = "sync.external.link"
    _description = "External Link"

    relation_name = fields.Char("Relation Name")
    external1 = fields.Char("External 1")
    external2 = fields.Char("External 2")
    external1_ref = fields.Char("External 1 Ref")
    external2_ref = fields.Char("External 2 Ref")
    date_update = fields.Datetime(string='Update Date', default=fields.Datetime.now)

    # TODO: make indexes depending on search requests
