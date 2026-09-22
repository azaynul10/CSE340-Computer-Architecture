# CSE340 — Computer Architecture (RISC-V) · BRAC University

Coursework, worked problem sets, a graded research report, and small Python tools I built while taking
**CSE340 Computer Architecture** (Summer 2026, BRAC University). Everything here is my own work.
Faculty slides, exam papers, and the textbook are **not** redistributed — see [Resources](#resources) for links.

> **Instructor:** [Md. Zulkar Naim](https://cse.bracu.ac.bd/faculty_profile/461/md_zulkar_naim), Department of CSE, BRAC University
> **Textbook:** Patterson & Hennessy, *Computer Organization and Design — RISC-V Edition* (2nd ed.)
> **Scope:** Ch1 Performance · Ch2 RISC-V ISA · Ch3 Arithmetic & IEEE 754 · Ch4 Datapath, Control & Pipelining · Ch5 Memory Hierarchy

**Read the study guide online:** https://azaynul10.github.io/CSE340-Computer-Architecture/

---

## Repository structure

```
CSE340-Computer-Architecture/
├── README.md
├── resources.md                     Links only: faculty playlists by chapter, simulators, community drives
├── study-guide/                     Final-exam guide: worked solutions, derivation rules, 23-point self-check
│   ├── CSE340_Study_Guide.md        Source of truth — worked Mock Q2/Q3/Q4, PS4 Q4/Q13–16, format tables, checklist
│   ├── CSE340_Study_Guide.html      Rendered, self-contained; open in any browser
│   ├── plan_html.py                 Markdown → styled HTML renderer (tables, code, task checkboxes)
│   └── tracker.py                   CLI task tracker that reads/writes checkboxes in the Markdown plan
├── research-report/                 Graded 5/5 · "Scaling the Architecture of a Village Weather Station Over Time"
│   ├── weather-station-report-submitted.docx
│   ├── weather-station-report-draft.docx
│   ├── Q15_weather_station_MODEL.md                   (Markdown source + rubric notes)
│   └── build_docx.py                python-docx generator that enforces the submission format
├── assignments/                     Question sheets for all four problem sets + typed solutions where I have them
│   ├── A1-performance-and-isa/      A1-questions.pdf
│   ├── A2-riscv-assembly/           A2-questions.pdf
│   ├── A3-arithmetic-ieee754/       A3-questions.pdf
│   └── A4-datapath-and-pipelining/  A4-questions.pdf · Q4 pipeline forwarding · Q5 branch datapath
└── notes/                           Full-course notes, chapter by chapter
    ├── handwritten-notes-midterm.pdf        Ch1–3 (midterm syllabus)
    ├── handwritten-notes-full-course.pdf    Ch1–5
    ├── ch2-riscv-isa-notes.pdf
    ├── ch3-arithmetic-notes.pdf
    ├── ch3-arithmetic-worked-answers.pdf
    ├── ch4-datapath-pipelining-notes.pdf
    ├── datapaths-reference.pdf              Every datapath variant on one sheet each
    └── final-syllabus-notes.pdf             Ch2–Ch5 condensed for the final
```

Faculty slides, handouts, quiz/exam papers, practice sheets, the textbook and lecture transcripts live in a
separate private folder and are **never** committed.

---

## What's inside

### Problem sets (all graded 20/20)

| # | Topic | Highlights |
|---|---|---|
| A1 | Performance & ISA | CPI / clock-rate / execution-time comparisons; RISC-V register conventions |
| A2 | RISC-V assembly | C → RISC-V translation (if/else, loops, arrays); instruction encode/decode across R/I/S/SB/UJ |
| A3 | Arithmetic | −834.12×10⁴ → IEEE 754 single; multiply `0xC0F147AE × 0x42A43D71` step-by-step; range of a custom 22-bit FP format; reserved exponents; optimized (Booth-style) multiplier trace |
| A4 | Datapath & pipelining | Full single-cycle datapath with control for R-type/ld/sd/beq; hazard taxonomy and mitigations; stuck-at fault analysis (`ALUSrc=1`, `MemtoReg=0`) — which instructions survive; 5-instruction pipeline diagram with dependency and forwarding arrows |

### Research report — graded 5/5, 0% similarity, 0% AI-flag

**"Scaling the Architecture of a Village Weather Station Over Time"**
Redesign of an 8-bit AVR (16 MHz, 2 KB SRAM) sensor node that must absorb 10× sampling rate,
real-time storm alerting, BLE sync and an on-device display on a 100 mAh/day budget.

- Identified SRAM capacity and single-threaded control flow — not clock speed — as the binding constraints
  (512-byte SD block buffer = 25% of SRAM; 128×160×16bpp frame buffer = 40 KB = 20× total SRAM).
- Proposed migration to a 32-bit RISC-V MCU (ESP32-C3 class: 400 KB SRAM, I-cache, native BLE 5.0).
- Split the address space by timing requirement: deadline-critical ISR + sampling in deterministic on-chip
  SRAM; throughput-bound display/sync code executing from cached flash.
- Replaced the superloop with timer-ISR → SRAM ring buffer → page-aligned batched NOR-flash writes.
- Quantified the result from datasheet values: **~1740 mAh/day (naive) → ~3.3 mAh/day (redesign)**, a 99.8% reduction, with the backlight identified as the next optimisation target.
- 10 primary-source references (datasheets, SD/Bluetooth specs, P&H, FreeRTOS).

### Study guide with worked solutions

`study-guide/CSE340_Study_Guide.md` is written for anyone sitting the CSE340 final. It contains a one-page
"last look" summary, a syllabus-to-practice map, and full step-by-step solutions to the mock final, including:

- 5-stage pipeline hazard analysis of a 9-instruction sequence — dependency table, stall-only vs. forwarding grids, cycle counts, CPI.
- Why the Immediate Generator consumes the full 32-bit instruction (I/S/SB/UJ immediate bit layouts).
- Per-instruction datapath component usage; control-signal table (P&H Fig. 4.22) with XNOR-bug analysis.
- Cache address decomposition (tag/index/offset), hit/miss traces, write-through vs. write-back.
- RISC-V encode/decode recipes for every format, LUI+ADDI large-constant loading, branch offset arithmetic.
- Stuck-at control-signal fault analysis and the AND→XNOR branch-decision bug.
- A 23-item closed-book self-check (`python study-guide/tracker.py list`) and a gap log for timed mocks.

### Tools

| Script | What it does | Stack |
|---|---|---|
| `study-guide/plan_html.py` | Renders the Markdown study plan to a self-contained styled HTML page (headings, tables, fenced code, interactive checkboxes) | Python 3, stdlib `re`/`html` |
| `study-guide/tracker.py` | Terminal task tracker — `list`, `next`, `done N`, `undo N` — persists state back into the Markdown checkboxes | Python 3 |
| `research-report/build_docx.py` | Generates the report `.docx` with enforced formatting (Times New Roman 11, single column, single spacing, styled tables) | `python-docx` |

---

## Quick start

```bash
git clone https://github.com/azaynul10/CSE340-Computer-Architecture.git
cd CSE340-Computer-Architecture

# Render the study guide to HTML (writes study-guide/CSE340_Study_Guide.html; add --open to launch it)
python study-guide/plan_html.py

# Track tasks from the terminal
python study-guide/tracker.py list
python study-guide/tracker.py next
python study-guide/tracker.py done 3

# Rebuild the research report .docx
pip install python-docx
python research-report/build_docx.py
```

---

## Resources

See [`resources.md`](resources.md) — chapter-by-chapter faculty lecture playlists (PBK, RDW, NTB, MAO, HBN),
simulators, and community-shared drives. Links only; no copyrighted material is hosted in this repository.

---

## Academic integrity

Published **after** final grades were submitted. Solutions are for reference and self-checking.
If you are currently enrolled in CSE340, do the problems yourself first — the exams are closed-book and
timed, and reading a solution is not the same as being able to reproduce it under pressure.

## License

Original code and write-ups: MIT. Third-party materials are linked, not redistributed.

---

**Zaynul Abedin Miah** · B.Sc. CSE, BRAC University · [Portfolio](https://zaynul-abedin-miah.vercel.app/) · [LinkedIn](#) · [GitHub](#)
