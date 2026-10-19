# AI Interactions Log

## Agent Workflow (SF7)

**What task did you give the agent?**

Build PawPal+ end to end from the starter: UML, `pawpal_system.py`, `main.py`, tests, the Streamlit UI, docs, then stretch features (next-slot search, JSON persistence, formatted output) and UI screenshots.

**What did the agent do?**

- Files modified/created: `pawpal_system.py`, `main.py`, `app.py`, `tests/test_pawpal.py`, `diagrams/uml.mmd`, `diagrams/uml_final.mmd`, `README.md`, `reflection.md`, `requirements.txt`, `.gitignore`, `docs/screenshots/*`.
- Wrote the dataclasses, `Scheduler` (sort, filter, conflicts, recurrence, daily plan, next slot), and `Owner.save`/`load`.
- Ran `main.py` and pytest after changes (16 tests passing), ran the Streamlit app headlessly, and captured screenshots with Playwright driving Chrome.
- Committed and pushed to `main`.

**What did you have to verify or fix manually?**

- The first UI draft had two bugs found only by checking behavior: the success message disappeared because of an immediate `st.rerun()`, and "Complete task" never changed the stored task because the selectbox returned a copy (fixed by selecting by index).
- `_slot_hint` first built a throwaway Owner; simplified with an `ignore` parameter.
- Early test and demo commands failed with `python: command not found` (use `python3`); one agent command killed its own shell by using `pkill -f` on a pattern it also contained.
- The conflict screenshot was captured before the selectbox fix; it was still accurate because it shows only the warning.

---

## Prompt Comparison (SF11)

Compared two prompting strategies for conflict detection. Only Option B was implemented; Option A was evaluated by reasoning about its behavior on the demo data.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Code (Sonnet 5.5) | Claude Code (Sonnet 5.5) |
| **Prompt** | "Detect if two tasks are scheduled at the same time" (exact start-time match) | "Detect tasks whose time windows overlap, using start time plus duration, across all pets" |
| **Response summary** | Group pending tasks by `due_time` and flag groups of 2+ | Sort pending tasks and flag pairs where the later start is before the earlier end |
| **What was useful** | Very short and easy to read | Catches a 08:00-08:30 walk overlapping an 08:15 feeding; back-to-back tasks are not flagged |
| **Problems noticed** | Misses that overlap without sharing a start time | Slightly longer; pairwise comparison is O(n²) |
| **Decision** | Rejected | Used |

**Which approach did you use in your final implementation and why?**

Option B (`Scheduler.detect_conflicts`). Real tasks have durations, so exact-time matching would miss the most common clash. O(n²) is fine for a household's daily tasks. Tests cover identical times, partial overlap, and back-to-back tasks.

*Option A's output was not run; its "problems" are from analysis. Edit these entries to match your own experience.*
