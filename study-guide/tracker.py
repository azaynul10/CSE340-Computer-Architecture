import re
import sys
from pathlib import Path

PLAN = Path(__file__).with_name("CSE340_Study_Guide.md")
TASK_RE = re.compile(r"^(\s*- \[)([ xX])(\] )(.*)$")


def load():
    lines = PLAN.read_text(encoding="utf-8").splitlines()
    tasks = []
    section = ""
    for i, line in enumerate(lines):
        if line.startswith("## "):
            section = line[3:].strip()
        m = TASK_RE.match(line)
        if m:
            tasks.append({"line": i, "done": m.group(2).lower() == "x", "text": m.group(4), "section": section})
    return lines, tasks


def save(lines):
    PLAN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def show(tasks, pending_only=False):
    section = None
    for n, t in enumerate(tasks, 1):
        if pending_only and t["done"]:
            continue
        if t["section"] != section:
            section = t["section"]
            print(f"\n== {section} ==")
        mark = "x" if t["done"] else " "
        print(f"  [{mark}] {n:>2}. {t['text']}")
    done = sum(t["done"] for t in tasks)
    print(f"\n{done}/{len(tasks)} done  ({100 * done // max(len(tasks), 1)}%)")
    nxt = next((t for t in tasks if not t["done"]), None)
    if nxt:
        print(f"NEXT -> {nxt['text']}")


def toggle(nums, value):
    lines, tasks = load()
    for n in nums:
        if not 1 <= n <= len(tasks):
            print(f"no task {n}")
            continue
        t = tasks[n - 1]
        lines[t["line"]] = TASK_RE.sub(lambda m: f"{m.group(1)}{'x' if value else ' '}{m.group(3)}{m.group(4)}", lines[t["line"]])
        print(("done: " if value else "undone: ") + t["text"])
    save(lines)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv or argv[0] in ("list", "ls"):
        _, tasks = load()
        show(tasks)
    elif argv[0] in ("next", "todo"):
        _, tasks = load()
        show(tasks, pending_only=True)
    elif argv[0] in ("done", "do") and len(argv) > 1:
        toggle([int(a) for a in argv[1:]], True)
    elif argv[0] in ("undo", "reset") and len(argv) > 1:
        toggle([int(a) for a in argv[1:]], False)
    else:
        print("usage: python tracker.py [list | next | done N [N...] | undo N [N...]]")


if __name__ == "__main__":
    main(sys.argv[1:])
