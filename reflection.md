# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three core actions a user should be able to perform:**

1. **Add a pet** – enter basic owner and pet info (name, species, age) so the app knows who is being cared for.
2. **Schedule a care task** – add a task such as a walk, feeding, or medication to a pet, with a description, duration, priority, and due time (and whether it repeats).
3. **See today's plan** – view a daily schedule across all pets, sorted by time/priority, with conflicts flagged and an explanation of why the plan was chosen.

**Initial UML design** (see [diagrams/uml.mmd](diagrams/uml.mmd)). Four classes:

- **Owner** – holds the owner's name, daily time available, and a list of pets. Responsible for adding/removing pets and gathering all tasks across pets.
- **Pet** – holds name, species, age, and its own list of tasks. Responsible for adding/removing tasks and listing pending ones.
- **Task** – holds description, duration, priority, due time, frequency (once/daily/weekly), and completion status. Responsible for marking itself complete.
- **Scheduler** – the "brain." Takes an Owner and works across all pets' tasks: sorting by time, filtering by pet or status, detecting time conflicts, building the daily plan within the owner's available time, and explaining it.

Relationships: an Owner has many Pets, a Pet has many Tasks, and the Scheduler uses one Owner to reach everything else.

**b. Design changes**

- Added `Task.pet_name` (set by `Pet.add_task`) so the Scheduler can filter and report by pet without walking the pet list.
- Added `Task.next_occurrence()` and `Scheduler.complete_task()` so recurring tasks create their next copy; the skeleton only had `mark_complete()`.
- `explain_plan` now takes the plan as an argument, and `detect_conflicts` returns pairs of overlapping tasks.
- The Scheduler needs one way to reach all tasks, so it reads only through `Owner.get_all_tasks()` rather than touching pets directly.
- Later additions: `Scheduler.find_next_slot` and `Owner.save`/`load` (with `to_dict`/`from_dict` on `Task` and `Pet`) for JSON persistence.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers due time, task priority, task duration, and the owner's daily time budget. Priority matters most when time is short (high-priority tasks are chosen first), and due time decides display order, since a pet owner mainly needs to know what to do next.

**b. Tradeoffs**

Conflict detection only warns about overlapping tasks; it does not reschedule them, and it compares every pair of pending tasks (O(n²)). That is reasonable for a household with a handful of daily tasks, keeps the code readable, and leaves the decision to move a task with the owner. I also kept a plain loop-based comprehension over a more compact but harder-to-read version.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code (an AI coding agent) in one continuous session for the whole project: drafting the Mermaid UML, writing the dataclasses and `Scheduler`, the demo, the tests, the Streamlit wiring, and the docs. It could edit several files at once and run `main.py`, pytest, and a headless Streamlit test itself, which was the most effective feature because it checked its own work. Prompts worked best when they named the exact classes and requirements (e.g. "the Scheduler must read from `Owner.get_all_tasks`"). I did not use separate chat sessions per phase; I kept phases organized by committing after each one instead.

**b. Judgment and verification**

- I kept the design to four classes and rejected extra ones (such as a separate `Plan` class) to avoid complexity, and kept a single source for task access (`Owner.get_all_tasks`).
- I simplified `_slot_hint`, which first built a temporary Owner/Pet just to exclude one task; I replaced that with an `ignore` parameter on `find_next_slot`.
- Verification caught two real UI bugs the first draft shipped: the "Next one scheduled" message vanished because `st.rerun()` ran right after `st.success`, and "Mark complete" never marked the task because Streamlit's selectbox returns a copy of object options. I found the second by checking the saved state, not just that the page loaded, and fixed it by selecting by index.
- Checks: `python3 main.py`, the pytest suite (16 tests), and a headless Streamlit run plus browser screenshots.

**c. Lead architect**

The AI is fast, but I had to decide the class boundaries first, keep the design small, and check behavior against reality. Passing tests and a page that loads were not enough; the state had to be right.

---

## 4. Testing and Verification

**a. What you tested**

Task completion, adding tasks, sorting and filtering across pets, conflict detection (overlap, identical times, back-to-back not flagged), daily/weekly recurrence, empty pets, and the plan's priority and time budget. These are the behaviors the UI depends on and where silent logic bugs would hurt most.

**b. Confidence**

About 4/5: all 16 tests pass and the Streamlit app was smoke-tested. Next I would test tasks that cross midnight, invalid priority values, and catching up recurring tasks that were missed for several days.

---

## 5. Reflection

**a. What went well**

Keeping the Scheduler reading everything through `Owner.get_all_tasks()`, so every feature naturally works across multiple pets and the UI stays thin.

**b. What you would improve**

Let users edit or delete tasks in the UI, handle tasks that cross midnight, and auto-move a conflicting task into the suggested free slot.

**c. Key takeaway**

The AI is fast at producing code, but the human has to be the lead architect: decide the classes and boundaries first, keep the design small, and verify with tests and a real run. Working in separate phases (design, logic, algorithms, tests, UI) kept each change focused and reviewable.

---

**Time spent:** about 4 hours in total (see the breakdown in the README).
