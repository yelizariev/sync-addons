# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models, tools


class SyncLink(models.Model):

    _name = "sync.link"
    _description = "External Link"

    relation_name = fields.Char("Relation Name")
    external1 = fields.Char("System 1")
    external2 = fields.Char("System 2")
    external1_ref = fields.Char("System 1 Ref")
    external2_ref = fields.Char("System 2 Ref")
    date_update = fields.Datetime(string="Update Date", default=fields.Datetime.now)

    @api.model_cr_context
    def _auto_init(self):
        res = super(SyncExternalLink, self)._auto_init()
        tools.create_unique_index(
            self._cr,
            "sync_external_link_refs_uniq_index",
            self._table,
            [
                "relation_name",
                "external1",
                "external2",
                "external1_ref",
                "external2_ref",
            ],
        )
        return res

    # External links
    @api.model
    def refs2vals(self, external_refs):
        external_refs = sorted(external_refs, key=lambda code_value: code_value[0])
        external1, external1_ref = external_refs[0]
        external2, external2_ref = external_refs[1]
        return {
            "external1": external1,
            "external2": external2,
            "external1_ref": external1_ref,
            "external2_ref": external2_ref,
        }

    @api.model
    def _set_link_external(self, rel, external_refs, sync_date=None):
        vals = self.refs2vals(external_refs)
        if sync_date:
            vals["date_update"] = sync_date
        vals["relation_name"] = rel
        return self.create(vals)

    @api.model
    def _get_link_external(self, rel, external_refs):
        return self._search_links_external(rel, external_refs)

    @api.model
    def _search_links_external(self, rel, external_refs):
        vals = self.refs2vals(external_refs)
        domain = [("relation_name", "=", rel)]
        for k, v in vals.items():
            if not v:
                continue
            operator = "in" if isinstance(v, list) else "="
            domain.append((k, operator, v))
        return self.search(domain)

    def get(self, system):
        res = []
        for r in self:
            if r.external1 == system:
                res.append(r.external1_ref)
            elif r.external2 == system:
                res.append(r.external2_ref)
            else:
                raise ValueError(
                    "Cannot find value for %s. Found: %s and %s"
                    % (system, r.external1, r.external2)
                )
        return res

    # Odoo links
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

    def _get_link_odoo(self, rel, ref):
        return self.search([("module", "=", rel), ("name", "=", str(ref))])

    # Common API
    @property
    def sync_date(self):
        return min(r.date_update for r in self)

    def update_links(self, sync_date=None):
        if not sync_date:
            sync_date = fields.Datetime.now()
        self.write({"date_update": sync_date})
        return self

    def __xor__(self, other):
        return (self | other) - (self & other)

