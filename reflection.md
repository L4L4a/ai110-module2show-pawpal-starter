# PawPal+ Project Reflection

## 1. System Design

**1a. Initial Design**

I started with four classes (`diagrams/uml_draft.mmd`) and tried to give each one a single job:

- `Task`: one piece of care work. It has a description, an `HH:MM` time, a frequency (`once`/`daily`/`weekly`), a `completed` flag and a `due_date`.
- `Pet`: name, species, age, and a list of `Task`s. It has `add_task` and `get_pending_tasks`.
- `Owner`: holds the list of `Pet`s. `get_all_tasks` flattens every pet's tasks so nothing else needs to loop over pets.
- `Scheduler`: takes an `Owner` and holds no data of its own. Sorting, filtering, conflicts and recurrence all live here.

Relationships are Owner 1-* Pet, Pet 1-* Task, and Scheduler pointing at Owner. I put the algorithms in `Scheduler` on purpose. The three data classes stay dumb and easy to test, and anything that has to look across pets has exactly one place to live. I used `HH:MM` strings instead of `datetime` objects so they sort as plain strings and drop straight into a Streamlit table.

**1b. Design changes**

The design changed in three places. You can see them by diffing `uml_draft.mmd` against `uml_final.mmd`, plus the code in `pawpal_system.py`.

- I added `Task.pet_name`, which `Pet.add_task` fills in. The draft didn't have it. Once `Owner.get_all_tasks` flattens everything, a task had no idea which pet it belonged to, so filtering by pet and showing a "Pet" column in the UI table were both impossible.
- `Task.mark_complete()` now returns the next occurrence (or `None`) instead of returning nothing. The date math with `timedelta` belongs on the task, and it means I can test recurrence without building an `Owner`. `Scheduler.handle_recurring` just finds the pet that owns the task and attaches the new one.
- `Task.__post_init__` validates the time and frequency. A bad time like `"25:00"` now raises `ValueError` right away instead of quietly breaking the sort later.

---

## 2. Scheduling Logic and Tradeoffs

**2a. Constraints and priorities**

The scheduler looks at start time, due date, completed status, which pet a task belongs to, and frequency. It does not look at duration, priority or owner preferences. The original README says tasks should have at least duration and priority, and I didn't build either, so that's a gap against the spec. Time of day was the constraint I treated as most important, because a schedule is only useful if it reads in order, and the conflict check falls out of it. Completion status came second so that finished tasks don't show up as pending or trigger fake conflicts.

**2b. Tradeoffs**

`Scheduler.detect_conflicts` only flags tasks with the **exact same date and start time**. Two things at `08:00` get a warning. A walk at `08:00` and a feeding at `08:15` don't, and that holds even if the walk runs 30 minutes, because `Task` has no duration field. A proper fix needs durations and an interval check (`start_a < end_b and start_b < end_a`). It also forces a decision I didn't want to make for this project: can one person feed the cat while the dog is on a walk?

I went with exact matching because it's simple, it's easy to test, and it catches the most obvious mistake, double-booking a slot. It returns warning strings and doesn't block anything, so the owner makes the call. The cost is false negatives for overlapping tasks that start at different times. It does check across all pets, since the owner is one person.

---

## 3. AI Collaboration

**3a. How you used AI**

I used Claude Code for most of the build. I handed it a phase-by-phase brief covering the UML, the classes, `app.py`, the algorithms, the tests and the polish, and it wrote the code and made one commit per phase (see `git log`). By phase:

- **Scaffolding:** `pawpal_system.py`, `main.py` and the Streamlit wiring, including keeping the `Owner` in `st.session_state`.
- **UML:** the Mermaid files, `uml_draft.mmd` and `uml_final.mmd`.
- **Tests:** the 17 tests in `tests/test_pawpal.py`, including the edge cases (pet with no tasks, empty owner, completing the same task twice).

It also ran `pytest` and `main.py`, and it drove the Streamlit app headlessly with `streamlit.testing.v1.AppTest` to check the add pet, add task, conflict and mark-complete flow. The prompt that worked best was the long one with exact class names, method names and behaviours per phase, because it left little room for a different design.

**3b. Judgment and verification**

Here are the concrete cases where the output got corrected. Some of these are the AI correcting itself rather than me rejecting a suggestion, and I'm not going to dress that up:

- The repo's last commit renamed `diagrams/uml_draft.mmd` to `uml.mmd` for grading, but the brief asked for `uml_draft.mmd` and `uml_final.mmd`. The result was both new files plus `uml.mmd` kept as a copy of the final. That's visible in the Phase 1 and Phase 6 commits.
- The first `main.py` picked the task to complete with a hard-coded list index, `[1]`. That only worked because of insertion order. It got changed to a lookup by description before the Phase 4 commit.
- The first "Mark complete" button in `app.py` updated the data but left the table above it stale for that run. It now stores the success messages in `st.session_state`, calls `st.rerun()`, and shows them on the next pass. A bad placeholder line (`st.rerun() if False else None`) was written and removed along the way.
- Running plain `pytest` failed to import `pawpal_system`, because only `python -m pytest` worked. A root `conftest.py` fixed that.
- The code uses no `X | None` type syntax because the Python here is 3.9.

I checked all this by running the tests, running `main.py`, and scripting the UI. The caveat is that I haven't opened the app in a browser.

---

## 4. Testing and Verification

**4a. What you tested**

I wrote 17 tests in `tests/test_pawpal.py`:

- Sorting: `sort_by_time` returns chronological order, and `get_todays_schedule` excludes other days.
- Recurrence: a daily task creates a next-day task, a weekly one creates a task a week later, a `once` task creates nothing, and completing the same task twice doesn't duplicate it. A task that belongs to none of the owner's pets is ignored.
- Conflicts: duplicate times across pets are flagged, and there are no false positives for different times, completed tasks or different dates.
- Filtering: by pet (case-insensitive), by status, by both, and by neither.
- Validation: a bad time or frequency raises `ValueError`.
- Edge cases: a pet with no tasks and an empty `Owner`.

These are the things most likely to be subtly wrong: off-by-one-day recurrence, a finished task still counting as a conflict, or a crash on empty input.

**4b. Confidence**

I'd say 4 out of 5 for the logic layer. The UI is only covered by `AppTest` and manual clicking. With more time I'd test overlapping tasks (which needs durations), recurrence across month and year boundaries, duplicate pet names, and the real app in a browser.

---

## 5. Reflection

**5a. What went well**

Putting every algorithm in `Scheduler` and keeping `Task`, `Pet` and `Owner` simple. The logic was easy to test with no Streamlit involved, and `app.py` ended up as thin glue.

**5b. What you would improve**

- Add `duration` and `priority` to `Task` (the README lists both as a minimum), then change `detect_conflicts` to check for overlapping intervals instead of exact times.
- Persist data to a JSON file, because right now everything is in memory and disappears when the app restarts.
- Let the UI edit and delete tasks, and show overdue tasks from earlier days, which `get_todays_schedule` currently leaves out.

**5c. Key takeaway**

Having the UML and a per-phase spec first is what made the AI output fit together, because it had a design to follow. The output still had brittle shortcuts, like the hard-coded index in `main.py` and the stale table in `app.py`, and I only caught them by running things.
