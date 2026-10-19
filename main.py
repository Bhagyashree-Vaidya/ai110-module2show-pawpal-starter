"""Demo script for PawPal+."""
from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def show(title, tasks):
    print(f"\n{title}")
    print("-" * len(title))
    for t in tasks:
        mark = "x" if t.completed else " "
        print(f"[{mark}] {t.due_time:%H:%M}  {t.pet_name:<8} {t.description:<14} "
              f"{t.duration_minutes:>3} min  {t.priority}")


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
        print(f"  WARNING: {warning}")

    nxt = scheduler.complete_task(plan[0])
    print(f"\nCompleted '{plan[0].description}'; next one scheduled for {nxt.due_time:%a %H:%M}")


if __name__ == "__main__":
    main()
