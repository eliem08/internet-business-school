# Architecture — internet-business-school

## 1. Scope
The learning engine for a school that teaches building internet businesses with real-world proof of work.
**MVP:** curriculum DAG with cycle detection, unlock logic and next-best lesson, weighted rubrics
(0–4), proof-of-work metric thresholds, graduation rule, certificate hash.
**Product:** cohorts and live case sessions, peer grading with calibration, verified metrics via
OAuth, alumni deal flow.

## 2. Domain model
```mermaid
classDiagram
  Lesson : key, module, prereqs[], case, rubric?, proof{metric:min}?, required
  Rubric : criteria{name: weight}
  Student : grades{lesson: 0..4}, completed{}
  School : unlocked(s), next_lesson(s), submit(s, lesson, levels, metrics), graduate(s)
  School --> Lesson
  Lesson --> Rubric
```

## 3. Rules
- A lesson unlocks when all of its prerequisites are complete. The topological order is computed
  once, and DFS with colouring detects cycles and unknown prerequisites at load time.
- Submit: proof metrics must meet their minimums, and the rubric grade must be ≥ 2.0. A lesson with
  only proof-of-work earns 4.0 when it passes.
- Graduation: all required lessons complete and an average grade ≥ 3.0. The capstone requires
  real revenue (≥ $1).
- Certificate ID = SHA-256 over the student and their sorted grades, so it can be verified offline.

## 4. Design decisions
- **Proof-of-work as a first-class assignment type.** It's the school's differentiation: you
  graduate by shipping, not by writing essays.
- **Electives don't block graduation**, and `next_lesson` prefers required lessons.
- **The curriculum is validated at load** (fail fast on bad prerequisites), not at submit time.

## 5. Future production architecture (not shipped)
The following is the production direction, not this release: an LMS service (Postgres: cohorts,
lessons, submissions, grades with grader IDs). A metric verifier pulls Stripe, Plausible and
Search Console via OAuth, with student consent. Peer grading assigns 3 graders and uses
calibration essays to weight grader reliability. Certificates are public verification pages.
This release validates and grades locally only; it runs no cohorts, no peer grading, and no
verified-metric OAuth.

## 6. Risks
Metric fraud (verified sources only for proof-of-work). Grade inflation (calibrated peer grading
and instructor spot-checks).
