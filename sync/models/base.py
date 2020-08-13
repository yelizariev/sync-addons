# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def set_link(self, relation_name, ref, sync_date=None):
        TODO
        return link

    def search_links(self, relation_name):
        TODO
        return link
