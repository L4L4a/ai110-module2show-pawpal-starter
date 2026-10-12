# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

**Covered (17 tests in `tests/test_pawpal.py`):** task completion, adding tasks, time/frequency validation, chronological sorting, today's schedule filtering, daily and weekly recurrence (plus one-off, double-complete and stray-task cases), conflict detection (cross-pet, no conflict, completed/other-day tasks ignored), filtering by pet and status, and edge cases (pet with no tasks, empty owner).

**Confidence: 4/5.** The logic layer is well covered. The Streamlit UI is only checked by hand and conflicts only match exact start times.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time`, `get_todays_schedule` | Sorts by `(due_date, "HH:MM")` using a lambda key; zero-padded 24-hour strings sort chronologically. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Either filter, both, or neither; pet name match is case-insensitive. |
| Conflict handling | `Scheduler.detect_conflicts` | Returns warning strings for pending tasks sharing the same date and start time (across pets too). Never raises. |
| Recurring tasks | `Task.mark_complete`, `Scheduler.handle_recurring` | Completing a `daily`/`weekly` task creates the next one at `due_date + timedelta(days=1 / weeks=1)` and attaches it to the same pet. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
