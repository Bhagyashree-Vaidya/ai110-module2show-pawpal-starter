"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import json
from datetime import datetime, timedelta
from pathlib import Path

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCY_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    due_time: datetime
    duration_minutes: int = 15
    priority: str = "medium"  # high | medium | low
    frequency: str = "once"  # once | daily | weekly
    completed: bool = False
    pet_name: str = ""

    @property
    def end_time(self) -> datetime:
        """Return when the task finishes."""
        return self.due_time + timedelta(minutes=self.duration_minutes)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def to_dict(self) -> dict:
        """Serialize to a JSON-friendly dict."""
        return {**self.__dict__, "due_time": self.due_time.isoformat()}

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Rebuild a Task from to_dict output."""
        return cls(**{**data, "due_time": datetime.fromisoformat(data["due_time"])})

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy of this task for its next due date, or None if it does not repeat."""
        delta = FREQUENCY_DELTA.get(self.frequency)
        if delta is None:
            return None
        return replace(self, due_time=self.due_time + delta, completed=False)


@dataclass
class Pet:
    """A pet and the care tasks assigned to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def to_dict(self) -> dict:
        """Serialize this pet and its tasks."""
        return {"name": self.name, "species": self.species, "age": self.age,
                "tasks": [t.to_dict() for t in self.tasks]}

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Rebuild a Pet from to_dict output."""
        return cls(data["name"], data["species"], data["age"],
                   [Task.from_dict(t) for t in data["tasks"]])

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    available_minutes_per_day: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet."""
        return [t for pet in self.pets for t in pet.tasks]

    def save(self, path: str | Path) -> None:
        """Write the owner, pets, and tasks to a JSON file."""
        data = {"name": self.name, "available_minutes_per_day": self.available_minutes_per_day,
                "pets": [p.to_dict() for p in self.pets]}
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> Owner:
        """Load an owner from a JSON file, or return a new default Owner if the file is missing or invalid."""
        try:
            data = json.loads(Path(path).read_text())
            return cls(data["name"], data["available_minutes_per_day"],
                       [Pet.from_dict(p) for p in data["pets"]])
        except (OSError, ValueError, KeyError, TypeError):
            return cls("Jordan")


class Scheduler:
    """Organizes and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Fetch all tasks via the owner (spans every pet)."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by due time (all tasks if none given)."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: t.due_time)

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Filter all tasks by pet name and/or completion status."""
        return [
            t for t in self.get_all_tasks()
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of pending tasks whose time windows overlap (across any pets)."""
        tasks = self.sort_by_time(self.filter_tasks(completed=False))
        return [
            (a, b)
            for i, a in enumerate(tasks)
            for b in tasks[i + 1:]
            if b.due_time < a.end_time
        ]

    def conflict_warnings(self) -> list[str]:
        """Return human-readable warnings for overlapping tasks (never raises)."""
        return [
            f"{a.pet_name}'s '{a.description}' ({a.due_time:%H:%M}-{a.end_time:%H:%M}) "
            f"overlaps {b.pet_name}'s '{b.description}' ({b.due_time:%H:%M})"
            + self._slot_hint(b)
            for a, b in self.detect_conflicts()
        ]

    def _slot_hint(self, task: Task) -> str:
        """Suggest the next free time for a conflicting task."""
        slot = self.find_next_slot(task.duration_minutes, task.due_time, ignore=task)
        return f" - next free slot: {slot:%H:%M}" if slot else ""

    def find_next_slot(self, duration_minutes: int, after: datetime, day_end_hour: int = 22,
                       ignore: Task | None = None) -> datetime | None:
        """Return the earliest start at or after `after` where a task of this length fits without overlap (ignoring `ignore`), or None if it would end after day_end_hour."""
        need = timedelta(minutes=duration_minutes)
        limit = after.replace(hour=day_end_hour, minute=0, second=0, microsecond=0)
        start = after
        for t in self.sort_by_time(self.filter_tasks(completed=False)):
            if t is ignore or t.end_time <= start:
                continue
            if t.due_time >= start + need:
                break
            start = t.end_time
        return start if start + need <= limit else None

    def complete_task(self, task: Task) -> Task | None:
        """Complete a task and, if it recurs, schedule the next occurrence on its pet."""
        task.mark_complete()
        nxt = task.next_occurrence()
        if nxt is not None:
            pet = next(p for p in self.owner.pets if p.name == task.pet_name)
            pet.add_task(nxt)
        return nxt

    def build_daily_plan(self, day: datetime | None = None) -> list[Task]:
        """Pick pending tasks for a day by priority, within the owner's time budget, ordered by time."""
        day = (day or datetime.now()).date()
        todays = [t for t in self.filter_tasks(completed=False) if t.due_time.date() == day]
        todays.sort(key=lambda t: (PRIORITY_RANK.get(t.priority, 1), t.due_time))
        plan, used = [], 0
        for t in todays:
            if used + t.duration_minutes <= self.owner.available_minutes_per_day:
                plan.append(t)
                used += t.duration_minutes
        return self.sort_by_time(plan)

    def explain_plan(self, plan: list[Task]) -> str:
        """Describe why these tasks were chosen."""
        used = sum(t.duration_minutes for t in plan)
        return (
            f"Scheduled {len(plan)} task(s) using {used} of "
            f"{self.owner.available_minutes_per_day} available minutes. "
            "Higher-priority tasks were chosen first; the plan is shown in time order."
        )
