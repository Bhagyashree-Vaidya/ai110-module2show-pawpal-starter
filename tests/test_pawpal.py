from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task

T0 = datetime(2025, 1, 1, 8, 0)


def make():
    owner = Owner("Sam", 60)
    a, b = Pet("A", "dog"), Pet("B", "cat")
    owner.add_pet(a)
    owner.add_pet(b)
    return owner, a, b


def test_mark_complete_changes_status():
    t = Task("Walk", T0)
    t.mark_complete()
    assert t.completed


def test_add_task_increases_count():
    pet = Pet("A", "dog")
    pet.add_task(Task("Walk", T0))
    assert len(pet.tasks) == 1


def test_sort_by_time_across_pets():
    owner, a, b = make()
    a.add_task(Task("late", T0 + timedelta(hours=5)))
    b.add_task(Task("early", T0))
    assert [t.description for t in Scheduler(owner).sort_by_time()] == ["early", "late"]


def test_filter_by_pet_and_status():
    owner, a, b = make()
    a.add_task(Task("x", T0))
    done = Task("y", T0)
    b.add_task(done)
    done.mark_complete()
    s = Scheduler(owner)
    assert [t.description for t in s.filter_tasks(pet_name="A")] == ["x"]
    assert s.filter_tasks(completed=True) == [done]


def test_conflict_detected_across_pets():
    owner, a, b = make()
    a.add_task(Task("walk", T0, 30))
    b.add_task(Task("feed", T0 + timedelta(minutes=10), 10))
    assert len(Scheduler(owner).detect_conflicts()) == 1


def test_daily_recurrence_creates_next_task():
    owner, a, _ = make()
    t = Task("meds", T0, frequency="daily")
    a.add_task(t)
    nxt = Scheduler(owner).complete_task(t)
    assert nxt.due_time == T0 + timedelta(days=1) and not nxt.completed
    assert len(a.tasks) == 2


def test_plan_respects_time_budget_and_priority():
    owner, a, _ = make()
    a.add_task(Task("low", T0, 40, "low"))
    a.add_task(Task("high", T0 + timedelta(hours=1), 40, "high"))
    plan = Scheduler(owner).build_daily_plan(T0)
    assert [t.description for t in plan] == ["high"]
