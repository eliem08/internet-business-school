"""Billing shape: monthly checkout carries the advertised 14-day trial, and /pricing says so."""

import pathlib
import tempfile
import threading
import unittest
import urllib.request

from internet_business_school import web

ENV = {
    "STRIPE_SECRET_KEY": "sk_test_x",
    "STRIPE_WEBHOOK_SECRET": "whsec_test",
    "STRIPE_PRICES": "student=price_1",
    "PUBLIC_URL": "https://example.test",
}


class BillingShapeTests(unittest.TestCase):
    def test_monthly_checkout_carries_14_day_trial(self):
        with tempfile.TemporaryDirectory() as t:
            gate = web.Gate(pathlib.Path(t))
            billing = web.Billing(pathlib.Path(t), gate, env=ENV)
            sent = {}
            billing._stripe = lambda path, form: sent.update(form) or {"url": "https://checkout.test/s"}
            self.assertEqual(billing.checkout("student"), "https://checkout.test/s")
            self.assertEqual(sent["mode"], "subscription")
            self.assertEqual(sent["line_items[0][price]"], "price_1")
            self.assertEqual(sent["subscription_data[trial_period_days]"], "14")

    def test_pricing_page_notes_trial_when_billing_enabled(self):
        with tempfile.TemporaryDirectory() as t:
            srv = web.make_server("127.0.0.1", 0, pathlib.Path(t), env=ENV)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                body = (
                    urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}/pricing", timeout=30)
                    .read()
                    .decode()
                )
            finally:
                srv.shutdown()
                srv.server_close()
            self.assertIn("14-day free trial", body)


if __name__ == "__main__":
    unittest.main()
