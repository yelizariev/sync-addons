# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import http

from odoo.addons.website.controllers.main import Website


class Webhook(http.Controller):
    @http.route(
        [
            "/website/action-json/<path_or_xml_id_or_id>",
            "/website/action-json/<path_or_xml_id_or_id>/<path:path>",
        ],
        type="json",
        auth="public",
        website=True,
    )
    def actions_server(self, path_or_xml_id_or_id, **post):
        return Website().actions_server(path_or_xml_id_or_id, **post)
