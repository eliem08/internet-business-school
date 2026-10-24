# internet-business-school

> **Harvard Business School for internet businesses** — a real education in building online.

MBA programmes teach you to run a Fortune 500 division. Nobody teaches how
to build a $30k/month internet business: distribution, SEO, pricing a SaaS,
running paid ads without lighting money on fire, building with agents.
This repo is the learning engine behind that school — case-method
curriculum, rubric-graded assignments with real-world proof, and a capstone
that requires actual revenue.

## What the MVP does

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
