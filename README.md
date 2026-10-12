# PawPal+ 🐾

PawPal+ is a pet care scheduler for busy owners. A Python OOP backend (`pawpal_system.py`) models owners, pets and care tasks, and a Streamlit app (`app.py`) lets you manage them and see a sorted, conflict-checked daily plan.

## Features

- **Owner / Pet / Task model** built with dataclasses; one owner can have many pets and each pet many tasks.
- **Sorted daily schedule**: tasks ordered chronologically by `HH:MM`.
- **Filtering** by pet name and/or completion status.
- **Conflict warnings** when two pending tasks share the same date and start time, including across different pets.
- **Recurring tasks**: completing a `daily` or `weekly` task automatically schedules the next occurrence.
- **Input validation**: bad times (`25:00`) and unknown frequencies raise `ValueError`; the UI rejects empty or duplicate names.
- **Persistent UI state**: the Owner lives in `st.session_state`, so data survives Streamlit reruns.

## Project layout

| Path | Purpose |
|------|---------|
| `pawpal_system.py` | Logic layer: `Task`, `Pet`, `Owner`, `Scheduler` |
| `main.py` | CLI demo of the logic layer |
| `app.py` | Streamlit UI |
| `tests/test_pawpal.py` | pytest suite |
| `diagrams/uml_draft.mmd`, `diagrams/uml_final.mmd` | Mermaid UML before and after implementation (`uml.mmd` mirrors the final) |
| `reflection.md` | Design and AI-collaboration reflection |

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py   # web app
python main.py         # CLI demo
```

Requires Python 3.9+.

## 🖥️ Sample Output

`python main.py`:

```
Today's Schedule
========================================
[ ] 07:30  Biscuit  Morning walk (daily)
[ ] 08:00  Biscuit  Vet call (once)
[ ] 08:00  Mochi    Feeding (daily)
[ ] 12:15  Mochi    Flea medication (weekly)
[ ] 18:00  Biscuit  Evening walk (daily)

Conflicts
 ! Conflict on 2026-10-11 at 08:00: Biscuit: Vet call, Mochi: Feeding

Completing 'Morning walk' (daily)...
  next occurrence: Morning walk on 2026-10-12 at 07:30
  Biscuit, completed: ['Morning walk']
```

## 📸 Demo Walkthrough

1. Run `streamlit run app.py`. The app starts with an empty owner, "Jordan"; rename them if you like.
2. Under **Add a pet**, enter a name, species and age and click **Add pet**. A green confirmation appears.
3. Under **Add a task**, choose the pet, type a description, pick a time and frequency (`once`, `daily`, `weekly`) and click **Add task**. Add a second task at the same time to see a conflict.
4. Click **Show schedule**. Conflicts appear as yellow warnings (or a green "No scheduling conflicts" message), followed by a table sorted by date and time.
5. Use the **Pet** and **Status** dropdowns to filter the table.
6. Under **Complete a task**, pick a pending task and click **Mark complete**. The table updates, and a daily or weekly task gets a new row for its next occurrence.

**Screenshot or video** *(optional)*: not included.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time`, `get_todays_schedule` | Sorts by `(due_date, "HH:MM")` using a lambda key; zero-padded 24-hour strings sort chronologically. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Either filter, both, or neither; pet name match is case-insensitive. |
| Conflict handling | `Scheduler.detect_conflicts` | Returns warning strings for pending tasks sharing the same date and start time (across pets too). Never raises. |
| Recurring tasks | `Task.mark_complete`, `Scheduler.handle_recurring` | Completing a `daily`/`weekly` task creates the next one at `due_date + timedelta(days=1 / weeks=1)` and attaches it to the same pet. |

## 🧪 Testing PawPal+

```bash
python -m pytest
```

**Covered (17 tests in `tests/test_pawpal.py`):** task completion, adding tasks, time/frequency validation, chronological sorting, today's schedule filtering, daily and weekly recurrence (plus one-off, double-complete and stray-task cases), conflict detection (cross-pet, no conflict, completed/other-day tasks ignored), filtering by pet and status, and edge cases (pet with no tasks, empty owner).

**Confidence: 4/5.** The logic layer is well covered. The Streamlit UI was only exercised with Streamlit's `AppTest` and by hand, and conflicts only match exact start times.

## Assumptions and limitations

- Tasks have a start time but no duration or priority, so conflict detection is exact-match only (see `reflection.md`, 2b).
- "Today" means the machine's local date. Overdue tasks from earlier days are not shown in the "today" schedule, but they do appear in the UI table.
- Data is held in memory only; restarting the app clears it.
- Pet names are treated as unique per owner (case-insensitive).
