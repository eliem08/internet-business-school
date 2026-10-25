import unittest

from internet_business_school import Lesson, School, Student, topo_order


class Tests(unittest.TestCase):
    def setUp(self):
        self.school = School()
        self.s = Student("s")

    def test_topo_and_cycle(self):
        order = self.school.order
        self.assertLess(order.index("niche"), order.index("landing"))
        self.assertEqual(order[-1], "capstone")
        with self.assertRaises(ValueError):
            topo_order([Lesson("a", "m", "A", ("b",)), Lesson("b", "m", "B", ("a",))])

    def test_locking_and_next(self):
        self.assertEqual(self.school.next_lesson(self.s), "niche")
        with self.assertRaises(ValueError):
            self.school.submit(self.s, "landing", metrics={"visitors": 500})

    def test_rubric_and_proof(self):
        self.assertEqual(self.school.grade("analysis", {"insight": 4, "evidence": 4, "clarity": 0}), 3.0)
        r = self.school.submit(self.s, "niche", {"insight": 1, "evidence": 1, "clarity": 1})
        self.assertFalse(r["passed"])
        self.school.submit(self.s, "niche", {"insight": 4, "evidence": 4, "clarity": 4})
        r = self.school.submit(self.s, "landing", metrics={"visitors": 20})
        self.assertFalse(r["passed"])
        self.assertIn("visitors 20 < required 100", r["notes"])

    def test_graduation(self):
        L = {"insight": 4, "evidence": 3, "clarity": 3}
        O = {"automation": 3, "reliability": 3, "cost_awareness": 3}
        steps = [
            ("niche", L, None),
            ("landing", None, {"visitors": 100}),
            ("pricing", L, None),
            ("seo", L, None),
            ("social", None, {"followers_gained": 50}),
            ("checkout", None, {"signups": 10}),
            ("agents", O, None),
        ]
        for lesson, lv, m in steps:
            self.assertTrue(self.school.submit(self.s, lesson, lv, m)["passed"], lesson)
        self.assertFalse(self.school.graduate(self.s)["graduated"])
        self.school.submit(self.s, "capstone", O, {"revenue_usd": 1})
        g = self.school.graduate(self.s)
        self.assertTrue(g["graduated"])
        self.assertEqual(len(g["certificate_id"]), 20)
        self.assertTrue(self.school.verify_certificate("s", self.s.grades, g["certificate_id"]))
        self.assertFalse(self.school.verify_certificate("s", {**self.s.grades, "capstone": 4.0}, g["certificate_id"]))

    def test_certificates_cannot_be_minted_from_the_public_formula(self):
        import hashlib

        grades = {"capstone": 4.0, "niche": 4.0}
        forged = hashlib.sha256(f"mallory|{sorted(grades.items())}".encode()).hexdigest()[:20]
        self.assertFalse(self.school.verify_certificate("mallory", grades, forged))
        self.assertFalse(School(key=b"other").verify_certificate("s", grades, self.school._sign("s", grades)))

    def test_nan_metrics_do_not_satisfy_proof_of_work(self):
        self.school.submit(self.s, "niche", {"insight": 4, "evidence": 4, "clarity": 4})
        r = self.school.submit(self.s, "landing", metrics={"visitors": float("nan")})
        self.assertFalse(r["passed"])


if __name__ == "__main__":
    unittest.main()
