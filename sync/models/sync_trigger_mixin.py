# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class SyncTriggerMixin(models.AbstractModel):

    _name = "sync.trigger.mixin"

    trigger_name = fields.Char("Trigger Name", help="Technical name to be used in task code")
