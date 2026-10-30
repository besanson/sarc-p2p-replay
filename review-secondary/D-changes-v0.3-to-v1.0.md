# Changes since v0.3 (draft v0.3 to the v1.0 candidate)

Generated from `DECISIONS.md` D-D-4 by `scripts/d_d_4.py`, for the record; there is no round-4 packet. Every round-3 finding the author accepted, numbering as in D-D-4, and where it was applied. The rejected findings and their reasons are in D-D-4.

| # | finding (round 3) | where applied in the v1.0 candidate |
|---|---|---|
| 1 | The Jev reply-template adaptation (typed choice instead of the registered JSON reply) is recorded as a pipeline reading in D-C-3, not as a deviation | prereg/DEVIATIONS.md, "E4 Jev request format"; Section 1 counts five deviations under v1.1; Section 4 lists it; one sentence in 5.4 |
| 2 | The Abstract calls every people hold an inferred non-release; the measure also includes a recorded payment block | Abstract: "where a hold is a recorded payment block or, in nearly every case, an inferred non-release within 60 days, not a recorded decision" |
| 3 | C9's "per-category matching rule" and its status "not supported" are not aligned with 5.5 | CLAIMS.md reading notes and Appendix B: a C9 note; the status refers to the registered comparison |
| 4 | Section 7: "reported beside every estimate" overstates what the paper shows for 5.2 and 5.3 | Appendix E (H1, H2 and gate by outcome per category, spend area, value quartile, vendor activity quartile and month), pointed to from 5.2, 5.3 and 7 |
| 5 | What substantive assurance C1's sufficiency check adds | Conclusion, one sentence: sufficient for "goods not received" and "changed amount", not for "pay twice" in the three-way categories, because no registered predicate reads the clearing's position |
| 6 | Which inferences the people, model and gate comparison supports | Section 7, one sentence: the only inference the three columns support; no decision quality is inferred for people |
| 7 | What the expected-correctives totals estimate | 5.4, one sentence: a projection from observed rates onto the sample, not an observed count |
| 8 | Section 6 table: "n/a" for the unknown counts of every predicate but D5 | results/e1/predicate-unknowns.json (a new slot); the Section 6 table |
