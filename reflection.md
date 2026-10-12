# PawPal+ Project Reflection

## 1. System Design

**1a. Initial Design**

My first UML (`diagrams/uml_draft.mmd`) has four classes, each with one job:

- **Task** holds one piece of care work: a description, an `HH:MM` time, a frequency (`once`, `daily`, `weekly`), a completed flag and a due date. It only knows how to mark itself complete.
- **Pet** (name, species, age) owns a list of Tasks and can add one or list the pending ones. A task belongs to exactly one pet, so the pet is the natural container.
- **Owner** owns a list of Pets and can flatten every pet's tasks into one list (`get_all_tasks`). It is the single entry point to the data.
- **Scheduler** holds no data of its own. It takes an Owner and does the "thinking": today's schedule, sorting, filtering, conflict detection and recurrence.

Relationships: Owner 1-* Pet, Pet 1-* Task, and Scheduler points at Owner.

I kept the algorithms out of the data classes on purpose. Task, Pet and Owner stay simple containers that are easy to test, and anything that looks across several pets lives in one place, the Scheduler. Times are `HH:MM` strings so they sort lexicographically and are easy to show in a UI.

**b. Design changes**

Yes, three changes (compare `uml_draft.mmd` with `uml_final.mmd`):

- `Task` gained a `pet_name` field, set by `Pet.add_task`. The draft had no way to tell which pet a task belonged to once `Owner.get_all_tasks` flattened them, which made filtering by pet and showing results in a table impossible.
- `Task.mark_complete` now returns the next occurrence (or `None`). I first thought of putting all recurrence logic in the Scheduler, but the date maths belongs with the task and is then testable without an Owner. `Scheduler.handle_recurring` only finds the owning pet and attaches the new task.
- `Task` validates its time and frequency in `__post_init__`, so a bad `"25:00"` fails when the task is created instead of corrupting sorting later.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers start time, due date, completion status, the pet a task belongs to, and recurrence. I did not model duration, priority or owner preferences. Time of day matters most, because the plan has to be read in order, and the double-booking check follows directly from it. Completion status comes next, since finished tasks must not clutter the plan or trigger false conflicts.

**2b. Tradeoffs**

Conflict detection only matches **exact start times**. Two tasks at `08:00` are flagged, but a 30-minute walk at `08:00` and a feeding at `08:15` are not, because a `Task` has no duration. Doing it properly means storing a duration, converting times to minutes and checking interval overlap (`start_a < end_b and start_b < end_a`), and it raises extra questions such as whether one person can walk the dog and feed the cat at once.

I chose exact matching because it is easy to explain, easy to test, and catches the most common mistake, double-booking the same slot. It also returns warnings instead of blocking anything, so the owner decides. For a single owner with a handful of short daily tasks, a false negative costs little. The cost is that real overlaps slip through, and adding durations is the first thing I would do next.

A second, smaller tradeoff is that conflicts are checked across all pets, because the owner is one person who cannot be in two places.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code as an agent for the whole build. I gave it a phase-by-phase brief (UML, core classes, UI, algorithms, tests, polish) and it wrote the code, ran pytest and `main.py`, and made one git commit per phase. It also drove the Streamlit app headlessly with `streamlit.testing.v1.AppTest` to check the add pet, add task, conflict and mark-complete flow. The most useful prompt was the one that named exact classes, methods and behaviours per phase, which left little room for it to invent a different design.

**b. Judgment and verification**

Several first drafts were changed before they were committed:

- The first `main.py` picked the task to complete with a hard-coded list index (`[1]`). That only worked because of the insertion order, so I replaced it with a lookup by description.
- The first version of the "Mark complete" button in the UI updated the data but left the table above it stale for that run. I changed it to store the success messages in `st.session_state` and call `st.rerun()`.
- Plain `pytest` could not import `pawpal_system` (only `python -m pytest` worked), so I added a root `conftest.py`.
- The code avoids `X | None` type syntax so it runs on Python 3.9, which is what is installed here.

I verified by running the 17 tests, running `main.py`, and scripting the Streamlit UI end to end. I have not looked at the app in a browser.

---

## 4. Testing and Verification

**a. What you tested**

Sorting order, daily and weekly recurrence (including one-off tasks, completing the same task twice, and a task that belongs to no pet), exact-time conflict detection (across pets, none, ignoring completed and other-day tasks), filtering by pet and status, input validation, and edge cases (a pet with no tasks, an empty owner). These are the behaviours a user would see go wrong first, and most of them are easy to get subtly wrong, such as an off-by-one-day recurrence or a false conflict from a finished task.

**b. Confidence**

About 4 out of 5 for the logic layer. Next I would test tasks that overlap but start at different times (which needs durations), recurrence across month and year boundaries, tasks created for past dates, duplicate pet names, and the UI in a real browser.

---

## 5. Reflection

**a. What went well**

Keeping all the algorithms in `Scheduler` while `Task`, `Pet` and `Owner` stay simple. That made the logic easy to test without the UI, and the Streamlit app is thin glue over it.

**b. What you would improve**

Add task duration and priority, switch conflict detection to interval overlap, and persist data to a JSON file so it survives restarts. I would also let the UI edit and delete tasks and show overdue tasks from earlier days.

**c. Key takeaway**

A clear design written first (the UML and a per-phase brief) is what let an AI agent produce coherent code quickly. Its output still needed checking by running it, because it contained brittle shortcuts that only showed up when executed.
