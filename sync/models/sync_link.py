# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

ODOO = "__odoo__"
EXTERNAL = "__external__"


class SyncLink(models.Model):

    _name = "sync.link"
    _description = "Resource Links"

    relation = fields.Char("Relation Name", required=True)
    system1 = fields.Char("System 1", required=True)
    system2 = fields.Char("System 2", required=True)
    ref1 = fields.Char("System 1 Ref", required=True)
    ref2 = fields.Char("System 2 Ref", required=True)
    date = fields.Datetime(
        string="Sync Date", default=fields.Datetime.now, required=True
    )
    model = fields.Char("Odoo Model")

    @api.model_cr_context
    def _auto_init(self):
        res = super(SyncLink, self)._auto_init()
        tools.create_unique_index(
            self._cr,
            "sync_link_refs_uniq_index",
            self._table,
            ["relation", "system1", "system2", "ref1", "ref2"],
        )
        return res

    # External links
    @api.model
    def refs2vals(self, external_refs):
        external_refs = sorted(
            external_refs.items(), key=lambda code_value: code_value[0]
        )
        system1, ref1 = external_refs[0]
        system2, ref2 = external_refs[1]
        vals = {
            "system1": system1,
            "system2": system2,
            "ref1": ref1,
            "ref2": ref2,
        }
        for k in ["ref1", "ref2"]:
            if vals[k] is None:
                continue
            if isinstance(vals[k], list):
                vals[k] = [str(i) for i in vals[k]]
            else:
                vals[k] = str(vals[k])
        return vals

    @api.model
    def _set_link_external(
        self, relation, external_refs, sync_date=None, allow_many2many=False
    ):
        vals = self.refs2vals(external_refs)
        # Check for existing records
        if allow_many2many:
            existing = self._search_links_external(relation, external_refs)
        else:
            # check existing links for a part of external_refs
            refs1 = external_refs.copy()
            refs2 = external_refs.copy()
            for i, k in enumerate(external_refs.keys()):
                if i:
                    refs1[k] = None
                else:
                    refs2[k] = None

            existing = self._search_links_external(
                relation, refs1
            ) or self._search_links_external(relation, refs2)

            if existing and not (
                existing.ref1 == vals["ref1"] and existing.ref2 == vals["ref2"]
            ):
                raise ValidationError(
                    "%s link already exists: %s=%s, %s=%s"
                    % (
                        relation,
                        existing.system1,
                        existing.ref1,
                        existing.system1,
                        existing.ref2,
                    )
                )

        if existing:
            existing.update_links(sync_date)
            return existing

        if sync_date:
            vals["date"] = sync_date
        vals["relation"] = relation
        print("create", vals)
        return self.create(vals)

    @api.model
    def _get_link_external(self, relation, external_refs):
        links = self._search_links_external(relation, external_refs)
        if len(links) > 1:
            raise ValidationError(
                "get_link found multiple links. Use search_links for many2many relations"
            )
        return links

    @api.model
    def _search_links_external(self, relation, external_refs):
        vals = self.refs2vals(external_refs)
        domain = [("relation", "=", relation)]
        for k, v in vals.items():
            if not v:
                continue
            operator = "in" if isinstance(v, list) else "="
            domain.append((k, operator, v))
        print("search", domain)
        return self.search(domain)

    def get(self, system):
        res = []
        for r in self:
            if r.system1 == system:
                res.append(r.ref1)
            elif r.system2 == system:
                res.append(r.ref2)
            else:
                raise ValueError(
                    "Cannot find value for %s. Found: %s and %s"
                    % (system, r.system1, r.system2)
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

    def _set_link_odoo(
        self, record, relation, ref, sync_date=None, allow_many2many=False
    ):
        # TODO: call _set_link_external
        self.ensure_one()

        # check existing links for the record
        existing = self._search_links(record, relation)
        if not existing:
            # check existing links for the reference
            existing = self._get_link_odoo(relation, ref)

        if existing.external == ref and existing.odoo == self:
            existing.update_links(sync_date)
            return existing

        if existing and not allow_many2many:
            raise ValidationError(
                "%s link already exists: record={}, ref={}".format(
                    relation, existing.odoo, existing.external
                )
            )

        vals = {
            "module": relation,
            "name": ref,
            "model": record._name,
            "res_id": record.id,
        }
        if sync_date:
            vals["date"] = sync_date
        return self.env["ir.model.data"].create(vals)

    def _get_link_odoo(self, relation, ref):
        # TODO: call _get_link_external
        return self.search([("module", "=", rel), ("name", "=", str(ref))])

    def _search_links_odoo(self, records, relation, refs=None):
        # TODO: call _search_link_external
        domain = [
            ("module", "=", relation),
            ("model", "=", records._name),
        ]
        if refs:
            domain.append(("name", "in", [str(r) for r in refs]))
        if self.ids:
            domain.append(("res_id", "in", records.ids))

        return self.search(domain)

    # Common API
    @property
    def sync_date(self):
        return min(r.date for r in self)

    def update_links(self, sync_date=None):
        if not sync_date:
            sync_date = fields.Datetime.now()
        self.write({"date": sync_date})
        return self

    def __xor__(self, other):
        return (self | other) - (self & other)
