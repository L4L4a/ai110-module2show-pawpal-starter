"""PawPal+ logic layer: Owner, Pet, Task and Scheduler."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
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

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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
