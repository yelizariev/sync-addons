# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestTriggerDB(TransactionCase):
    def setUp(self):
        funcs = self.env["ir.actions.server"]._get_links_functions()
        self.get_link = funcs["get_link"]
        super(TestTriggerDB, self).setUp()

    def test_trigger_db(self):
        """Test handle_db created in sync_demo.xml"""

        # activate project
        self.env.ref("sync.test_project").active = True
        # trigger event
        partner = self.env["res.partner"].create({"name": name})
        # check that handler is executed
        param = self.env.ref("sync.test_project_param")
        link = self.get_link(param.value, partner.id)
        self.assertTrue(link)