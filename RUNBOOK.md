# Organics Dashboard v4 — Runbook (LOCKED LOGIC)

> Single source of truth. Hand this file to a fresh chat and say *"read this and continue."*
>
> **Built:** 2026-08-01 · **Owner:** sabarimani.p@infinitylearn.com
> **Output:** `Organics_Dashboard.html` — self-contained, just open it
> **Supersedes:** `..\Dashboard v3\` and `..\New Dashboard\`. It also replaces the old
> **Weekly Cohort Ageing** dashboard — that analysis now lives in the *Weekly View* tab, so the two
> dashboards are finally one file.

---

## 1 · Time model

- **W1 = Monday 4 May 2026.** Monday–Sunday weeks, **W1 … W13** (W13 = 27 Jul – 2 Aug).
- **A month is a GROUP OF WEEKS, not calendar dates.** A week belongs to the month holding most of
  its days (the month of its Thursday):
  - **May = W1–W4** (4–31 May) · **June = W5–W8** (1–28 Jun) · **July = W9–W13** (29 Jun – 2 Aug)
- This is why the MTD view for July starts on **29 June** — the user's instruction: *"July's first
  week is the 29th, so keep that."* A column never splits a week in half.
- Because months are week groups, **week bitmasks answer every question** — the cube needs no
  separate month layer.
- Anything before 4 May is out of scope: *"forget about what is before May 4th."*

## 2 · Cohort, Rolling, Outside

| Period | Cohort | Rolling |
|---|---|---|
| May | created in W1–W4 | created **1 Mar – 30 Apr** |
| June | created in W5–W8 | created **1 Apr – 31 May** |
| July | created in W9–W13 | created **1 May – 30 Jun** |
| August | created in Aug's weeks | created 1 Jun – 31 Jul |

- Rolling = the **two full calendar months before**, derived, never hard-coded.
- **Cohort wins ties.** A lead created 29–30 June is calendar June, but its creation week is W9,
  which is a *July* week — so it is **July cohort and must NOT also be in July's rolling base**,
  or "Both" would double-count it. **1,098 leads** sit in exactly this case. The verification script
  caught this; the dashboard was right and the naive calendar rule was wrong.
- **Outside** = worked in the period but created earlier than the rolling window. No denominator, but
  its sales are surfaced so nothing disappears.
- **1,618 leads created 1–3 May** fall before W1, so they are never a cohort — but they do count in
  June's and July's rolling base.
- For a **single week**, rolling also includes leads created earlier in the same month.

## 3 · Lead Assigned — the denominator

```
assigned = Owner NOT IN {Leads Manager, LSQ Admin, Lead Allocation}
           OR the lead has real activity (call / demo / sale)
```
- **Every rate divides by Lead Assigned.** The % under Assigned is the assign rate (÷ created).
- The activity override guarantees every numerator sits inside the denominator, so **no share can
  exceed 100%** — 288 invariant assertions enforce it.
- Owner is a snapshot at export time; a historical assign rate cannot be reconstructed.

## 4 · The counting rule

**Timing views** — *when did this first happen to a lead*: first call, second call, first answered,
first demo, first conducted. Each lead counted **once**.

**Activity views** — *what did we do in this period*: the funnel stages. **Distinct leads inside the
period** (week bits OR-ed across the period's weeks). A month is therefore **not** the sum of its
weeks — the same lead is often worked in several weeks.

> This is the fix the user demanded: the old dashboard counted a lead again in every week it was
> re-dialled, so Answered exceeded the number of leads ever answered. *"If the lead is answered
> between D0 and D3 it is counted, that's it. It should not count in future days."*

## 5 · Weekly View (the old Cohort Ageing analysis)

Five views, **latest week at the top**, each lead counted **once**:

| View | Bucketed by |
|---|---|
| 1 · Lead → Fresh Dial | its **first** outbound call |
| 2 · Lead → Redial | its **second** call |
| 3 · Lead → Answered | its **first answered** call |
| 4 · Lead → Demo Booking | its **first** demo |
| 5 · Answered → Demo | see below |

- Buckets 1–4 = **calendar days from the cohort week's Monday**: **D0–D3 · D4–D7 · D8–D14 ·
  D15–D30 · D30–D60 · D60+**.
- **View 5 is anchored differently**: buckets are **days from that lead's own first answered call**
  to its first demo — **D0–D3 · D4–D7 · D8+** (three buckets, per the user's instruction).
- Demo leads **never answered** have no anchor, so they are outside View 5's buckets; the count is
  printed in the note rather than hidden.
- **Windows that have not elapsed are greyed, not shown as 0** — W13 started 27 Jul, so it cannot
  have a D8+ figure.
- **This view is cohort only.** Rolling leads were created before 4 May and call data starts 4 May,
  so their D0–D3 window cannot be measured; showing zeros would mislead.
- Views 6 and 7 of the old dashboard (Answered→Demo Timing, Answered Calls before Demo) were
  **dropped** — View 5 replaces the first and the second wasn't wanted.

## 6 · MTD View

- **Lead generation** — leads created, lead assigned (+ assign rate).
- **Consumption** — Consumed (called), Consumed → Answered, Answered → Booked, Booked → Conducted,
  Conducted → Sale. *"Consumed" = a lead dialled at least once; it is not a separate stage.*
- **Columns switch** between MTD (months) and Weekly.
- **Breakup switch**: Total only / Source / Grade / State, with a measure selector so any funnel
  stage can be broken down. **Prediction category was dropped entirely** at the team's request.

## 7 · Compare

Any two periods, **including a month against a single week**. **Counts only** — the pp rate rows
were removed on the user's instruction. Both sides honour the current lead set and filters.

## 8 · Sales

- **The master sheet is truth**, but only sales whose lead is in the **organic** leads file count —
  the master also holds Inbound Project, WhatsApp Chat, InMobious, Referral, External Database etc.,
  which are out of scope for an Organics dashboard.
- 181 distinct lead ids in the master → **129 organic** → **120 inside W1–W13**.
- **52 excluded as non-organic.** **7 organic ones are `Type Of Sales = Offline` and are currently
  included** — say the word to exclude them.
- Sale week always from the master's **Sale Date** (`%d-%b-%y` first, then `%d-%b-%Y`, then a generic
  parse; the build asserts nothing is left unparsed).
- **No purge step any more.** v2/v3 purged referral leads using a Sale-Activity export; that file is
  no longer supplied and is no longer needed, because the LSQ source filter already removes
  non-organic leads.

## 9 · Data prep

- Join on **Prospect ID**, trimmed and lower-cased. Duplicate leads → keep the **earliest** `Created On`.
- Source: contains *learn* → **Learn App** (covers both `Learn AN` and `Learn (AN)`, which are the
  same thing); *surge* → IL Surge; *website* → IL Website; anything else → Other.
- Grades `1-5 / 6-10 / 11-12 / 13 (Dropper)` else Blank/Unknown. `National Capital Territory of
  Delhi` → Delhi.
- Activity rows are kept only if the lead exists in the leads file.

## 10 · Source files — five, in `..\Orignal updated data\`

| File | Rows | Notes |
|---|---|---|
| `Created in Mar to Aug.xlsx` | 76,961 | leads 1 Mar – 1 Aug, **zero duplicates**, `Owner` present |
| `Outbound phone call mar 4 to 1 aug 8pm.xlsx` | 101,925 | 40,327 answered · **despite the name, data starts 4 May** |
| `demo booking 4 mar to 1 aug 8pm.xlsx` | 1,451 | 1,228 leads |
| `demo conducted 4 mar to 1 aug 8 pm.xlsx` | 611 | 582 leads |
| `Original Sales May, June, July.xlsx` | 184 | 181 distinct lead ids |

**LSQ export rules**
- All exports carry the **Lead Source filter**: `IL Website` / `Learn (AN)` / `IL Surge` / `Learn AN`.
  **The same filter must be on every file** — if the leads file is unfiltered while the calls file is
  filtered, every rate comes out too low.
- Activity files are filtered **by activity date**; the calls export also carries
  `Created On 1 Mar → today`, which is fine (it matches the leads file) but means activity on leads
  created before March is invisible — that is why Outside base shows sales with no calls.
- The calls export must include `Status`, or answered cannot be distinguished.

Rebuild: `python _build\build_cube.py` then `python _build\make_dashboard.py`.

## 11 · Colours

The old Weekly Cohort Ageing palette, as requested: **navy `#13315c`** headers, **green intensity**
heat cells, **red `#c0392b`** for drops. The discrete bucket ramp is **`#6cc096 · #1f8f5c · #0a5730`**,
which passes every colourblind-safety check (lightness monotone, adjacent ΔL, light-end contrast,
single hue). A 7-step green ramp was tried for the funnel and **failed** — the steps were
indistinguishable — so funnel bars are a single colour and bar length carries the magnitude.

## 12 · Verified anchors (2026-08-01 build)

| | Leads | Assigned | Called | Answered | Demo booked | Conducted | Sale |
|---|---|---|---|---|---|---|---|
| **May cohort** | 16,777 | 9,957 | 4,515 | 2,757 | 189 | 105 | 25 |
| May rolling | 24,601 | 7,688 | 3,085 | 1,875 | 50 | 30 | 11 |
| **June cohort** | 14,761 | 12,340 | 4,765 | 3,073 | 230 | 125 | 18 |
| June rolling | 31,793 | 15,357 | 4,658 | 2,802 | 79 | 22 | 2 |
| **July cohort** | 19,204 | 12,655 | 10,089 | 7,164 | 387 | 185 | 38 |
| July rolling | 33,156 | 23,136 | 10,011 | 6,443 | 250 | 98 | 21 |

**How it was verified** — the dashboard's own JavaScript executed headlessly, every panel scraped,
and compared against a **separately written** recomputation from the five Excel files:

- **198 of 198** figure assertions pass — monthly cohort and rolling blocks, all 13 weekly blocks,
  all five ageing matrices bucket by bucket, cohort + rolling = both, and the sales
- **288 invariants** hold across every period × lens (assigned ≤ leads, called ≤ assigned, …)
- **Filters partition exactly** — summing each Source (3), Grade (5) and State (143) option
  reproduces the unfiltered total
- **105 renders** clean: no NaN, no empty panels

## 13 · DO-NOT list

- **Do NOT** revert any rate to ÷ Leads Created. Everything is ÷ **Lead Assigned**.
- **Do NOT** drop the activity override from the assigned rule — it keeps every share ≤ 100%.
- **Do NOT** add weeks together to get a month for activity measures. Compute the month directly.
- **Do NOT** put a lead in both cohort and rolling. Cohort wins (the 29–30 June case).
- **Do NOT** count a lead again in a later ageing bucket — first occurrence only.
- **Do NOT** anchor View 5 on the cohort Monday; it is anchored on the lead's **first answered call**.
- **Do NOT** show rolling in the Weekly View — its D0–D3 window is unmeasurable before 4 May.
- **Do NOT** count non-organic master sales (Inbound Project, WhatsApp, Referral…).
- **Do NOT** re-add: Detail views tab, the pp rate rows in Compare, stat tiles, the conversion-rates
  chart, the Analysis tab, or the Prediction category. All were explicitly removed.

## 14 · August growth analysis (from the 2026-08-01 data)

Computed from the verified numbers above; the narrative the user is presenting to leadership.

- **July was the best month by a distance** — 637 demos (cohort 387 + rolling 250) versus 309 in June.
- **The win came from consumption, not lead quality.** Call rate of assigned leads went
  **38.6% → 79.7%**; answer rate 64.5% → 71.0%; demos per assigned lead 1.86% → **3.06%**.
- **Answered → booked fell 7.48% → 5.40%** — we reached far more people and a smaller share said yes.
  Volume covered it. Watch, don't panic.
- **A third of July's leads never reached a salesperson**: 6,549 of 19,204 unassigned (34%), and
  2,566 of the assigned (20%) were never called.
- **August headroom, at July's own 3.84% book-per-called rate:** assigning + calling the 6,549
  ≈ **251 demos**; calling the 2,566 ≈ **98 demos**; total **≈ 350** — roughly a doubling of July,
  with no new leads. Halve it for lead-quality realism → **≈ 175**, the number worth committing to.
- **New leads out-convert old ones per dial**: 3.84% vs **2.50%** (≈1.5×). When capacity is short,
  fresh leads first.
- **Downstream is sliding**: booked → conducted 56.5% → 47.6% → **44.4%**; conducted → sale
  26.7% → 13.6% → 20.8%. Outside the team's control, but raise it first.

**Not yet analysed** (read-only, one query each): speed-to-first-dial vs booking rate; dial attempts
vs outcome; which sources/grades/states hold the 6,549 unassigned.

## 15 · Change log

- **2026-08-01** — v4. The two dashboards merged into one file. Four tabs: Overview (cohort and
  rolling funnels side by side, combined below, What changed), Weekly View (the old ageing analysis,
  5 views, count-once), MTD View (Lead generation + Consumption with breakups), Compare (counts only).
  Months redefined as groups of weeks. Prediction category, Detail views, stat tiles, rates chart and
  Analysis tab removed. Old ageing palette restored. Sales re-based to organic-only; purge dropped.
