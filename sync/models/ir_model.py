# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models


class IrModelData(models.Model):
    _name = "ir.model.data"
    _inherit = ["ir.model.data", "sync.link.mixin"]

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
