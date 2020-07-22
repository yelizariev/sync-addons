# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import json
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)

class TestTriggerDB(TransactionCase):

    def test_trigger_db(self):
        """Test handle_db created in sync_demo.xml"""

        # activate project
        self.env.ref("sync.test_project").active = True
        # trigger event
        partner = self.env["res.partner"].create({"name": name})
        # check that handler is executed
        ref = partner.make_ref()
        self.assertEqual(ref, "sync.partner_%s" % partner.id)
