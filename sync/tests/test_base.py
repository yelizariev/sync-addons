# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import uuid


class TestBase(TransactionCase):

    def create_record(self):
        self.env["res.partner"].create({"name": "Test"})

    def test_make_ref(self):
        # Simplest scenario
        r = self.create_record()
        ref = r.make_ref()
        r_by_ref = self.env.ref(ref)
        self.assertEqual(r.id, r_by_ref.id)

        # Second call
        ref_response = r.make_ref()
        self.assertEqual(ref, ref_response)

        # Custom ref
        r = self.create_record()
        ref = str(uuid.uuid4())
        ref_response = r.make_ref(ref)
        self.assertEqual(ref, ref_response)
        r_by_ref = self.env.ref(ref)
        self.assertEqual(r, r_by_ref)

        # Second call with custom ref
        ref_response = r.make_ref(ref)
        self.assertEqual(ref, ref_response)

        # Multiple records
        r = self.create_record()
        r2 = self.create_record()
        self.assetNotEqual(r.make_ref(), r2.make_ref())

        # Call on existing ref
        ref = "sync.module_category_sync"
        r = self.env.ref(ref)
        ref_response = r.make_ref(ref)
        self.assertEqual(ref, ref_response)

        # Multiple refs
        ref2 = str(uuid.uuid4())
        with self.assertRaises(ValidationError):
            ref_response = r.make_ref(ref2)
        ref_response = r.make_ref(ref2, raise_if_exists=False)
        self.assertEqual(ref2, ref_response)
        r_by_ref = self.env.ref(ref2)
        self.assertEqual(r, r_by_ref)
