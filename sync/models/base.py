# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models
from odoo.exceptions import ValidationError


class Base(models.AbstractModel):
    _inherit = "base"

    def set_link(self, relation_name, ref, sync_date=None):
        self.ensure_one()
        existing = self.search_links(relation_name)
        if existing:
            if existing.name != ref:
                raise ValidationError(
                    "Link already exists: record={}, ref={}".format(
                        existing, existing.name
                    )
                )
            existing.update_links(sync_date)
            return existing

        vals = {
            "module": relation_name,
            "name": ref,
            "model": self._name,
            "res_id": self.id,
        }
        if sync_date:
            vals["date_update"] = sync_date
        return self.env["ir.model.data"].create(vals)

    def search_links(self, relation_name, refs=None):
        domain = [
            ("module", "=", relation_name),
            ("model", "=", self._name),
        ]
        if refs:
            domain.append(("name", "in", [str(r) for r in refs]))
        if self.ids:
            domain.append(("res_id", "in", self.ids))

        return self.env["ir.model.data"].search(domain)
