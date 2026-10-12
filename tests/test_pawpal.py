from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def owner():
    o = Owner("Jordan")
    dog, cat = Pet("Biscuit", "dog", 4), Pet("Mochi", "cat", 2)
    o.add_pet(dog)
    o.add_pet(cat)
    return o


# --- core behaviour ---------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog", 4)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Feed", "09:00"))
    assert len(pet.tasks) == 2


def test_add_task_sets_pet_name_and_pending_filter():
    pet = Pet("Biscuit", "dog")
    done, todo = Task("Walk", "08:00"), Task("Feed", "09:00")
    pet.add_task(done)
    pet.add_task(todo)
    done.mark_complete()
    assert done.pet_name == "Biscuit"
    assert pet.get_pending_tasks() == [todo]


def test_invalid_time_and_frequency_rejected():
    with pytest.raises(ValueError):
        Task("Walk", "25:00")
    with pytest.raises(ValueError):
        Task("Walk", "8am")
    with pytest.raises(ValueError):
        Task("Walk", "08:00", frequency="hourly")


# --- sorting ----------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(owner):
    pet = owner.pets[0]
    for t in ("18:00", "07:30", "12:15", "09:05"):
        pet.add_task(Task(f"task {t}", t))
    s = Scheduler(owner)
    assert [t.time for t in s.sort_by_time(owner.get_all_tasks())] == [
        "07:30", "09:05", "12:15", "18:00"]


def test_todays_schedule_sorted_and_excludes_other_days(owner):
    owner.pets[0].add_task(Task("Late", "20:00"))
    owner.pets[1].add_task(Task("Early", "06:00"))
    owner.pets[0].add_task(Task("Tomorrow", "01:00", due_date=date.today() + timedelta(days=1)))
    assert [t.description for t in Scheduler(owner).get_todays_schedule()] == ["Early", "Late"]


# --- recurrence -------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task(owner):
    pet = owner.pets[0]
    task = Task("Walk", "08:00", "daily")
    pet.add_task(task)
    new = Scheduler(owner).handle_recurring(task)
    assert task.completed is True
    assert new is not None and new.completed is False
    assert new.due_date == task.due_date + timedelta(days=1)
    assert new.time == "08:00" and new.pet_name == "Biscuit"
    assert new in pet.tasks and len(pet.tasks) == 2


def test_weekly_recurrence_creates_task_a_week_later(owner):
    task = Task("Bath", "10:00", "weekly")
    owner.pets[0].add_task(task)
    new = Scheduler(owner).handle_recurring(task)
    assert new.due_date == task.due_date + timedelta(weeks=1)


def test_one_off_task_does_not_recur(owner):
    task = Task("Vet", "10:00", "once")
    owner.pets[0].add_task(task)
    assert Scheduler(owner).handle_recurring(task) is None
    assert len(owner.pets[0].tasks) == 1


def test_completing_twice_does_not_duplicate(owner):
    task = Task("Walk", "08:00", "daily")
    owner.pets[0].add_task(task)
    s = Scheduler(owner)
    s.handle_recurring(task)
    assert s.handle_recurring(task) is None
    assert len(owner.pets[0].tasks) == 2


def test_recurring_task_not_owned_by_owner_is_ignored(owner):
    stray = Task("Walk", "08:00", "daily")
    assert Scheduler(owner).handle_recurring(stray) is None


# --- conflicts --------------------------------------------------------------

def test_conflict_detection_flags_duplicate_times_across_pets(owner):
    owner.pets[0].add_task(Task("Walk", "08:00"))
    owner.pets[1].add_task(Task("Feed", "08:00"))
    owner.pets[1].add_task(Task("Play", "09:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0] and "Biscuit" in warnings[0] and "Mochi" in warnings[0]


def test_no_conflicts_returns_empty_list(owner):
    owner.pets[0].add_task(Task("Walk", "08:00"))
    owner.pets[0].add_task(Task("Feed", "09:00"))
    assert Scheduler(owner).detect_conflicts() == []


def test_completed_tasks_and_different_dates_do_not_conflict(owner):
    done = Task("Walk", "08:00")
    owner.pets[0].add_task(done)
    done.mark_complete()
    owner.pets[1].add_task(Task("Feed", "08:00"))
    owner.pets[1].add_task(Task("Feed", "08:00", due_date=date.today() + timedelta(days=1)))
    assert Scheduler(owner).detect_conflicts() == []


# --- filtering --------------------------------------------------------------

def test_filter_by_pet_and_status(owner):
    a, b, c = Task("Walk", "08:00"), Task("Feed", "09:00"), Task("Play", "10:00")
    owner.pets[0].add_task(a)
    owner.pets[0].add_task(b)
    owner.pets[1].add_task(c)
    a.mark_complete()
    s = Scheduler(owner)
    assert s.filter_tasks(pet_name="biscuit") == [a, b]
    assert s.filter_tasks(completed=True) == [a]
    assert s.filter_tasks(pet_name="Biscuit", completed=False) == [b]
    assert s.filter_tasks(pet_name="Mochi", completed=True) == []
    assert len(s.filter_tasks()) == 3


# --- edge cases -------------------------------------------------------------

def test_pet_with_no_tasks(owner):
    assert owner.pets[0].get_pending_tasks() == []
    assert Scheduler(owner).get_todays_schedule() == []


def test_empty_owner_never_crashes():
    s = Scheduler(Owner("Nobody"))
    assert s.get_todays_schedule() == []
    assert s.detect_conflicts() == []
    assert s.filter_tasks("Ghost", True) == []
    assert s.sort_by_time([]) == []
