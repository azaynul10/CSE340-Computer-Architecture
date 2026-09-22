# Scaling the Architecture of a Village Weather Station Over Time

**Problem 15** — assigned as (student ID mod 20) + 1
Target format: Times New Roman 11, single column, single spacing, **max 2 pages excluding References**.

---

## Introduction

A weather station built for a rural school is a useful lens on architectural scaling because
its constraints are absolute rather than negotiable: a fixed energy envelope, a fixed budget,
and no technician to service it. The original deployment logs two sensors once per hour on an
8-bit microcontroller with 2 KB of SRAM. Two years later the community wants ten times the
sampling rate, real-time storm alerting, monthly Bluetooth synchronisation, and an on-device
chart display, all on the same power budget. This report argues that these requests cannot be
met by adding features to the existing design, because the limiting resources are SRAM
capacity and the single-threaded control flow rather than clock speed. It then proposes a
revised memory hierarchy and concurrency model, and quantifies the result against a 100 mAh
per day budget.

## Background and Related Work

The original platform is a classic 8-bit AVR-class device: 16 MHz, 2 KB SRAM, 32 KB flash, no
cache, and no operating system (Microchip, 2016). Memory is flat and uniformly accessed, so
every load takes a fixed number of cycles. Patterson and Hennessy (2021, ch. 5) frame the
memory hierarchy as a trade of capacity against latency, exploiting temporal and spatial
locality to approximate the speed of the fastest level at the cost of the largest. A
microcontroller of this class sits at a degenerate point in that hierarchy: there is only one
level, so there is no locality to exploit and, equally, no cache-miss variability. The result
is complete timing determinism, which is why such parts remain common in control loops.

Three documented facts about the requested features determine what breaks. First, the SD card
interface is block-oriented: the physical layer specification fixes a 512-byte block as the
unit of transfer (SD Association, 2010), so any driver must hold a 512-byte buffer, which is
25% of the available SRAM before application code exists. Second, a 1.8-inch display of the
common ST7735 class has a 128 × 160 pixel matrix at 16 bits per pixel (Sitronix, 2011). A full
frame buffer is therefore 128 × 160 × 2 = 40 KB, twenty times the entire SRAM of the original
part. Even a one-bit-per-pixel monochrome buffer needs 2.5 KB and still does not fit. Third,
Bluetooth Classic modules of the HC-05 class draw tens of milliamperes continuously while
connectable, whereas Bluetooth Low Energy is designed around short connection events with
microampere idle current (Bluetooth SIG, 2019).

Prior work on energy-constrained sensing converges on the same two strategies. Duty cycling
with aggressive sleep states is standard practice, since leakage-dominated sleep currents are
three to four orders of magnitude below active current (Microchip, 2016; Espressif, 2023).
Batching writes is the second: NOR flash is programmed in pages and erased in sectors with a
finite endurance of roughly 100,000 cycles per sector (Winbond, 2021), so aggregating small
records into one page-aligned write reduces both energy per byte and wear. This is the same
spatial-locality argument that motivates cache line fills in Patterson and Hennessy (2021,
ch. 5), applied to a non-volatile level of the hierarchy. Finally, the concurrency literature
treats a blocking write inside a single-threaded loop as a latency hazard; decoupling
producers from consumers through a ring buffer, or scheduling them as separate priority tasks
under a small real-time kernel, is the conventional remedy (Barry, 2016; Patterson &
Hennessy, 2021, ch. 6).

## Methodology and System Design

**Step 1 — establish where the original design fails.** Table 1 costs the naive approach of
attaching the new peripherals to the existing superloop.

*Table 1: Daily energy cost of adding features without architectural change*

| Component | Assumption | mAh/day |
|---|---|---|
| MCU active continuously, no sleep | 12 mA × 24 h | 288 |
| Bluetooth Classic module always connectable | 30 mA × 24 h | 720 |
| Display and backlight always on | 30 mA × 24 h | 720 |
| SD card idle current plus 240 writes | ~0.5 mA average | 12 |
| **Total** | | **~1740** |

Against a 100 mAh per day budget this is roughly seventeen times over. The memory position is
worse, and is not a matter of degree: the 512-byte SD buffer, a serial receive buffer, and any
display buffer cannot coexist in 2 KB, and the 40 KB frame buffer is impossible by a factor of
twenty. Sampling every six minutes also produces 240 records per day, which at even five bytes
per record is 1200 bytes of buffering, leaving too little headroom for the SD driver. These are
hard walls, so the correct conclusion is that the platform must change.

**Step 2 — choose a processor class and memory hierarchy.** I select a 32-bit RISC-V
microcontroller with an integrated 2.4 GHz radio, of the ESP32-C3 class: 400 KB of on-chip
SRAM, 384 KB of ROM, an instruction cache for execution from external flash, native Bluetooth
Low Energy 5.0, and a deep-sleep current in the single-digit microamperes (Espressif, 2023).
This resolves all three memory walls at once and removes the external Bluetooth module.
Choosing RISC-V also keeps the instruction-set model consistent with the course reference.

The cache deserves explicit treatment, because it introduces the trade-off that Patterson and
Hennessy (2021, ch. 5) describe. Executing from external flash at high clock rates requires an
instruction cache to hide flash latency, but a cache miss makes execution time variable, and
variable latency is precisely what a storm-alert path must not have. The design therefore
splits the address space by requirement: the alert interrupt handler and the sampling routine
are placed in on-chip SRAM so their timing is deterministic, while the display rendering and
synchronisation code, which are throughput-oriented and not deadline-bound, execute from
cached flash. This is a deliberate use of the hierarchy rather than an acceptance of its
defaults.

**Step 3 — restructure control flow.** The superloop is replaced by three cooperating elements.
A hardware timer interrupt samples the sensors and writes fixed-size records into an SRAM ring
buffer, so acquisition cannot be delayed by any slower activity. A low-priority task drains the
ring buffer to NOR flash once per four hours in page-aligned batches. Storm detection is made
event-driven rather than polled: the threshold comparison runs in the timer handler and asserts
the buzzer directly, so alert latency is bounded by the sampling interval and not by whatever
the main loop is doing. The display and the monthly synchronisation are on-demand consumers,
triggered by a button press and a scheduled wake respectively.

**Step 4 — verify the budget.** Table 2 costs the revised design.

*Table 2: Daily energy cost of the revised event-driven design*

| Component | Assumption | mAh/day |
|---|---|---|
| Deep sleep for ~23.9 h | 5 µA | 0.12 |
| 240 sensor wakes at 50 ms each | 20 mA active | 0.07 |
| Flash batch writes, 6 per day | 15 mA for ~3 s total | 0.01 |
| Storm alerting, 2 min average | 25 mA | 0.83 |
| Display on demand, 10 views × 20 s | 40 mA | 2.20 |
| Monthly BLE sync, 60 s at 100 mA, amortised | | 0.06 |
| **Total** | | **~3.3** |

The revised design uses about 3.3% of the daily budget, against 1740% for the naive version.
The display dominates what remains, which correctly identifies it as the component to optimise
next.

## Discussion

The dominant cost in Table 2 is the backlight, not computation, which is the main design
lesson: once sleep states and batching are applied, the processor is no longer the constraint.
A memory-in-pixel or electrophoretic display would cut that 2.20 mAh to roughly 0.2 mAh
because it retains an image without power, but at 900–1500 tk it strains the original sub-1200
tk budget, so the honest recommendation is an on-demand backlight now and an e-paper upgrade
if the budget grows. The proposal has two further limitations. The figures in both tables are
derived from datasheet typical values rather than measured on hardware, and real solar
harvesting varies with monsoon cloud cover, so a margin of the order observed here is a
requirement rather than a luxury.

The sustainability argument follows from the same numbers. Provisioning 400 KB of SRAM when
the application needs perhaps 20 KB costs very little at purchase but avoids replacing the
entire board when requirements grow, which is exactly the failure this scenario describes.
Page-aligned batching reduces flash wear by writing whole pages instead of five-byte records,
extending service life on a part with finite endurance. Keeping the sensor, compute, and
display functions on separable modules means a cracked screen does not scrap a working
processor, and favouring through-hole, widely stocked parts keeps repair inside the community.
Architectural foresight here is not an abstraction: it is the difference between a firmware
update and a landfill entry.

## Conclusion

The upgrades requested for this weather station are blocked by SRAM capacity and by a
single-threaded control flow, not by insufficient clock speed. Moving to a 32-bit RISC-V part
with integrated Bluetooth Low Energy, placing deadline-critical code in deterministic on-chip
memory while allowing cached flash execution elsewhere, and replacing the superloop with
interrupt-driven acquisition into a batched ring buffer brings the daily cost to roughly 3.3
mAh against a 100 mAh budget. The wider point is that headroom in the memory hierarchy is what
makes incremental growth survivable, and is therefore the cheapest available defence against
premature obsolescence.

## References

1. Barry, R. (2016). *Mastering the FreeRTOS Real Time Kernel: A Hands-On Tutorial Guide*. Real Time Engineers Ltd.
2. Bluetooth SIG. (2019). *Bluetooth Core Specification v5.1*. Bluetooth Special Interest Group.
3. Espressif Systems. (2023). *ESP32-C3 Series Datasheet*. Espressif Systems.
4. Forti, V., Baldé, C. P., Kuehr, R., & Bel, G. (2020). *The Global E-waste Monitor 2020*. UNU/UNITAR, ITU and ISWA.
5. Microchip Technology. (2016). *ATmega328/P Datasheet*. Microchip Technology Inc.
6. Patterson, D. A., & Hennessy, J. L. (2021). *Computer Organization and Design: The Hardware/Software Interface, RISC-V Edition* (2nd ed.). Morgan Kaufmann.
7. SD Association. (2010). *SD Specifications Part 1: Physical Layer Simplified Specification, Version 3.01*. SD Association.
8. Sensirion AG. (2019). *Datasheet SHT3x-DIS: Humidity and Temperature Sensor*. Sensirion AG.
9. Sitronix Technology. (2011). *ST7735S 132 × 162 Pixel TFT Single Chip Driver Datasheet*. Sitronix.
10. Winbond Electronics. (2021). *W25Q64JV 3V 64M-bit Serial Flash Memory Datasheet*. Winbond.

---

# NOT PART OF THE SUBMISSION — working notes for you

## Word count and fit

Body prose is roughly 1,150 words plus two compact tables. In Times New Roman 11, single
spacing, that lands close to two pages. **Check the real page count in Word before submitting**
and if it overruns, cut in this order:

1. The `Step 1` paragraph after Table 1 — the table already carries the argument.
2. The last two sentences of `Discussion` paragraph 1 (the limitations sentence can shrink).
3. The `Background` paragraph on prior work — compress the two strategies into one sentence.

Do **not** cut Background to fit. It is worth 2.3 of 5 marks, which is 46% of the grade.

## Every number, and where it came from

Verify these yourself; do not cite anything you have not opened. Marked *derived* means I
calculated it, so it needs no citation but must be reproducible by you.

| Number | Status |
|---|---|
| 2 KB SRAM, 32 KB flash, 16 MHz | given in the question |
| 12 mA active, ~1 µA power-down | ATmega328P datasheet, electrical characteristics |
| 512-byte SD block | SD Physical Layer Simplified Spec |
| 128 × 160 px, 16 bpp → 40 KB | ST7735 datasheet + *derived* |
| 30 mA HC-05 continuous | module datasheets vary 25–40 mA; state your figure |
| 400 KB SRAM, ~5 µA deep sleep | ESP32-C3 datasheet |
| ~100,000 erase cycles per sector | W25Q64JV datasheet |
| 240 samples/day | *derived*: 1440 min ÷ 6 |
| 1740 mAh/day and 3.3 mAh/day totals | *derived*: Tables 1 and 2 |

Recompute both table totals by hand once. If a marker checks one row and it fails, the whole
quantitative section loses credibility.

## Optional figure

The sample report included a labelled diagram and gained from it. A simple block diagram would
help here: sensors → timer ISR → SRAM ring buffer → (batch) NOR flash, with the display and BLE
hanging off as on-demand consumers, and a dashed box marking which code lives in SRAM versus
cached flash. Draw it yourself in draw.io or PowerPoint. If you adapt any figure from a source,
label it `Adapted from <author> (<year>, p. <n>)` exactly as the sample did — that converts it
from a similarity hit into a citation.

## Rubric mapping

| Section | Marks | What the marker is looking for |
|---|---:|---|
| Introduction | 0.5 | the problem, and your thesis stated in one sentence |
| Background / Related Work | **2.3** | **a citation attached to every factual claim** |
| Methodology | 1.5 | a numbered, followable design procedure |
| Discussion | 0.5 | trade-offs, including what your design costs you |
| References | 0.2 | consistent style, all cited in the body |

The Background section is the grade. Notice that in the text above nearly every sentence there
ends in a citation. That density is deliberate and you should preserve it when you rewrite.
