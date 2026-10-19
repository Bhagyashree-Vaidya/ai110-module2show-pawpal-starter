"""Demo script for PawPal+."""
from datetime import datetime

from tabulate import tabulate

from pawpal_system import Owner, Pet, Scheduler, Task


PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}


def show(title, tasks):
    """Print tasks as a formatted table."""
    print(f"\n{title}")
    rows = [
        ["✅" if t.completed else "⬜", f"{t.due_time:%H:%M}", t.pet_name, t.description,
         f"{t.duration_minutes} min", PRIORITY_ICON[t.priority]]
        for t in tasks
    ]
    print(tabulate(rows, headers=["", "Time", "Pet", "Task", "Length", "Priority"], tablefmt="rounded_outline"))


def main():
    today = datetime.now().replace(second=0, microsecond=0)
    at = lambda h, m=0: today.replace(hour=h, minute=m)

    owner = Owner("Jordan", available_minutes_per_day=90)
    biscuit, whiskers = Pet("Biscuit", "dog", 3), Pet("Whiskers", "cat", 5)
    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    biscuit.add_task(Task("Evening walk", at(18), 30, "medium", "daily"))
    biscuit.add_task(Task("Morning walk", at(8), 30, "high", "daily"))
    whiskers.add_task(Task("Feeding", at(8, 15), 10, "high", "daily"))  # overlaps morning walk
    whiskers.add_task(Task("Grooming", at(14), 60, "low"))

    scheduler = Scheduler(owner)
    show("All tasks, sorted by time", scheduler.sort_by_time())
    plan = scheduler.build_daily_plan()
    show(f"Today's Schedule for {owner.name}", plan)
    print(scheduler.explain_plan(plan))
    show("Whiskers only", scheduler.filter_tasks(pet_name="Whiskers"))

    print("\nConflicts:")
    for warning in scheduler.conflict_warnings():
        print(f"  ⚠️  {warning}")

    slot = scheduler.find_next_slot(30, at(8))
    print(f"\nNext free 30-minute slot from 08:00: {slot:%H:%M}")

    nxt = scheduler.complete_task(plan[0])
    print(f"\nCompleted '{plan[0].description}'; next one scheduled for {nxt.due_time:%a %H:%M}")


if __name__ == "__main__":
    main()
