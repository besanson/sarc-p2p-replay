# Deviations

One entry per deviation from `prereg/p7-v1.md` after the tag `prereg-p7-v1`:
what changed, why, when it was found, and which results it touches. Pipeline
fixes during C0 that change no registered item are logged in `DECISIONS.md`
instead; any change to a predicate, pattern, template, mapping, window, frame,
sample or threshold is a deviation.

p7-v1: tagged `prereg-p7-v1` on e239864. No deviations.

## p7-v1 to p7-v1.1 (2026-10-19)

Found at E0 run 1 (`DECISIONS.md` D-C0-1), which fired two stop conditions of
section 2.2. Three changes, registered in `prereg/p7-v1.1.md`:

1. **T_end rule** (section 2, observation end): T_end is the latest timestamp in
   the last calendar month (UTC) carrying at least 1,000 events; events after
   T_end are excluded from every computation and counted in a slot. Under v1,
   T_end was the latest timestamp of any event (2020-04-09, set by two
   outlying events). Touches the frame.
2. **Mapping attribute name** (`prereg/column-mapping.yaml`): case attribute
   `Doc. Category name` renamed `Purch. Doc. Category name`, the name the log
   uses. Touches the mapping; the engine does not read this field.
3. **Section 3.6, explicit sentence**: a clearing recorded before the first
   `Record Invoice Receipt` counts as a release (it fails D3; it is not a
   hold). This states the reading already implemented and recorded in D-B-1,
   confirmed by the author in D-C0-2.

No result is touched: none exists. E0 is drawn again under v1.1 before E1.

p7-v1.1: tagged `prereg-p7-v1.1` on d8cdb2d.

## Under p7-v1.1

### H3 convention (2026-10-25)

Found after E2 (`DECISIONS.md` D-C-1): no analysed clearing fails D5, so the
H3 defect group is empty and the registered H3 statistic is not computable.
The author decided (D-C-2, A) that the Holm family stays at five tests and H3
enters it with p = 1; C5 will read "inconclusive: defect class has zero
incidence in this log". Touches: the Holm family (section 4). Does not touch
the E1 or E2 estimates. Results it changes: the Holm table in `results/e2/hypotheses.json`
(`holm`) and `results/e4/h4.json`.

### D5 applicability at a non-clearing decision point (2026-10-25)

Found at E3 (`DECISIONS.md` D-C-1): under the literal reading of section 7, D5
at a decision point t* that is not a clearing is unknown, so a line with no
clearing within W can never be clean. The author decided (D-C-2, B) that D5 is
not applicable there and counts as pass. Touches: the line status at t*, hence
the E3 human-hold slot and the E4 sample frame. Does not touch E1 or E2 (no
predicate at an actual clearing changes). Results it changes:
`results/e3/human-hold.json` (both readings kept) and every E4 result.

### Description corrections in COVERAGE.md, no predicate changes (2026-10-28)

Found in review round 1 (`DECISIONS.md` D-D-2). The descriptions in `COVERAGE.md` are corrected to
match the registered predicates; no predicate, pattern, template, mapping or threshold changes, and
no result changes. D1' row: "no event in the registered approval list before the payment" (it read
"no final approval event", which is D2'); D6 row: the count rule of section 3.2 (sets minus removals
greater than zero before t_c); D7 row: the count rule of section 3.2 (deletions plus blocks minus
reactivations greater than zero before t_c); the "Detected" definition adds that the absent and stale
receipt split uses events after t_c and is reporting only (section 3.3); the recovery row reads "the
log records the corrective event and nothing about recovery". Touches: `COVERAGE.md` and the paper's
coverage table, which reproduces it.

Addendum (2026-10-30). Found in review round 2 (`DECISIONS.md` D-D-3). D1 row: the count rule of
section 3.2, "receipts minus cancellations at most zero before t_c, on a line whose category requires
receipt" (it described a temporal rule, "every one cancelled by a later `Cancel Goods Receipt`"); D1'
class label: "paid without an approval event" (it read "paid without final approval", which is D2').
No predicate, pattern, template, mapping or threshold changes, and no result changes.

### E7 bootstrap replicates with an empty group discarded (2026-10-25)

Found in review round 1 and recorded then as a pipeline reading (`DECISIONS.md` D-D-2); entered here
in review round 2 (`DECISIONS.md` D-D-3, 2026-10-30). The registration fixes the bootstrap at
B = 10,000 (sections 5 and 9), and E7 reports a clustered interval (sections 6 and 8). In `experiments/e7.py`, as run on 2026-10-25, a replicate in which either
comparison group is empty is discarded, and the percentiles are taken over the retained replicates,
so the E7 intervals rest on fewer than B replicates. Touches: the E7 bootstrap intervals (section 8),
descriptive and not in Holm. Does not touch any point estimate, BPI 2019 result or Holm entry. The
retained counts per scope and predicate are in `results/e7/comparisons.json`
(`bootstrap_resamples_used`). Results it changes: none; the slot is as committed.
