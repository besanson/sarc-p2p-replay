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

p7-v1.1: no deviations (pending tag).
