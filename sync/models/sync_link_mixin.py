# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncLinkMixin(models.AbstractModel):
    _name = "sync.link.mixin"
    _description = "Links"

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
