import argparse
import csv
import os
import sys

from .core import School, Student
from .registry import Registry, parse_pairs


def demo():
    school = School()
    s = Student("Sam")
    plan = [
        ("niche", {"insight": 4, "evidence": 3, "clarity": 3}, None),
        ("landing", None, {"visitors": 240}),
        ("pricing", {"insight": 3, "evidence": 3, "clarity": 4}, None),
        ("seo", {"insight": 3, "evidence": 2, "clarity": 3}, None),
        ("social", None, {"followers_gained": 80}),
        ("checkout", None, {"signups": 4}),
        ("checkout", None, {"signups": 14}),
        ("agents", {"automation": 4, "reliability": 3, "cost_awareness": 3}, None),
        ("capstone", {"automation": 3, "reliability": 3, "cost_awareness": 4}, {"revenue_usd": 49}),
    ]
    for lesson, levels, metrics in plan:
        r = school.submit(s, lesson, levels, metrics)
        print(f"{lesson:<9} {'PASS' if r['passed'] else 'FAIL'} grade={r['grade']}  {'; '.join(r['notes'])}")
        print(f"          next up: {school.next_lesson(s)}")
    print(school.graduate(s))


def build_parser():
    ap = argparse.ArgumentParser(prog="internet-business-school")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("curriculum")
    sub.add_parser("demo")
    store = os.environ.get("IBS_STORE", "school.json")
    e = sub.add_parser("enroll", help="add a student")
    e.add_argument("name")
    s = sub.add_parser("submit", help="hand in a lesson: rubric levels and/or proof metrics")
    s.add_argument("name")
    s.add_argument("lesson")
    s.add_argument("--level", action="append", default=[], help="rubric criterion=0..4, e.g. insight=3")
    s.add_argument("--metric", action="append", default=[], help="proof metric=value, e.g. visitors=240")
    s.add_argument("--evidence", default="", help="link to the shipped work (page, repo, dashboard)")
    pr = sub.add_parser("progress", help="grades so far and what unlocks next")
    pr.add_argument("name")
    gr = sub.add_parser("graduate", help="issue a signed certificate if every required lesson passed")
    gr.add_argument("name")
    v = sub.add_parser("verify", help="check a certificate id against the student's transcript")
    v.add_argument("name")
    v.add_argument("certificate_id")
    for p in (e, s, pr, gr, v):
        p.add_argument("--store", default=store)
    return ap


def _run(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.cmd == "demo":
        demo()
        return 0
    if a.cmd != "curriculum":
        return _student(a)
    school = School()
    for k in school.order:
        l = school.lessons[k]
        extra = f" | case: {l.case}" if l.case else ""
        extra += f" | proof: {l.proof}" if l.proof else ""
        print(f"[{l.module}] {l.title}{'' if l.required else ' (elective)'}{extra}")
    return 0


def _student(a) -> int:
    reg = Registry(a.store)
    if a.cmd == "enroll":
        new = reg.enroll(a.name)
        reg.save()
        print(f"{'enrolled' if new else 'already enrolled'}: {a.name}; first lesson: {reg.school.order[0]}")
        return 0
    if a.cmd == "submit":
        r = reg.submit(a.name, a.lesson, parse_pairs(a.level, "level"), parse_pairs(a.metric, "metric"), a.evidence)
        reg.save()
        print(f"{a.lesson}: {'PASS' if r['passed'] else 'FAIL'}  grade={r['grade']}")
        for note in r["notes"]:
            print(f"  - {note}")
        print(f"next up: {r['next'] or 'nothing left: run graduate'}")
        return 0 if r["passed"] else 1
    s = reg.student(a.name)
    if a.cmd == "progress":
        for k in reg.school.order:
            lesson = reg.school.lessons[k]
            state = f"{s.grades[k]:.2f}" if k in s.completed else ("open" if k in reg.school.unlocked(s) else "locked")
            print(f"  {state:>6}  {lesson.title}{'' if lesson.required else ' (elective)'}")
        print(f"next up: {reg.school.next_lesson(s) or 'nothing left: run graduate'}")
        return 0
    if a.cmd == "graduate":
        g = reg.school.graduate(s)
        if g["graduated"]:
            print(f"GRADUATED {s.name}  average {g['average']}  certificate {g['certificate_id']}")
            return 0
        print(f"not yet: average {g['average']} (need 3.0); missing {g['missing']}")
        return 1
    ok = reg.school.verify_certificate(s.name, s.grades, a.certificate_id)
    print(f"{'VALID' if ok else 'INVALID'} certificate for {s.name}")
    return 0 if ok else 1


def main(argv=None):
    """Run the CLI; a bad input file or argument exits 2 with a one-line error instead of a traceback.

    Set AGENT_ECONOMY_DEBUG=1 to see the full traceback.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        return _run(argv)
    except (OSError, ValueError, KeyError, csv.Error) as e:
        if os.environ.get("AGENT_ECONOMY_DEBUG"):
            raise
        msg = e.args[0] if isinstance(e, KeyError) and e.args else e
        print(f"error: {msg}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
