"""CLI demo for PawPal+."""
from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner("Jordan")
    biscuit = Pet("Biscuit", "dog", 4)
    mochi = Pet("Mochi", "cat", 2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added out of order on purpose so sorting is visible.
    biscuit.add_task(Task("Evening walk", "18:00", "daily"))
    biscuit.add_task(Task("Morning walk", "07:30", "daily"))
    mochi.add_task(Task("Feeding", "08:00", "daily"))
    mochi.add_task(Task("Flea medication", "12:15", "weekly"))
    return owner


def print_schedule(scheduler: Scheduler) -> None:
    print("Today's Schedule")
    print("=" * 40)
    for task in scheduler.get_todays_schedule():
        mark = "x" if task.completed else " "
        print(f"[{mark}] {task.time}  {task.pet_name:<8} {task.description} ({task.frequency})")


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    # Deliberate clash: Biscuit and Mochi both at 08:00.
    owner.pets[0].add_task(Task("Vet call", "08:00"))
    print_schedule(scheduler)

    print("\nConflicts")
    for warning in scheduler.detect_conflicts() or ["none"]:
        print(" !", warning)

    print("\nCompleting 'Morning walk' (daily)...")
    walk = next(t for t in scheduler.filter_tasks(pet_name="Biscuit") if t.description == "Morning walk")
    new = scheduler.handle_recurring(walk)
    print(f"  next occurrence: {new.description} on {new.due_date} at {new.time}")
    print("  Biscuit, completed:", [t.description for t in scheduler.filter_tasks("Biscuit", True)])


if __name__ == "__main__":
    main()
