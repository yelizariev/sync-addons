# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @property
    def odoo(self):
        res = None
        for r in self:
            record = self.env[r.model].browse(r.res_id)
            if res:
                res |= record
            else:
                res = record
        return res

    @property
    def external(self):
        res = [r.name for r in self]
        if len(res) == 1:
            return res[0]
        return res

    @property
    def sync_date(self):
        return min(r.date_update for r in self)

    def update_links(self, sync_date=None):
        if not sync_date:
            sync_date = fields.Datetime.now()
        self.write({"date_update": sync_date})
