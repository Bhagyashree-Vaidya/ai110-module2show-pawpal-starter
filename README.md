# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation summary

All logic is in [pawpal_system.py](pawpal_system.py):

- `Task` (dataclass): description, due time, duration, priority, frequency, completion status.
- `Pet` (dataclass): details plus its list of tasks.
- `Owner` (dataclass): holds pets; `get_all_tasks()` returns every pet's tasks together.
- `Scheduler`: reads tasks through `Owner.get_all_tasks()` so it works across all pets (sorting, filtering, conflicts, recurrence, daily plan).

Run the demo with `python3 main.py` and the tests with `python3 -m pytest`.

## 🖥️ Sample Output

Output of `python3 main.py`:

```

All tasks, sorted by time
-------------------------
[ ] 08:00  Biscuit  Morning walk    30 min  high
[ ] 08:15  Whiskers Feeding         10 min  high
[ ] 14:00  Whiskers Grooming        60 min  low
[ ] 18:00  Biscuit  Evening walk    30 min  medium

Today's Schedule for Jordan
---------------------------
[ ] 08:00  Biscuit  Morning walk    30 min  high
[ ] 08:15  Whiskers Feeding         10 min  high
[ ] 18:00  Biscuit  Evening walk    30 min  medium
Scheduled 3 task(s) using 70 of 90 available minutes. Higher-priority tasks were chosen first; the plan is shown in time order.

Whiskers only
-------------
[ ] 08:15  Whiskers Feeding         10 min  high
[ ] 14:00  Whiskers Grooming        60 min  low

Conflicts:
  Biscuit's Morning walk overlaps Whiskers's Feeding

Completed 'Morning walk'; next one scheduled for Mon 08:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /Users/bhagyashree/Desktop/A2/ai110-module2show-pawpal-starter
plugins: asyncio-1.4.0, anyio-4.13.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 7 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 14%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [ 28%]
tests/test_pawpal.py::test_sort_by_time_across_pets PASSED               [ 42%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 57%]
tests/test_pawpal.py::test_conflict_detected_across_pets PASSED          [ 71%]
tests/test_pawpal.py::test_daily_recurrence_creates_next_task PASSED     [ 85%]
tests/test_pawpal.py::test_plan_respects_time_budget_and_priority PASSED [100%]

============================== 7 passed in 0.01s ===============================
```

Coverage: task completion, adding tasks, sorting and filtering across pets, conflict detection, daily recurrence, and plan priority/time-budget.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time` | Orders tasks from all pets by due time |
| Filtering | `Scheduler.filter_tasks` | By pet name and/or completion status |
| Conflict handling | `Scheduler.detect_conflicts` | Reports overlapping time windows, including across different pets |
| Recurring tasks | `Scheduler.complete_task`, `Task.next_occurrence` | Completing a daily/weekly task adds the next one |
| Daily plan | `Scheduler.build_daily_plan`, `explain_plan` | Picks by priority within the owner's time budget, shown in time order |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
