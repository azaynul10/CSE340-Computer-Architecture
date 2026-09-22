import html
import re
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent
MD = ROOT / "CSE340_Study_Guide.md"
OUT = ROOT / "CSE340_Study_Guide.html"

CSS = """
body{font-family:Segoe UI,system-ui,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;line-height:1.45;color:#1c1c1c;background:#fafafa}
h1{border-bottom:3px solid #1e5aa8;padding-bottom:6px}
h2{margin-top:36px;background:#1e5aa8;color:#fff;padding:6px 12px;border-radius:6px}
ul{list-style:none;padding-left:0}
ul ul{padding-left:28px;list-style:disc}
ul ul li{margin:2px 0}
li.task{margin:8px 0;padding:6px 10px;border-left:4px solid #1e5aa8;background:#fff;border-radius:4px}
li.task.done{border-left-color:#3a9a3a;background:#eef7ee;color:#666}
li.task.done>.label{text-decoration:line-through}
li.task .box{display:inline-block;width:1.1em;font-weight:bold;color:#1e5aa8}
li.task.done .box{color:#3a9a3a}
code{background:#eef1f6;padding:1px 5px;border-radius:3px;font-size:.92em}
table{border-collapse:collapse;width:100%;margin:12px 0;background:#fff}
th,td{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#e6edf7}
table.wide td,table.wide th{padding:2px 4px;font-size:.8em;text-align:center;white-space:nowrap}
table.wide td:nth-child(2){text-align:left}
pre{background:#eef1f6;padding:10px 14px;border-radius:6px;overflow-x:auto}
del{color:#999}
hr{border:0;border-top:1px solid #ccc;margin:28px 0}
p.meta{color:#666;font-size:.9em}
@media print{body{max-width:none;margin:0} h2{background:none;color:#000;border-bottom:2px solid #000;border-radius:0} li.task{background:none}}
"""


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"~~(.+?)~~", r"<del>\1</del>", s)
    s = re.sub(r"(https?://[^\s<)]+)", r'<a href="\1">\1</a>', s)
    return s


def render(md: str) -> str:
    out = []
    stack = []  # open <ul> indents
    table = []

    def close_lists(to_indent=-1):
        while stack and stack[-1] > to_indent:
            out.append("</ul>")
            stack.pop()

    def flush_table():
        if not table:
            return
        rows = [r for r in table if not re.match(r"^\s*\|?\s*:?-{3,}", r)]
        ncols = rows[0].count("|") - 1 if rows else 0
        out.append('<table class="wide">' if ncols > 10 else "<table>")
        for i, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
        out.append("</table>")
        table.clear()

    in_code = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            close_lists()
            flush_table()
            out.append("</pre>" if in_code else "<pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(raw, quote=False))
            continue
        if line.lstrip().startswith("|"):
            close_lists()
            table.append(line)
            continue
        flush_table()

        m = re.match(r"^(\s*)- (.*)$", line)
        if m:
            indent = len(m.group(1))
            body = m.group(2)
            if not stack or indent > stack[-1]:
                out.append("<ul>")
                stack.append(indent)
            else:
                close_lists(indent)
                if not stack or stack[-1] != indent:
                    out.append("<ul>")
                    stack.append(indent)
            t = re.match(r"^\[( |x|X)\] (.*)$", body)
            if t:
                done = t.group(1).lower() == "x"
                box = "&#9745;" if done else "&#9744;"
                cls = "task done" if done else "task"
                out.append(f'<li class="{cls}"><span class="box">{box}</span> <span class="label">{inline(t.group(2))}</span></li>')
            else:
                out.append(f"<li>{inline(body)}</li>")
            continue

        close_lists()
        if not line.strip():
            continue
        if line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.strip() == "---":
            out.append("<hr>")
        elif re.match(r"^\d+\.\s*$", line.strip()):
            out.append(f"<p>{line.strip()} ______________________________</p>")
        else:
            out.append(f"<p>{inline(line)}</p>")

    close_lists()
    flush_table()
    return "\n".join(out)


def main():
    body = render(MD.read_text(encoding="utf-8"))
    OUT.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>CSE340 Study Guide</title>"
        f"<style>{CSS}</style></head><body>{body}"
        "<p class='meta'>Generated from CSE340_Study_Guide.md — tick tasks with <code>python tracker.py done N</code> then rerun <code>python plan_html.py</code>.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    print(f"wrote {OUT}")
    if "--open" in sys.argv:
        webbrowser.open(OUT.as_uri())


if __name__ == "__main__":
    main()
