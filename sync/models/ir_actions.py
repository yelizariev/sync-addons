# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    sync_task_id = fields.Many2one("sync.task")

    @api.model
    def _get_links_functions(self):
        env = self.env

        def set_link(rel, external_refs, sync_date=None):
            # Works for external links only
            return env["sync.external.link"]._set_link_external(
                rel, external_refs, sync_date
            )

        def search_links(rel, external_refs):
            # Works for external links only
            return env["sync.external.link"]._search_links_external(rel, external_refs)

        def get_link(rel, ref_info):
            if isinstance(ref_info, list):
                # External link
                external_refs = ref_info
                return env["sync.external.link"]._get_link_external(rel, external_refs)
            else:
                # Odoo link
                ref = ref_info
                return env["ir.model.data"].search(
                    [("module", "=", rel), ("name", "=", str(ref))]
                )

        return {
            "set_link": set_link,
            "search_links": search_links,
            "get_link": get_link,
        }


class Link:
    def __len__(self):
        # Is used for ``elinks.length`` and for ``bool(elinks)``
        TODO
