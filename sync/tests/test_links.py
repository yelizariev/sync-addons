# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import uuid


class TestLink(TransactionCase):
    def setUp(self):
        funcs = self.env["ir.actions.server"]._get_links_functions()
        self.get_link = funcs["get_link"]
        self.set_link = funcs["set_link"]
        self.search_links = funcs["search_links"]
        super(TestLink, self).setUp()

    def create_record(self):
        return self.env["res.partner"].create({"name": "Test"})

    def test_odoo_link(self):
        REL = "sync_test_links_partner"
        REL2 = "sync_test_links_partner2"

        self.assertFalse(self.search_links(REL))

        # Set and get links
        r = self.create_record()
        ref = uuid.uuid4()
        slink = r.set_link(REL, ref)
        glink = self.get_link(REL, ref)
        self.assertEqual(r, glink.odoo)
        self.assertEqual(ref, glink.external)
        glink = r.get_link(REL)
        self.assertEqual(r, glink.odoo)
        self.assertEqual(ref, glink.external)

        # check search_links
        all_links = self.search_links(REL)
        self.assertEqual(1, len(all_links))
        self.assertEqual(r, all_links[0].odoo)

        # update sync_date
        now = datetime.now() - relativedelta(days=1)
        all_links.update(now)
        glink = self.get_link(REL, ref)
        self.assertEqual(glink.sync_date, now)

        # update sync_date
        now = datetime.now()
        glink.update(now)
        glink = self.get_link(REL, ref)
        self.assertEqual(glink.sync_date, now)

        # check search_links
        all_links = self.search_links(REL)
        self.assertTrue(all_links)
        self.assertEqual(1, len(all_links))
        self.assertEqual(r, all_links[0].odoo)

        # Error: get_link with multiple results
        r = self.create_record()
        ref1 = uuid.uuid4()
        ref2 = uuid.uuid4()
        r.set_link(REL, ref1)
        r.set_link(REL, ref2)
        with self.assertRaises(Exception):
            r.get_link(REL)

        # multiple links for different relation_name
        r = self.create_record()
        ref1 = uuid.uuid4()
        r.set_link(REL, ref1)
        ref2 = uuid.uuid4()
        r.set_link(REL2, ref2)
        self.assertFalse(get_link(REL2, ref1))

        # check links
        all_links = self.search_links(REL)
        self.assertNotEqual(1, len(all_links))
        self.assertNotEqual(1, len(all_links.odoo))
        self.assertIsInstance(all_links.odoo.ids, list)
        self.assertIsInstance(all_links.external, list)
        self.assertIsInstance(all_links.sync_date, datetime)
        for link in all_links:
            self.assertIsInstance(link.odoo.id, int)

        # unlink
        all_links.unlink()
        all_links = self.search_links(REL)
        self.assertFalse(all_links)

    def test_external_link(self):
        REL = "sync_test_external_links"
        all_links = self.search_links(REL, [("github", None), ("trello", None)])
        self.assertFalse(self.search_links(REL))

        # set get links
        now = datetime.now() - relativedelta(days=1)
        slink = self.set_link(REL, [("github", 1), ("trello", 101)], sync_date=now)
        glink = self.get_link(REL, [("github", 1), ("trello", 101)])
        self.assertEqual(slink.get("github"), glink.get("github"))
        glink = self.get_link(REL, [("github", 1), ("trello", None)])
        self.assertEqual(slink.get("github"), glink.get("github"))
        glink = self.get_link(REL, [("github", None), ("trello", 101)])
        self.assertEqual(slink.get("github"), glink.get("github"))

        # update sync_date
        now = datetime.now()
        glink.update(now)
        glink = self.get_link(REL, ref)
        self.assertEqual(glink.sync_date, now)

        # search_links
        all_links = self.search_links(REL, [("github", None), ("trello", None)])
        self.assertEqual(1, len(all_links))
        self.assertEqual(now, all_links.sync_date)
        for link in all_links:
            self.assertEqual(now, link.sync_date)
        all_links.update(now)

        # sets operations
        self.set_link(REL, [("github", 2), ("trello", 102)])
        self.set_link(REL, [("github", 3), ("trello", 103)])
        self.set_link(REL, [("github", 4), ("trello", 104)])
        a = self.search_links(REL, [("github", [1,2,3]), ("trello", None)])
        b = self.search_links(REL, [("github", None), ("trello", [102, 103, 104])])
        self.assertNotEqual(a, b)
        self.assertEqual(set((a-b).get("trello")), set([102,103]))
        self.assertEqual(set((a-b).get("github")), set([2,3]))
        self.assertEqual(set((a|b).get("github")), set([1,2,3,4]))
        self.assertEqual(set((a&b).get("github")), set([2,3]))
        self.assertEqual(set((a^b).get("github")), set([1,4]))

        # one2many
        self.set_link(REL, [("github", 5), ("trello", 105)])
        self.set_link(REL, [("github", 5), ("trello", 1005)])
        with self.assertRaises(Exception):
            glink = self.get_link(REL, [("github", 5), ("trello", None)])
        glink1 = self.get_link(REL, [("github", 5), ("trello", 105)])
        glink2 = self.get_link(REL, [("github", 5), ("trello", 1005)])
        glink3 = self.get_link(REL, [("github", None), ("trello", 1005)])
        glink4 = self.get_link(REL, [("github", None), ("trello", 1005)])
        self.assertEqual(glink1, glink2)
        self.assertEqual(glink1, glink3)
        self.assertEqual(glink1, glink4)
        elinks = self.get_link(REL, [("github", None), ("trello", [105,1005])])
        self.assertEqual(1, len(elinks))

        # unlink
        all_links = self.search_links(REL, [("github", None), ("trello", None)])
        all_links.unlink()
        all_links = self.search_links(REL, [("github", None), ("trello", None)])
        self.assertFalse(all_links)
