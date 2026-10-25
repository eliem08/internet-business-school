"""Curriculum DAG, rubric grading, proof-of-work assignments and graduation."""

from __future__ import annotations

import hashlib
import hmac
import math
import os
import secrets
from dataclasses import dataclass, field

__all__ = ["Lesson", "Rubric", "CURRICULUM", "RUBRICS", "Student", "School", "topo_order"]


@dataclass(frozen=True)
class Lesson:
    key: str
    module: str
    title: str
    prereqs: tuple = ()
    case: str = ""
    rubric: str | None = None
    proof: dict | None = None  # metric -> minimum
    required: bool = True


@dataclass(frozen=True)
class Rubric:
    key: str
    criteria: dict  # name -> weight


CURRICULUM = [
    Lesson(
        "niche",
        "Foundations",
        "Finding a niche with demand",
        case="How a $9/mo Notion template business hit $40k MRR",
        rubric="analysis",
    ),
    Lesson("landing", "Foundations", "Ship a landing page in a day", ("niche",), proof={"visitors": 100}),
    Lesson(
        "seo",
        "Distribution",
        "SEO that compounds",
        ("landing",),
        case="Programmatic SEO: 0 to 1M visits",
        rubric="analysis",
    ),
    Lesson("social", "Distribution", "Building in public on X", ("landing",), proof={"followers_gained": 50}),
    Lesson("paid", "Distribution", "Paid ads without burning cash", ("landing",), rubric="analysis", required=False),
    Lesson("pricing", "Monetisation", "Pricing a SaaS", ("niche",), case="Why 3 tiers beat 1", rubric="analysis"),
    Lesson("checkout", "Monetisation", "Stripe, trials and dunning", ("pricing", "landing"), proof={"signups": 10}),
    Lesson("agents", "Operations", "Running the company with agents", ("checkout",), rubric="ops"),
    Lesson(
        "capstone",
        "Capstone",
        "First dollar",
        ("seo", "social", "checkout", "agents"),
        proof={"revenue_usd": 1},
        rubric="ops",
    ),
]
RUBRICS = {
    "analysis": Rubric("analysis", {"insight": 0.4, "evidence": 0.35, "clarity": 0.25}),
    "ops": Rubric("ops", {"automation": 0.4, "reliability": 0.3, "cost_awareness": 0.3}),
}


def topo_order(lessons: list[Lesson]) -> list[str]:
    by_key = {l.key: l for l in lessons}
    order, state = [], {}

    def visit(k):
        if state.get(k) == 1:
            raise ValueError(f"prerequisite cycle at {k}")
        if state.get(k) == 2:
            return
        state[k] = 1
        for p in by_key[k].prereqs:
            if p not in by_key:
                raise ValueError(f"{k} depends on unknown lesson {p}")
            visit(p)
        state[k] = 2
        order.append(k)

    for l in lessons:
        visit(l.key)
    return order


@dataclass
class Student:
    name: str
    grades: dict = field(default_factory=dict)  # lesson -> 0..4
    completed: set = field(default_factory=set)


class School:
    def __init__(self, lessons: list[Lesson] | None = None, rubrics: dict | None = None, key: bytes | None = None):
        # certificates are HMAC-signed so only the school can mint one; never a guessable default key
        self.key = key or (os.environ.get("IBS_CERT_KEY") or secrets.token_hex(32)).encode()
        self.lessons = {l.key: l for l in (lessons or CURRICULUM)}
        self.order = topo_order(list(self.lessons.values()))
        self.rubrics = rubrics or RUBRICS

    def unlocked(self, s: Student) -> list[str]:
        return [
            k for k in self.order if k not in s.completed and all(p in s.completed for p in self.lessons[k].prereqs)
        ]

    def next_lesson(self, s: Student) -> str | None:
        options = self.unlocked(s)
        required = [k for k in options if self.lessons[k].required]
        return (required or options or [None])[0]

    def grade(self, rubric_key: str, levels: dict) -> float:
        r = self.rubrics[rubric_key]
        missing = set(r.criteria) - set(levels)
        if missing:
            raise ValueError(f"missing criteria {sorted(missing)}")
        if any(not 0 <= v <= 4 for v in levels.values()):
            raise ValueError("levels must be 0-4")
        return round(sum(w * levels[c] for c, w in r.criteria.items()), 2)

    def submit(self, s: Student, lesson: str, levels: dict | None = None, metrics: dict | None = None) -> dict:
        l = self.lessons[lesson]
        if lesson not in self.unlocked(s):
            raise ValueError(f"{lesson} is locked; finish {[p for p in l.prereqs if p not in s.completed]}")
        result = {"lesson": lesson, "passed": True, "notes": []}
        if l.proof:
            for metric, minimum in l.proof.items():
                got = (metrics or {}).get(metric, 0)
                if not (isinstance(got, (int, float)) and math.isfinite(got)) or got < minimum:  # nan < x is False
                    result["passed"] = False
                    result["notes"].append(f"{metric} {got} < required {minimum}")
        grade = None
        if l.rubric:
            grade = self.grade(l.rubric, levels or {})
            if grade < 2.0:
                result["passed"] = False
                result["notes"].append(f"rubric grade {grade} below 2.0 - revise and resubmit")
        elif result["passed"]:
            grade = 4.0
        result["grade"] = grade
        if result["passed"]:
            s.completed.add(lesson)
            s.grades[lesson] = grade
        return result

    def graduate(self, s: Student) -> dict:
        missing = [k for k, l in self.lessons.items() if l.required and k not in s.completed]
        avg = sum(s.grades.values()) / len(s.grades) if s.grades else 0
        ok = not missing and avg >= 3.0
        out = {"graduated": ok, "average": round(avg, 2), "missing": missing}
        if ok:
            out["certificate_id"] = self._sign(s.name, s.grades)
        return out

    def _sign(self, name: str, grades: dict) -> str:
        payload = f"{name}|{sorted(grades.items())}".encode()
        return hmac.new(self.key, payload, hashlib.sha256).hexdigest()[:20]

    def verify_certificate(self, name: str, grades: dict, certificate_id: str) -> bool:
        """True only for a certificate this school issued for exactly this student and transcript."""
        return hmac.compare_digest(self._sign(name, grades), str(certificate_id))
