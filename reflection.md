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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

I used the AI assistant to brainstorm classes and draft the Mermaid UML, generate dataclass skeletons, implement the Scheduler, and draft the demo and tests. Prompts that named the exact classes and the rubric requirements (e.g. "Scheduler must read from Owner.get_all_tasks") worked best.

**b. Judgment and verification**

I kept the design to four classes and did not add extra ones (e.g. a separate Plan class), to avoid unneeded complexity; I also trimmed the duplicate Scheduler/Owner task access down to one source. I verified behavior by running `python3 main.py` (the demo deliberately includes an overlapping walk and feeding) and by running the pytest suite.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
