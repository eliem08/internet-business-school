import contextlib
import io
import json
import os
import tempfile
import unittest

from internet_business_school.__main__ import main
from internet_business_school.registry import Registry, parse_pairs

ANALYSIS = ["--level", "insight=4", "--level", "evidence=3", "--level", "clarity=3"]
OPS = ["--level", "automation=4", "--level", "reliability=3", "--level", "cost_awareness=3"]
LOW = ["--level", "insight=1", "--level", "evidence=1", "--level", "clarity=1"]
JOURNEY = [
    ["niche", *ANALYSIS],
    ["landing", "--metric", "visitors=240", "--evidence", "https://example.com"],
    ["pricing", *ANALYSIS],
    ["seo", *ANALYSIS],
    ["social", "--metric", "followers_gained=80"],
    ["checkout", "--metric", "signups=14"],
    ["agents", *OPS],
    ["capstone", *OPS, "--metric", "revenue_usd=49"],
]


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class RegistryTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("IBS_CERT_KEY", None)
        self.tmp = tempfile.TemporaryDirectory()
        self.store = os.path.join(self.tmp.name, "school.json")

    def tearDown(self):
        self.tmp.cleanup()

    def graduate_sam(self) -> str:
        run("enroll", "Sam", "--store", self.store)
        for step in JOURNEY:
            code, out = run("submit", "Sam", *step, "--store", self.store)
            self.assertEqual(code, 0, out)
        code, out = run("graduate", "Sam", "--store", self.store)
        self.assertEqual(code, 0, out)
        return out.split("certificate ")[1].strip()

    def test_full_journey_certificate_survives_a_restart(self):
        cert = self.graduate_sam()
        # every CLI call is a fresh Registry reading the same key file, so the certificate still verifies
        self.assertEqual(run("verify", "Sam", cert, "--store", self.store), (0, "VALID certificate for Sam\n"))
        self.assertEqual(run("verify", "Sam", "0" * 20, "--store", self.store)[0], 1)
        self.assertEqual(Registry(self.store).doc["students"]["Sam"]["evidence"]["landing"], "https://example.com")

    def test_tampered_transcript_invalidates_the_certificate(self):
        cert = self.graduate_sam()
        with open(self.store, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["students"]["Sam"]["grades"]["niche"] = 4.0
        with open(self.store, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        self.assertEqual(run("verify", "Sam", cert, "--store", self.store)[0], 1)

    def test_locked_lessons_failed_grades_and_unknown_students(self):
        run("enroll", "Ana", "--store", self.store)
        self.assertEqual(run("submit", "Ana", "capstone", *OPS, "--store", self.store)[0], 2)  # locked
        self.assertEqual(run("submit", "Ana", "niche", "--level", "insight=1", "--store", self.store)[0], 2)
        code, out = run("submit", "Ana", "niche", *LOW, "--store", self.store)
        self.assertEqual(code, 1, out)  # graded, but below the bar
        self.assertEqual(run("progress", "Nobody", "--store", self.store)[0], 2)

    def test_pairs(self):
        self.assertEqual(parse_pairs(["a=1", "b = 2.5"], "x"), {"a": 1.0, "b": 2.5})
        for bad in (["a"], ["=1"], ["a=x"]):
            with self.assertRaises(ValueError):
                parse_pairs(bad, "x")


if __name__ == "__main__":
    unittest.main()
