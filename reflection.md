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
- Review of the skeleton flagged a bottleneck: the Scheduler needs one way to reach all tasks, so it reads only through `Owner.get_all_tasks()` rather than touching pets directly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers due time, task priority, task duration, and the owner's daily time budget. Priority matters most when time is short (high-priority tasks are chosen first), and due time decides display order, since a pet owner mainly needs to know what to do next.

**b. Tradeoffs**

Conflict detection only warns about overlapping tasks; it does not reschedule them, and it compares every pair of pending tasks (O(n²)). That is reasonable for a household with a handful of daily tasks, keeps the code readable, and leaves the decision to move a task with the owner. I also kept a plain loop-based comprehension over a more compact but harder-to-read version.

---

## 3. AI Collaboration

**a. How you used AI**

I used the AI assistant to brainstorm classes and draft the Mermaid UML, generate dataclass skeletons, implement the Scheduler, and draft the demo and tests. Prompts that named the exact classes and the rubric requirements (e.g. "Scheduler must read from Owner.get_all_tasks") worked best.

**b. Judgment and verification**

The agent features that helped most were multi-file edits and running the demo and tests directly to check its own work. I kept the design to four classes and did not add extra ones (e.g. a separate Plan class), to avoid unneeded complexity; I also trimmed the duplicate Scheduler/Owner task access down to one source. I verified behavior by running `python3 main.py` (the demo deliberately includes an overlapping walk and feeding) and by running the pytest suite.

---

## 4. Testing and Verification

**a. What you tested**

Task completion, adding tasks, sorting and filtering across pets, conflict detection (overlap, identical times, back-to-back not flagged), daily/weekly recurrence, empty pets, and the plan's priority and time budget. These are the behaviors the UI depends on and where silent logic bugs would hurt most.

**b. Confidence**

About 4/5: all 11 tests pass and the Streamlit app was smoke-tested. Next I would test tasks that cross midnight, invalid priority values, and catching up recurring tasks that were missed for several days.

---

## 5. Reflection

**a. What went well**

Keeping the Scheduler reading everything through `Owner.get_all_tasks()`, so every feature naturally works across multiple pets and the UI stays thin.

**b. What you would improve**

Persist data to JSON, add a "next available slot" suggestion for conflicts, and let users edit or delete tasks in the UI.

**c. Key takeaway**

The AI is fast at producing code, but the human has to be the lead architect: decide the classes and boundaries first, keep the design small, and verify with tests and a real run. Working in separate phases (design, logic, algorithms, tests, UI) kept each change focused and reviewable.
