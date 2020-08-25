# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

ODOO = "__odoo__"
ODOO_REF = "ref2"
EXTERNAL = "__external__"
EXTERNAL_REF = "ref1"


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
        self, relation, external_refs, sync_date=None, allow_many2many=False, model=None
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
                    _("%s link already exists: %s=%s, %s=%s")
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
        if model:
            vals["model"] = model
        return self.create(vals)

    @api.model
    def _get_link_external(self, relation, external_refs):
        links = self._search_links_external(relation, external_refs)
        if len(links) > 1:
            raise ValidationError(
                _(
                    "get_link found multiple links. Use search_links for many2many relations"
                )
            )
        return links

    @api.model
    def _search_links_external(self, relation, external_refs, model=None):
        vals = self.refs2vals(external_refs)
        domain = [("relation", "=", relation)]
        if model:
            domain.append(("model", "=", model))
        for k, v in vals.items():
            if not v:
                continue
            operator = "in" if isinstance(v, list) else "="
            domain.append((k, operator, v))
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
                    _("Cannot find value for %s. Found: %s and %s")
                    % (system, r.system1, r.system2)
                )
        return res

    # Odoo links
    @property
    def odoo(self):
        res = None
        for r in self:
            record = self.env[r.model].browse(int(getattr(r, ODOO_REF)))
            if res:
                res |= record
            else:
                res = record
        return res

    @property
    def external(self):
        res = [getattr(r, EXTERNAL_REF) for r in self]
        if len(res) == 1:
            return res[0]
        return res

    def _set_link_odoo(
        self, record, relation, ref, sync_date=None, allow_many2many=False
    ):
        refs = {ODOO: record.id, EXTERNAL: ref}
        self._set_link_external(
            relation, refs, sync_date, allow_many2many, record._name
        )

    def _get_link_odoo(self, relation, ref):
        refs = {ODOO: None, EXTERNAL: ref}
        return self._get_link_external(relation, refs)

    def _search_links_odoo(self, records, relation, refs=None):
        refs = {ODOO: records.ids, EXTERNAL: refs}
        return self._search_links_external(relation, refs, model=records._name)

    # Common API
    def _get_link(self, rel, ref_info):
        if isinstance(ref_info, dict):
            # External link
            external_refs = ref_info
            return self._get_link_external(rel, external_refs)
        else:
            # Odoo link
            ref = ref_info
            return self._get_link_odoo(rel, ref)

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