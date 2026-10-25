<!-- sell-kit:start -->
# Internet Business School

[![CI](https://github.com/eliem08/internet-business-school/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/internet-business-school/actions/workflows/ci.yml)

> **A real education in building an online business, graded on what you ship.**

**Who it's for:** Aspiring founders, and the creators and cohorts who teach them.

**The problem:** Online business courses reward watching videos, not shipping, so students finish with certificates and no business.

**What you get:** A prerequisite-ordered curriculum, rubric grading, proof-of-work assignments with real metrics, and signed graduation certificates.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install internet_business_school-0.1.0-py3-none-any.whl
internet-business-school curriculum
internet-business-school demo
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
internet-business-school-web --port 8000          # then open http://127.0.0.1:8000
internet-business-school-web keys create --label "first customer"   # prints an API key (stored hashed)
docker build -t internet-business-school . && docker run -p 8000:8000 -e API_KEYS=sk_... -v internet-business-school-data:/data internet-business-school
```

Every API call needs `Authorization: Bearer <key>` once any key exists; a server on a public address refuses to start without one. Calls are rate-limited per key (60/min, `--rate`) and metered: `internet-business-school-web usage` prints calls per key for billing.

Endpoints: `POST /api/curriculum`, `POST /api/demo`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Student** | $29 per month | Full curriculum; Graded assignments; Signed certificate |
| **Cohort host** | $299 per month | Run your own cohort; Custom lessons and rubrics; Student dashboard |
| **Academy** | $999 per month | White label; Unlimited students; Priority support |

To start a trial or buy a plan, [request access](https://github.com/eliem08/internet-business-school/issues/new?title=Internet%20Business%20School%20trial&labels=sales).

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

- **Curriculum graph**: modules → lessons with prerequisites (DAG, cycle-checked)
  covering foundations, distribution, product, monetisation, operations with agents
- **Case studies** attached to lessons (case method, HBS-style)
- **Assignments** graded with weighted **rubrics** (criteria × levels 0–4)
- **Proof-of-work** assignments: you submit metrics (visitors, signups, revenue)
  and they must cross thresholds — "launch a landing page with 100 visitors"
- **Progress & next-best lesson**: topological ordering respecting prerequisites
- **Graduation**: all required lessons + average grade ≥ 3.0 + capstone
  (first $1 of revenue) → certificate with verification hash

## Quickstart

```bash
pip install -e .
internet-business-school curriculum
internet-business-school demo
```

## Roadmap

- Cohorts, live case discussions, peer grading with calibration
- Verified metrics via Stripe / Plausible / Search Console OAuth
- Alumni deal flow (pairs with solo-combinator)

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
internet_business_school/core.py       domain logic (pure, importable, fully tested)
internet_business_school/__main__.py   CLI (`internet-business-school ...` / `python -m internet_business_school ...`)
tests/                unit tests + generated CLI smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #26).
