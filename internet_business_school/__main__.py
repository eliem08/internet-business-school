import argparse
import csv
import os
import sys

from .core import School, Student


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
    return ap


def _run(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.cmd == "demo":
        demo()
        return 0
    school = School()
    for k in school.order:
        l = school.lessons[k]
        extra = f" | case: {l.case}" if l.case else ""
        extra += f" | proof: {l.proof}" if l.proof else ""
        print(f"[{l.module}] {l.title}{'' if l.required else ' (elective)'}{extra}")
    return 0


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
