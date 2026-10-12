"""PawPal+ logic layer: Owner, Pet, Task and Scheduler."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional

FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet care task scheduled at an HH:MM time on a due date."""

    description: str
    time: str  # 24-hour "HH:MM"
    frequency: str = "once"  # "once", "daily" or "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""  # filled in by Pet.add_task

    def __post_init__(self) -> None:
        try:
            datetime.strptime(self.time, "%H:%M")
        except ValueError:
            raise ValueError(f"time must be HH:MM (24-hour), got {self.time!r}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {FREQUENCIES}, got {self.frequency!r}")

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as done.

        Returns the next occurrence for a daily/weekly task (not yet attached
        to a pet), or None for one-off tasks or if it was already complete.
        """
        if self.completed:
            return None
        self.completed = True
        step = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}.get(self.frequency)
        if step is None:
            return None
        return Task(self.description, self.time, self.frequency, False,
                    self.due_date + step, self.pet_name)


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return the tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    """A pet owner; the single entry point to all pets and tasks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds schedules from the tasks an Owner's pets hold."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_todays_schedule(self, today: Optional[date] = None) -> List[Task]:
        """Return tasks due today in time order."""
        today = today or date.today()
        due = [t for t in self.owner.get_all_tasks() if t.due_date == today]
        return sorted(due, key=lambda t: t.time)

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by due date, then HH:MM time."""
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Filter all tasks by pet name and/or completion status (None = any)."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> List[str]:
        """Return a warning string for each date/time slot with 2+ pending tasks.

        Only exact start-time matches are detected (tasks have no duration).
        Never raises; returns an empty list when there are no conflicts.
        """
        slots = {}
        for task in self.owner.get_all_tasks():
            if not task.completed:
                slots.setdefault((task.due_date, task.time), []).append(task)
        warnings = []
        for (due, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = ", ".join(f"{t.pet_name}: {t.description}" for t in group)
                warnings.append(f"Conflict on {due.isoformat()} at {time}: {names}")
        return warnings

    def handle_recurring(self, task: Task) -> Optional[Task]:
        """Complete a task and, if it repeats, add its next occurrence to the same pet.

        Returns the newly created task, or None if nothing was created.
        """
        next_task = task.mark_complete()
        if next_task is None:
            return None
        for pet in self.owner.pets:
            if any(t is task for t in pet.tasks):
                pet.add_task(next_task)
                return next_task
        return None  # task does not belong to any of this owner's pets
