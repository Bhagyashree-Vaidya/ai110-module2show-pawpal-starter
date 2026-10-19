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


def test_pet_with_no_tasks_and_empty_scheduler():
    owner, _, _ = make()
    s = Scheduler(owner)
    assert s.sort_by_time() == [] and s.detect_conflicts() == [] and s.build_daily_plan(T0) == []


def test_identical_times_flagged_with_warning():
    owner, a, b = make()
    a.add_task(Task("walk", T0, 20))
    b.add_task(Task("feed", T0, 10))
    warnings = Scheduler(owner).conflict_warnings()
    assert len(warnings) == 1 and "overlaps" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    owner, a, _ = make()
    a.add_task(Task("one", T0, 30))
    a.add_task(Task("two", T0 + timedelta(minutes=30), 30))
    assert Scheduler(owner).detect_conflicts() == []


def test_weekly_recurrence_and_one_off_task():
    owner, a, _ = make()
    weekly, once = Task("bath", T0, frequency="weekly"), Task("vet", T0)
    a.add_task(weekly)
    a.add_task(once)
    s = Scheduler(owner)
    assert s.complete_task(weekly).due_time == T0 + timedelta(weeks=1)
    assert s.complete_task(once) is None and len(a.tasks) == 3


def test_find_next_slot_skips_busy_blocks():
    owner, a, b = make()
    a.add_task(Task("walk", T0, 30))
    b.add_task(Task("feed", T0 + timedelta(minutes=30), 30))
    assert Scheduler(owner).find_next_slot(15, T0) == T0 + timedelta(minutes=60)


def test_find_next_slot_none_when_day_full():
    owner, a, _ = make()
    a.add_task(Task("all day", T0, 14 * 60))
    assert Scheduler(owner).find_next_slot(30, T0) is None


def test_conflict_warning_suggests_slot():
    owner, a, b = make()
    a.add_task(Task("walk", T0, 30))
    b.add_task(Task("feed", T0 + timedelta(minutes=10), 10))
    assert "next free slot: 08:30" in Scheduler(owner).conflict_warnings()[0]


def test_save_and_load_round_trip(tmp_path):
    owner, a, _ = make()
    a.add_task(Task("walk", T0, 30, "high", "daily"))
    path = tmp_path / "data.json"
    owner.save(path)
    loaded = Owner.load(path)
    assert loaded.name == "Sam" and loaded.pets[0].tasks[0] == a.tasks[0]


def test_load_missing_or_corrupt_file_returns_default(tmp_path):
    assert Owner.load(tmp_path / "nope.json").pets == []
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert Owner.load(bad).pets == []
