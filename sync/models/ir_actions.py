# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    sync_task_id = fields.Many2one("sync.task")

    @api.model
    def _get_links_functions(self):
        env = self.env

        def set_link(rel, external_refs, sync_date=None, allow_many2many=False):
            # TODO use *args, **kwargs
            # Works for external links only
            return env["sync.link"]._set_link_external(
                rel, external_refs, sync_date, allow_many2many
            )

        def search_links(rel, external_refs):
            # TODO use *args, **kwargs
            # Works for external links only
            return env["sync.link"]._search_links_external(rel, external_refs)

        def get_link(rel, ref_info):
            # TODO: move code to sync.link model
            # return  env["sync.link"]._get_link(*args)
            if isinstance(ref_info, dict):
                # External link
                external_refs = ref_info
                return env["sync.link"]._get_link_external(rel, external_refs)
            else:
                # Odoo link
                ref = ref_info
                return env["sync.link"]._get_link_odoo(rel, ref)

        return {
            "set_link": set_link,
            "search_links": search_links,
            "get_link": get_link,
        }


class Link:
    def __len__(self):
        # Is used for ``elinks.length`` and for ``bool(elinks)``
        TODO
