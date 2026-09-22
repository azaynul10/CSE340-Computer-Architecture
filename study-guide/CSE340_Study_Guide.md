# CSE340 Final — Study Guide & Worked Solutions

**Exam format (recent semesters):** 4 questions · 50 marks scaled to 40 · ~110 minutes → budget **≈ 2 minutes per mark**. Bring a calculator, pencil, eraser, sharpener, pen, water, ID.
**Where the marks are (typical final):** Ch4 datapath + pipelining ≈ 25 · Ch2 RISC-V ISA ≈ 11 · Ch3 arithmetic ≈ 7–18 · Ch5 memory hierarchy ≈ 6–7. Prepare in that order.
**The one rule:** pen in hand for every lecture video. Draw, don't watch. Every 90-minute block should end with something you produced from a blank page.

Tick `[x]` in the checklist at the bottom as you go — `python tracker.py list` shows progress, `python plan_html.py` renders this file to HTML.

---

## Last look before the hall (read twice, 5 min)

**Order of attack:** the chapter you are surest of first (bank the marks) → the Ch4 question (most marks, most time) → Ch2 → Ch5. If stuck for more than 3 minutes, move on and come back.

**Datapath:** 9 boxes first (PC · Instr Mem · Registers · Imm Gen · ALU · Data Mem · Add+4 · Shift-left-1 · Add branch), 3 MUXes (ALUSrc, MemtoReg, PCSrc), then wire R-type → add `ld` → add `sd` → add `beq`. Label every bit range ([6:0] Control, [19:15] rs1, [24:20] rs2, [11:7] rd, [31:0] Imm Gen, [30,14:12] ALU control). For a code snippet: only the instruction types present.

**Control signals — 5 questions:** immediate as ALU input B? → ALUSrc · writes rd? → RegWrite · value from memory? → MemtoReg · touches memory? → MemRead/MemWrite · branch? → Branch. ALUOp 00 add / 01 sub / 10 funct. X when RegWrite = 0.

**Hazards:** source register → look *up* for the nearest writer → distance 1–2 = hazard, ≥3 safe. Stall-only: adjacent 2, distance-2 → 1, recheck after inserting stalls. Forwarding: ALU 0, load-use 1. Total = last WB cycle; CPI = cycles / instructions. Single-cycle = 0 hazards, CPI 1.

**Clock:** single-cycle = sum of stages; pipelined = slowest stage; n instructions = (n + 4 + stalls) × T.

**Imm Gen needs the whole instruction:** imm bits sit in different places for I (31:20), S (31:25 + 11:7), SB (scrambled) → must read the opcode, then sign-extend from bit 31.

**Decode:** hex → binary → opcode [6:0] → format → rd [11:7], funct3 [14:12], rs1 [19:15], rs2/imm. `0x00CB1A93` = `slli x21, x22, 12`.

**Ch2 traps:** `lw` offset is bytes, add in hex (0x1232 + 8 = 0x123A); loads the *value at* the address; carry x3 forward. Arrays: index × 8 (`slli 3`) for doublewords, × 4 for words. Invert the C condition to branch past the body. FP: `flw`/`fsw`, `.s` suffix, 4-byte offsets.

**Cache:** offset bits = log₂(block bytes), index bits = log₂(#blocks), tag = rest. 328 / 8 B / 32 B → tag 10, index 1, offset 0. Hierarchy = locality (temporal + spatial). Big blocks: lower miss *rate*, higher miss *penalty*, more conflicts. Write-through = every write to memory + write buffer; write-back = dirty bit, write on eviction. AMAT = hit time + miss rate × penalty.

**In the hall:** read every hint printed on the paper. Pencil for diagrams. Label before wiring.

---

## Syllabus → what to practise

| Chapter | Final syllabus | Practise | Check against |
|---|---|---|---|
| Ch2 | Instruction formats, encode/decode, C → assembly, addressing | Practice Sheet 2: Q1–4 (coding), Q8–9 (encode SB-type), Q10 (LUI + ADDI), Q12 (asm → C) | Faculty's Quiz 2 solve — a fully worked decode; copy its layout |
| Ch3 | IEEE 754, FP add/multiply, integer multiply/divide | Assignment 3 Q1–4 · Practice Sheet 3 | `notes/ch3-arithmetic-worked-answers.pdf` |
| Ch4 | Single-cycle datapath, control, pipelining, hazards | Practice Sheet 4: Q4–15 — every one, by hand | `notes/ch4-datapath-pipelining-notes.pdf`, `notes/datapaths-reference.pdf` |
| Ch5 | Memory hierarchy, direct-mapped cache, write policies | Practice Sheet 5 | PBK Ch5 handout (faculty explicitly say "read the handouts too") |
| Past papers | — | Mock Final, timed, in one sitting | Compare against the worked solutions below |

**Question formats announced → where they come from**

- **Datapath drawing** → Practice Sheet 4 Q5–12 (single instruction → two-instruction combined → BEQ→BNE modification → full datapath). A past final asked "design a datapath for BNE" = PS4 Q11 exactly.
- **Coding** → Practice Sheet 2 Q1–6 + FP code (Euclidean distance below).
- **Mathematical** → Ch3 conversions/arithmetic · Ch4 clock period + CPI · Ch5 tag/index/offset + AMAT.
- **Analytical** → PS4 Q13 (AND→XNOR bug), stuck-at control signals, why Imm Gen takes the whole instruction.
- **Scenario-based justification** → which FP format for a given precision, block-size trade-off, role of the offset.
- **True/False** → all chapters; **always write one reason line**, a bare T/F scores nothing.

**Using the lecture playlists** (links in `resources.md`)

- Ch4: watch the full playlist once, then never again — every further mark comes from drawing. Lecture 16 (the full single-cycle datapath, P&H Fig 4.17) is the one to redraw from.
- Ch2: skip the basics if you passed the midterm; go straight to the format/encoding lectures, then Practice Sheet 2.
- Ch5: the tag/index/offset lecture is the essential one; the simulation lectures can be skipped.
- Ch3: problems only; the videos add little over the handout once you can do one conversion end to end.

---

## Control-signal table (P&H Fig 4.22 — the slides only have it as a picture)

| Instr | ALUSrc | MemtoReg | RegWrite | MemRead | MemWrite | Branch | ALUOp |
|---|---|---|---|---|---|---|---|
| R-type | 0 | 0 | 1 | 0 | 0 | 0 | 10 |
| `ld`   | 1 | 1 | 1 | 1 | 0 | 0 | 00 |
| `sd`   | 1 | X | 0 | 0 | 1 | 0 | 00 |
| `beq`  | 0 | X | 0 | 0 | 0 | 1 | 01 |
| `addi` (I-type ALU) | 1 | 0 | 1 | 0 | 0 | 0 | 10 (funct3 decides) |

How to derive any row without memorising:
- **ALUSrc** = 1 whenever the ALU's second input is an immediate (`ld`, `sd`, `addi`); 0 when it's a register (R-type, `beq`)
- **RegWrite** = 1 only if the instruction produces a value in `rd` (R-type, `ld`, `addi`); `sd`/`beq` have no `rd` → 0
- **MemtoReg** = 1 only for `ld` (the written value comes from memory). X (don't care) when RegWrite=0
- **MemRead** = 1 only for `ld`; **MemWrite** = 1 only for `sd`
- **Branch** = 1 only for `beq`/`bne`
- **ALUOp**: 00 = add (address calc for `ld`/`sd`), 01 = subtract (compare for `beq`), 10 = look at funct3/funct7 (R-type / I-type ALU)
- `bne` row = `beq` row; the datapath differs (Zero inverted), not the signals

**Worked:** `bne x3, x4, Else` → RegWrite=0 (no rd), MemRead=0, MemWrite=0 (no memory), ALUSrc=0 (compares two registers), Branch=1, MemtoReg=X (nothing is written). Say *why* for each — that is where the marks are.

---

## How to build any datapath (the method, not the figure)

Never start from the full figure.

1. Read the instruction.
2. Ask: *where do I read? where do I write?*
3. Pick only the components that answer those two questions.
4. Connect them left → right, one wire at a time, asking "what happens next?".
5. For a code snippet, take the **union** of the datapaths of every instruction type present.

**Exam pattern:** "`add`, `sub`, `addi` — design a datapath" = R-type + I-type only (ALUSrc MUX, no Data Mem, no branch adder). "`add`, `addi`, `sd`, `beq`" = the full figure. Identify the types first, then draw only what they need.

**Practice ladder:** draw `ld`, `sd`, R-type, `beq` on one sheet each with every component labelled (64-bit data, 5-bit register numbers, 12-bit imm → 64) → then the **full** single-cycle datapath from a blank page, timed, target under 8 minutes → circle your misses against Fig 4.17 → draw again from blank.

---

## Pipeline timing — worked example

Stage latencies **IF 260 / ID 220 / EX 260 / MEM 200 / WB 220 ps**.

- Single-cycle: one instruction must pass through *all five* stages inside one clock → T = 260 + 220 + 260 + 200 + 220 = **1160 ps**
- Pipelined: every stage gets the same clock, so the clock must fit the *slowest* stage → T = max(260, 220, 260, 200, 220) = **260 ps** (add register overhead only if the question gives one)
- Ideal speedup = 1160 / 260 = **4.46×**, not 5× — stages are unbalanced, so four of them idle part of each cycle
- n = 5 instructions, no hazards: single-cycle 5 × 1160 = 5800 ps; pipelined (5 + 4) × 260 = 2340 ps. Each stall adds one more 260 ps cycle
- "Which stage to shorten?" — only cutting the *longest* stage(s) reduces the pipelined clock; shortening MEM from 200 → 150 changes nothing

**Hazard conventions used in this course** (match these exactly in the exam):

- Hazard check: for each instruction, take its *source* operands and look **upward** for a line where that register is the **destination**. Using a register is not a hazard; writing it is
- Register file writes in the **first half** of a cycle, reads in the **second half** → the consumer's ID may sit in the **same cycle** as the producer's WB
- **Stall-only:** adjacent dependent → **2 stalls** (ALU and load producers alike); one independent instruction between → 1 stall; two between → 0. Mark stalls as bubbles or crosses
- **Forwarding only:** ALU producer → **0 stalls** (EX→EX); load producer → **1 stall** (value exists only after MEM)
- **Stall + forward:** forward first; add a stall only where forwarding cannot (load-use). It does *not* mean two stalls
- Total cycles = last instruction's WB cycle number. CPI = total cycles / #instructions

---

## Worked: hazards on a 9-instruction sequence (Mock Final Q3b)

Attempt it first, then compare.

```
1  ld   x10, 32(x11)      writes x10
2  add  x5,  x10, x7      writes x5
3  addi x5,  x5,  3       writes x5
4  ld   x13, 48(x5)       writes x13
5  sd   x13, 32(x5)       writes nothing (store)
6  add  x5,  x13, x5      writes x5
7  sub  x6,  x12, x5      writes x6
8  sw   x5,  12(x13)      writes nothing (store)
9  sll  x16, x6,  x5      writes x16
```

**Step 1 — dependency table** (for each source register look *upward* to the nearest line that *writes* it; distance = how many lines apart)

| Consumer | Source | Nearest producer | Distance | Producer type | Hazard in pipeline? |
|---|---|---|---|---|---|
| 2 `add` | x10 | 1 `ld` | 1 | load | yes |
| 3 `addi` | x5 | 2 `add` | 1 | ALU | yes |
| 4 `ld` | x5 | 3 `addi` | 1 | ALU | yes |
| 5 `sd` | x13 | 4 `ld` | 1 | load | yes |
| 5 `sd` | x5 | 3 `addi` | 2 | ALU | yes |
| 6 `add` | x13 | 4 `ld` | 2 | load | yes |
| 6 `add` | x5 | 3 `addi` | 3 | ALU | **no** — WB of 3 and ID of 6 share a cycle (write first half, read second half) |
| 7 `sub` | x5 | 6 `add` | 1 | ALU | yes |
| 8 `sw` | x5 | 6 `add` | 2 | ALU | yes |
| 8 `sw` | x13 | 4 `ld` | 4 | load | no |
| 9 `sll` | x6 | 7 `sub` | 2 | ALU | yes |
| 9 `sll` | x5 | 6 `add` | 3 | ALU | no |

Rule of thumb: distance 1 or 2 → hazard; distance ≥ 3 → safe (producer WB = cycle k+4, consumer ID = cycle k+d+1; equal when d = 3).

**i. Single-cycle:** 9 instructions → **9 cycles**, CPI = 9/9 = **1**.

**ii. Hazards in single-cycle:** **0**. Each instruction finishes (including its register write) before the next one starts, so a later read can never see a stale value.

**iii. Hazards in pipelined:** **9 RAW data hazards** (the "yes" rows above), affecting 8 of the 9 instructions (every instruction except the first). State both numbers; markers check operand by operand.

**iv. Stall-only** — consumer's ID must land in the same cycle as the producer's WB → adjacent dependents get **2 stalls**, distance-2 gets **1**, distance ≥ 3 gets 0. Mark each stall as `x` (bubble) before the IF.

| # | Instr | stalls | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `ld x10,32(x11)` | 0 | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | `add x5,x10,x7` | 2 |  | x | x | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | `addi x5,x5,3` | 2 |  |  |  |  | x | x | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | `ld x13,48(x5)` | 2 |  |  |  |  |  |  |  | x | x | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |  |  |  |
| 5 | `sd x13,32(x5)` | 2 |  |  |  |  |  |  |  |  |  |  | x | x | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |
| 6 | `add x5,x13,x5` | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  | IF | ID | EX | MEM | WB |  |  |  |  |  |  |
| 7 | `sub x6,x12,x5` | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | x | x | IF | ID | EX | MEM | WB |  |  |  |
| 8 | `sw x5,12(x13)` | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | IF | ID | EX | MEM | WB |  |  |
| 9 | `sll x16,x6,x5` | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | x | IF | ID | EX | MEM | WB |

Why 6 and 8 need 0 stalls: the stalls already inserted for 5 (and 7) pushed them far enough that their producer's WB has happened by their ID. Always re-check distance *after* earlier stalls, not from the original listing.

Total = last WB = **24 cycles**. Stalls = 2+2+2+2+0+2+0+1 = 11 (check: 9 + 4 + 11 = 24). **CPI = 24/9 = 2.67**.

**v. Forwarding only** — ALU result forwarded EX→EX: **0 stalls**. Load result exists only after MEM, so a load followed *immediately* by its user still needs **1 stall** (load-use). Distance-2 load-use (6 ← 4) needs none.

| # | Instr | stalls | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `ld x10,32(x11)` | 0 | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |  |  |  |
| 2 | `add x5,x10,x7` | 1 |  | x | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |  |
| 3 | `addi x5,x5,3` | 0 |  |  |  | IF | ID | EX | MEM | WB |  |  |  |  |  |  |  |
| 4 | `ld x13,48(x5)` | 0 |  |  |  |  | IF | ID | EX | MEM | WB |  |  |  |  |  |  |
| 5 | `sd x13,32(x5)` | 1 |  |  |  |  |  | x | IF | ID | EX | MEM | WB |  |  |  |  |
| 6 | `add x5,x13,x5` | 0 |  |  |  |  |  |  |  | IF | ID | EX | MEM | WB |  |  |  |
| 7 | `sub x6,x12,x5` | 0 |  |  |  |  |  |  |  |  | IF | ID | EX | MEM | WB |  |  |
| 8 | `sw x5,12(x13)` | 0 |  |  |  |  |  |  |  |  |  | IF | ID | EX | MEM | WB |  |
| 9 | `sll x16,x6,x5` | 0 |  |  |  |  |  |  |  |  |  |  | IF | ID | EX | MEM | WB |

Draw forwarding arrows: 1.MEM→2.EX (load), 2.EX→3.EX, 3.EX→4.EX, 4.MEM→5.EX, 3.MEM→5.EX (x5), 4.MEM→6.EX (x13, no stall needed at distance 2), 6.EX→7.EX, 6.MEM→8.EX, 7.MEM→9.EX.

Total = **15 cycles**, stalls = 2 (both load-use). **CPI = 15/9 = 1.67**.

**vi.** Summary after each method: stall-only **24 cycles, CPI 2.67**; forwarding **15 cycles, CPI 1.67**. If the question wording is ambiguous about which method it means, write both and label them.

Exam layout that scores: the dependency table first (it *is* the answer to ii/iii), then each grid with the stall-count column, then one line of arithmetic per total. Pencil the grid — a wrong bubble costs more to erase in pen.

---

## Why Imm Gen takes the whole instruction (Mock Final Q3a, 2 marks)

The 12 immediate bits are **not in a fixed position** — it depends on the format:

| Format | Example | Where the immediate bits are |
|---|---|---|
| I-type | `ld`, `addi` | imm[11:0] = bits 31:20, contiguous |
| S-type | `sd` | imm[11:5] = bits 31:25, imm[4:0] = bits 11:7 (rs2 sits in between) |
| SB-type | `beq` | imm[12] = bit 31, imm[10:5] = 30:25, imm[4:1] = 11:8, imm[11] = bit 7 |

So Imm Gen must read the **opcode (bits 6:0)** to know the format, pick the right bits, reassemble them, and **sign-extend** from bit 31 to 64 bits. A fixed 12-bit slice would be wrong for S and SB types → the datapath feeds `Instruction[31:0]` into Imm Gen.

Two-sentence version for the paper: *"The immediate field is located in different bit positions for I-, S- and SB-type instructions (contiguous in 31:20 for I-type, split across 31:25 and 11:7 for S-type, scrambled for SB-type). Imm Gen must read the opcode to identify the format, select and reorder the correct bits, and sign-extend them to 64 bits — so it needs the entire instruction."*

---

## Which components each instruction needs (Practice Sheet 4 Q4)

**Used by every instruction:** PC, PC+4 adder, Instruction Memory, and the PC-source MUX (selects PC+4 unless a branch is taken). Only list the *extra* components per row.

| Instr | Reg read | Imm Gen | ALU | Data Mem | Reg write | Branch adder + PC MUX |
|---|---|---|---|---|---|---|
| R-type (`add`, `sub`, `and`, `or`) | rs1, rs2 | — | yes (funct decides op) | — | yes (rd) | — |
| `addi` (I-type ALU) | rs1 | yes | yes | — | yes (rd) | — |
| `ld` | rs1 | yes | yes (add — address) | read | yes (rd) | — |
| `sd` | rs1, rs2 | yes | yes (add — address) | write | — | — |
| `beq` / `bne` | rs1, rs2 | yes | yes (subtract — compare) | — | — | yes |

Derivation rules — do not memorise the table:
- **Instr Memory + PC + PC+4 adder** — every instruction, always. Say this once, then stop repeating it per row
- **Reg File read port 2 (rs2)** — only when rs2 is a real operand: R-type, `sd`, branches
- **Imm Gen** — only when the format carries an immediate field: I, S, SB
- **ALU** — every instruction: arithmetic (R / I), address calculation (`ld` / `sd`), or comparison (branches)
- **Data Memory** — only `ld` (read) and `sd` (write)
- **Reg File write port** — only when the instruction has an `rd`: R-type, I-type ALU, `ld`. No `rd` → no write (`sd`, branches)
- **Branch adder + PC MUX** — branches only
- For a **code snippet**, take the union of the components of every instruction type present

---

## AND gate replaced by XNOR in the branch decision (Practice Sheet 4 Q13)

The correct datapath computes `PCSrc = Branch AND Zero`. The bug makes it `PCSrc = XNOR(Branch, Zero)`, which is 1 whenever the two inputs are **equal**.

| Branch | Zero | AND (correct) | XNOR (buggy) |
|---|---|---|---|
| 0 | 0 | 0 | **1 ← the only row that changes** |
| 0 | 1 | 0 | 0 |
| 1 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 |

**i. `SUB x1, x2, x3`** — Branch = 0, and Zero = 1 only if x2 == x3
- x2 ≠ x3 → Zero = 0 → XNOR(0,0) = **1** → PC loads the branch target instead of PC+4. A non-branch instruction takes a branch
- The target is garbage: Imm Gen reads an SB-type immediate out of a SUB instruction's funct7/rs2 bits, so the jump lands at an arbitrary address
- The subtraction still completes correctly — x1 receives x2 − x3, since the RegWrite path is untouched. **Only control flow breaks**
- x2 == x3 → Zero = 1 → XNOR(0,1) = 0 → PC+4, correct by luck

**ii. `BEQ x1, x2, target`** — Branch = 1
- XNOR(1, Zero) = Zero, and AND(1, Zero) = Zero → **identical**. BEQ is completely unaffected and still branches exactly when x1 == x2

One-line answer: the bug never affects branches — it corrupts the PC of *every non-branch instruction whose ALU result is non-zero* (which includes `ld`/`sd`, whose ALU output is an address).

---

## Control bits for a given instruction (Practice Sheet 4 Q14–Q16)

| Question | Instruction | Branch | MemWrite | RegWrite | ALUSrc |
|---|---|---|---|---|---|
| Q14 | `Add X21, X22, X23` | 0 | 0 | 1 | 0 |
| Q15 | `Addi X21, X22, 12` | 0 | 0 | 1 | **1** |

- **Q14** R-type: not a branch, no memory write, writes `rd` = x21, second ALU operand is register x23 → ALUSrc 0
- **Q15** Only ALUSrc changes — the second ALU operand is now the immediate 12. Everything else is identical to Q14
- **Q16** asks the same for `Add X21, X22, X23` but swaps in MemToReg: Branch 0 · ALUSrc 0 · RegWrite 1 · **MemToReg 0** (the written value comes from the ALU, not from memory)

---

## Stuck-at faults (Assignment 4 Q3 pattern)

Method: for each instruction type, read the correct control row above, then ask whether the stuck value *happens to equal* the correct value.

- **`ALUSrc` stuck at 1** (ALU input B is always the immediate): `ld`, `sd`, `addi` need 1 anyway → **still correct**. R-type and `beq` need 0 → the ALU adds/compares against a garbage immediate → **fail**.
- **`MemtoReg` stuck at 0** (register write data always comes from the ALU): R-type and `addi` need 0 → **still correct**. `ld` needs 1 → rd receives the *address* instead of the loaded value → **fail**. `sd`/`beq` don't write a register (X) → **unaffected**.
- Combine: an instruction survives only if it survives *every* stuck signal. Here only `addi` survives both.

---

## Ch2 — branch translation patterns

P&H register convention: `f`=x19, `g`=x20, `h`=x21, `i`=x22, `j`=x23, `k`=x24, `save[]` base = x25.

**`if (i == j) f = g + h;`**
- `bne x22, x23, Exit` — branch on the *opposite* condition to skip the body
- `add x19, x20, x21`
- `Exit:`

**`if (i == j) f = g + h; else f = g - h;`**
- `bne x22, x23, Else`
- `add x19, x20, x21`
- `beq x0, x0, Exit` — unconditional jump idiom, since x0 always equals x0
- `Else:`
- `sub x19, x20, x21`
- `Exit:`

**`while (save[i] == k) i += 1;`**
- `Loop: slli x10, x22, 3` — i × 8, because doublewords are 8 bytes
- `add x10, x10, x25` — address of `save[i]`
- `ld x9, 0(x10)`
- `bne x9, x24, Exit` — leave the loop as soon as the test fails
- `addi x22, x22, 1`
- `beq x0, x0, Loop`
- `Exit:`

Three rules generate all of the above:
- **Invert the C condition** to branch *past* the body (`==` → `bne`, `<` → `bge`)
- `beq x0, x0, L` = unconditional branch (`jal x0, L` is also accepted)
- **Index → byte offset:** shift left 3 for doublewords (`ld`/`sd`), left 2 for words (`lw`/`sw`)

---

## Ch2 — the 5 instruction formats (write this once from memory)

Bits run 31 (left) → 0 (right). Opcode is always bits 6:0; rd 11:7; funct3 14:12; rs1 19:15; rs2 24:20.

| Format | 31:25 | 24:20 | 19:15 | 14:12 | 11:7 | 6:0 | Used by |
|---|---|---|---|---|---|---|---|
| **R** | funct7 | rs2 | rs1 | funct3 | rd | opcode `0110011` | `add sub and or sll` |
| **I** | imm[11:0] (all of 31:20) | | rs1 | funct3 | rd | `0000011` loads · `0010011` ALU-imm | `ld lw addi slli srli ori` |
| **S** | imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | `0100011` | `sd sw sh sb` |
| **SB** | imm[12] imm[10:5] | rs2 | rs1 | funct3 | imm[4:1] imm[11] | `1100011` | `beq bne blt bge` |
| **UJ** | imm[20] imm[10:1] imm[11] imm[19:12] (all of 31:12) | | | | rd | `1101111` | `jal` |

- `slli`/`srli` (RV64): bits 31:26 = funct6 `000000`, bits 25:20 = 6-bit shamt; funct3 001 = slli, 101 = srli. If the exam paper prints its own opcode table, use that one
- SB immediate is in **bytes**, always even, so bit 0 is implied and not stored → 13-bit range ±4 KB. Offset = (target address − branch address)
- Sign-extension: bit 31 is always the sign bit of the immediate in I / S / SB / UJ

**Decode recipe (`0x00CB1A93`)**

```
hex   0    0    C    B    1    A    9    3
bin   0000 0000 1100 1011 0001 1010 1001 0011
bits  31                                     0

opcode  [6:0]   = 0010011  -> I-type ALU-immediate
rd      [11:7]  = 10101    = x21
funct3  [14:12] = 001      -> SLLI
rs1     [19:15] = 10110    = x22
imm     [31:20] = 000000001100 = 12   (shamt = 12, funct6 = 000000)

answer: slli x21, x22, 12      (x21 = x22 << 12  = x22 * 4096)
```

Verify any decode at https://luplab.gitlab.io/rvcodecjs/ — but only *after* doing it by hand.

Datapath for that instruction: I-type ALU path — PC → Instr Mem → rs1 to Read reg 1; Instr[31:0] → Imm Gen → MUX(ALUSrc=1) → ALU; ALU result → MUX(MemtoReg=0) → Write data; rd = x21, RegWrite=1, MemRead=0, MemWrite=0, Branch=0, ALUOp=10 (ALU control reads funct3 → shift left). No Data Memory, no branch adder needed.

**Encode recipe (Practice Sheet 2 Q9 SB-type, Q10 LUI+ADDI)**
- SB: offset = target − PC of the branch (bytes). Write it as a 13-bit two's-complement number, drop bit 0, then scatter: bit12 → 31, bits10:5 → 30:25, bits4:1 → 11:8, bit11 → 7. Example `beq x9, x24, +16`: imm = 0000000010000 → [31]=0, [30:25]=000000, [11:8]=1000, [7]=0
- 32-bit constant in one register: `lui rd, upper20` then `addi rd, rd, lower12`. If lower12 ≥ 0x800 (negative as 12-bit) add 1 to upper20 first. Example 0x003D0500: `lui x19, 0x003D` ; `addi x19, x19, 0x500`

---

## Ch2 — register trace with x1 = 0x00001232, x2 = 1024 (Mock Final Q2a pattern)

```
x1 = 0x1232 = 0001 0010 0011 0010 (binary) = 4658 (decimal)
x2 = 1024   = 0x400 = 0000 0100 0000 0000
```

| Operation | Result (hex) | Result (decimal) | How |
|---|---|---|---|
| `slli x3, x1, 2` | 0x48C8 | 18632 | shift left = ×4 |
| `srli x3, x1, 2` | 0x48C | 1164 | shift right = ÷4, floor |
| `and x3, x1, x2` | 0x0 | 0 | 0x1232 has bit 10 clear |
| `or x3, x1, x2` | 0x1632 | 5682 | sets bit 10 |
| `xor x3, x1, x2` | 0x1632 | 5682 | same here because AND was 0 |
| `add x3, x1, x2` | 0x1632 | 5682 | 4658 + 1024 |
| `sub x3, x1, x2` | 0xE32 | 3634 | 4658 − 1024 |
| `addi x3, x1, -100` | 0x11CE | 4558 | negative imm is fine |
| `andi x3, x1, 0xFF` | 0x32 | 50 | keeps low byte |

Rules: shift n = ×/÷ 2ⁿ · write both operands in binary under each other for AND/OR/XOR · if the table asks for **decimal**, convert at the end · show every line of working.

---

## Ch2 — FP Euclidean distance (Mock Final Q2c, 3 marks)

`a2, a1, b2, b1` are 4-byte floats at x23+0, +4, +8, +12. Result to f15, then to memory at x14.

```
flw   f1, 0(x23)        # a2
flw   f2, 4(x23)        # a1
flw   f3, 8(x23)        # b2
flw   f4, 12(x23)       # b1
fsub.s f5, f1, f2       # a2 - a1
fsub.s f6, f3, f4       # b2 - b1
fmul.s f5, f5, f5       # (a2 - a1)^2
fmul.s f6, f6, f6       # (b2 - b1)^2
fadd.s f15, f5, f6      # sum
fsqrt.s f15, f15        # D = sqrt(sum)
fsw   f15, 0(x14)       # store D
```

Marks come from: `flw`/`fsw` (not `lw`), 4-byte offsets, `.s` suffix, `fsqrt.s`, final store. Comment every line.

---

## Ch2 — offset in base + displacement addressing (Mock Final Q2d, 2 marks)

- Address = **base register + 12-bit signed offset**, e.g. `ld x5, 16(x10)` reads from x10 + 16
- **Role:** the offset selects a specific element/field relative to a base — the 3rd doubleword of an array is `16(x10)`, a struct field at byte 24 is `24(x10)` — without changing the base register
- **Benefits:** one base register serves a whole array/struct (fewer registers, no extra `add` to compute each address); the constant is inside the instruction so no extra memory access; ±2 KB reach is enough for most locals/fields; makes loops simple (bump the base, keep the offsets)

---

## Ch5 — cache (Mock Final Q4, 6–7 marks)

**a. Offset field (1):** picks the **byte (or word) inside the block**. Block size 8 B → 3 offset bits. Address 328 = …001 000 → offset 000 = first byte of its block; address 331 → offset 011 = 4th byte of the same block, same cache line, a hit if 328 was fetched.

**b. Why a memory hierarchy (2):** fast memory (SRAM) is expensive and small; large memory (DRAM/disk) is slow and cheap. Programs show **temporal locality** (reuse recent data — loop variables) and **spatial locality** (use neighbours — arrays, sequential code), so a small fast cache holding the recently used blocks serves most accesses at cache speed while capacity comes from the cheap levels below → the illusion of a large *and* fast memory at low cost.

**c. Address 328, block 8 B, cache 32 B (1):** #blocks = 32 / 8 = 4 → index bits = log₂ 4 = **2**; offset bits = log₂ 8 = **3**; tag = the rest.
```
328 = 1 0100 1000
      tag  |idx|off
      1010 | 01 | 000      tag = 10, index = 1, offset = 0
```
(If the paper says "bits" where it means bytes, state "assuming bytes" and proceed — same method for words.)

**d. "Large cache line minimises miss penalty" (2) — FALSE.** Larger blocks *reduce the miss rate* (spatial locality) up to a point, but the **miss penalty grows** because more bytes must be transferred from memory on every miss. Also, for a fixed cache size, fewer blocks → more conflict misses, and past a point the miss rate rises again. Example: 32 B blocks vs 128 B blocks in a 4 KB cache — the 128 B version fetches 4× the data per miss (longer penalty) and has only 32 lines instead of 128. Correct statement: large lines lower miss *rate*, not miss *penalty*.

**e. Write-through vs write-back (1):**

| | Write-through | Write-back |
|---|---|---|
| On a write hit | update cache **and** memory immediately | update cache only, mark block **dirty** |
| Memory updated | every write | when the dirty block is evicted |
| Speed | slower (memory traffic per write) — needs a **write buffer** | faster, less traffic |
| Complexity | simple, memory always consistent | dirty bit, eviction write-back, harder coherence |
| Example | `sd` to x[0] in a loop of 100 iterations → 100 memory writes | same loop → 1 memory write at eviction |

**Hit/miss trace — method:** direct-mapped, 16 one-word blocks → index = block address mod 16. Track a 16-row table (valid, tag). Address sequence 22, 26, 22, 26, 16, 3, 16, 18:

| Access | Index (mod 16) | Tag (addr ÷ 16) | Result |
|---|---|---|---|
| 22 | 6 | 1 | miss (cold) |
| 26 | 10 | 1 | miss |
| 22 | 6 | 1 | **hit** |
| 26 | 10 | 1 | **hit** |
| 16 | 0 | 1 | miss |
| 3 | 3 | 0 | miss |
| 16 | 0 | 1 | **hit** |
| 18 | 2 | 1 | miss |

Hit rate 3/8. **AMAT = hit time + miss rate × miss penalty**, e.g. 1 + 0.625 × 100 = 63.5 cycles. If block size > 1 word, first divide the address by words-per-block to get the block address, then index = block address mod #blocks.

---

## Self-check — can you do each of these from a blank page, closed-book?

Tick only when you have actually done it, not when you understand it. `python tracker.py done N` updates this file.

- [ ] Ch4: draw the full single-cycle datapath with control (R-type, `ld`, `sd`, `beq`) in under 8 minutes, every bit range labelled
- [ ] Ch4: draw the datapath for a 3-instruction snippet containing only the components those instructions need
- [ ] Ch4: modify the BEQ datapath into BNE and explain the one change
- [ ] Ch4: write the control-signal table for R / `ld` / `sd` / `beq` / `addi` from the derivation rules, then justify each 0/1/X in one line
- [ ] Ch4: given 5 stage latencies, compute single-cycle period, pipelined period, speedup, and time for n instructions
- [ ] Ch4: build a dependency table for a 6–9 instruction sequence and count hazards
- [ ] Ch4: draw the stall-only grid and the forwarding grid, compute total cycles and CPI for both
- [ ] Ch4: explain why Imm Gen needs all 32 instruction bits
- [ ] Ch4: analyse a stuck-at control signal — which instructions survive, which fail, and why
- [ ] Ch2: write the 5 instruction formats with bit positions from memory
- [ ] Ch2: decode a 32-bit hex instruction to assembly by hand
- [ ] Ch2: encode an SB-type branch with a PC-relative offset; load a 32-bit constant with LUI + ADDI
- [ ] Ch2: translate an if/else and a while loop over an array to RISC-V with the correct shift for the element size
- [ ] Ch2: trace shifts / and / or / xor / add / sub on given register values in hex and decimal
- [ ] Ch2: write FP code with `flw` / `fsw`, `.s` arithmetic and 4-byte offsets
- [ ] Ch3: convert a decimal to IEEE 754 single precision and back; state bias, exponent range, and the special values
- [ ] Ch3: multiply two IEEE 754 numbers showing sign, exponent (E1 + E2 − bias) and normalised significand
- [ ] Ch3: trace the optimised multiplier for two 4-bit operands step by step
- [ ] Ch5: split an address into tag / index / offset for a given block size and cache size
- [ ] Ch5: run a hit/miss trace on a direct-mapped cache and compute hit rate and AMAT
- [ ] Ch5: argue the block-size trade-off and write-through vs write-back with one concrete example each
- [ ] Ch1: compute CPU time = IC × CPI × T and apply Amdahl's law to a proposed improvement
- [ ] Do the Mock Final in one timed sitting and list every sub-question you got wrong below

---

## Gap log — every sub-question you got wrong in a timed mock

Re-solve each one from blank the next day. Cross it out only when you get it right twice.

1.
2.
3.
4.
5.
