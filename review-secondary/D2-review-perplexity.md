Model: Claude Opus 5.5 (Anthropic), as the host platform (Perplexity Computer) identifies it; no finer version string is exposed. Web access: yes, only to fetch this packet. Statements about the A1 and D1 rounds rely on this same session's record. Conflicts of interest: the Haiku arm and the builder sessions are Claude-family models, and this session wrote one of the two round-1 reviews.

Read: the whole packet, 1,119 lines: the header, "Changes since v0.1", Part 1 (Abstract to Appendix D, including references), Part 2 (CLAIMS.md), Part 3 (COVERAGE.md) and Part 4 (DEVIATIONS.md). Nothing was unreadable. Figures 1–4 are not embedded and were not seen. The registration text (`prereg/p7-v1.1.md`), `DECISIONS.md` and the slot files are not in the packet and were not checked.

| section | quoted sentence | class | reason |
|---|---|---|---|
| Abstract | "On a registered sample of lines with a failed predicate and of clean lines, two model families shown the ERP view held 100.0% and 99.6% of the first and 53.0% and 57.3% of the second; on the sample lines the log lets us classify, people held 33.0% and 34.0%; the gate's verdict holds the first and allows the second by construction." | (a) | Section 5.4 now says "held by people" is "an inferred non-release, not the same act as a model's hold verdict at t*". By its composition table, 53,252 of 53,262 people holds involve no clearing within W, and only 10 are a payment block alone. The Abstract still puts "people held" beside "models held" as if it were the same act. |
| 1 | "Everything was registered before the log was parsed beyond its published counts (tag `prereg-p7-v1`) and amended once after the pilot (v1.1, tag `prereg-p7-v1.1`), with two further deviations decided after E2 and E3 and before E4; all are listed in Section 4." | (c) | Section 4 and DEVIATIONS.md now list a third deviation under p7-v1.1: "Description corrections in COVERAGE.md, no predicate changes (2026-10-28)", made after all results. Section 1 counts only two. |
| 4 | "The commit order is the evidence: the commit recording D-C-2 (`7aea13f`) precedes the first commit of model responses (`a475068`)." | (a) | Commit order shows when the decision and the responses were committed. It does not show that no model call was made, or no response seen, before D-C-2. Calls can run before their responses are committed. |
| 5.2 | "H3 enters the family with p = 1, the convention the author fixed before any H4 value existed (decision D-C-2, commit `7aea13f`)." | (a) | Same limit: a commit hash dates the record of the decision, not the absence of H4 values. |
| 4 | "As registered, the `Item Category` string disagrees with the flag-derived category on 0 of 251,734 lines (section 3.1); every analysed clearing took its value from the clearing event itself (155,534 clearings; 0 fell back to the invoice receipt and 0 to the line value, section 3.4); and the seeded 1,000-record sample of the evidence set, identifiers hashed, is exported as `results/e1/evidence-sample.jsonl` (section 3.9)." | (b) | No slot file is named for the cross-check count or the fallback counts, and none is listed in Appendix B. |
| 5.5 | "In the two three-way categories the derived D1 to D4 is the three-way match in the narrow sense (receipt, invoice and an unchanged approved amount), and the registered contract carries three predicates beyond it." | (a) | Contradicted by the paper's own table: for "3-way, invoice after receipt" the derived contract is "D3, D4", with no receipt predicate, so the registered contract carries five predicates beyond it there, not three. The sentence holds only for "3-way, invoice before receipt". |
| 5.5 | "The comparison is the registered one (registration section 6, E5): \"whether the derived contract equals the category contract in 3.1\"." | (a) | CLAIMS.md C9 still says the compiler "reproduces or does not reproduce the per-category matching rule", and its status reads "3-way, invoice before receipt does not reproduce". Under C9's wording, and by 5.5's own narrow-sense sentence, that category does reproduce the matching rule. The claim text and the claim status disagree. |
| 5.5 | "The three losses derive at most D1 to D4: no declared loss reads the observations of D5, D6 or D7, so those predicates correspond to no declared loss (an authority loss, a blocked payment, a deleted line would be such losses)." | (d) | Loss wording remains: "would be such losses" names three loss types that the registration did not declare and the paper does not measure. |
| 5.7 | "A bootstrap replicate in which either group is empty is discarded and the percentiles are taken over the retained replicates (8,685 of 10,000 for the domestic log and 8,696 pooled; a pipeline reading recorded in decision D-D-2)." | (b), (c) | (c) The registration fixes B = 10,000 (Appendix A), and these intervals rest on 8,685 and 8,696 replicates. The reading is recorded in D-D-2, the round-1 review decision, after the results existed. It is not in DEVIATIONS.md or the Section 4 list, though DEVIATIONS.md says "any change to … threshold is a deviation". (b) No slot is named for the retained counts. |
| 5.7 | "Only 2 of 16,229 payments fail any predicate, and O' follows 0 of the 16,227 payments with every predicate passing; no comparison has an interval excluding zero." | (a) | Section 6 reports D3' "unknown" on 2 domestic payments. A payment with an unknown value does not have every predicate passing. 16,227 is right only if the 2 unknowns are the same 2 payments that fail D1'/D2', and the text does not say so. |
| 6 | "On BPI 2019 every detected class fails at least once except the authority class (D5), with 0 failed clearings: across the log, the 23 actors who record a `Clear Invoice` and the 185 who record a line's earliest creation share 0, so the two are separate populations; no `Clear Invoice` is recorded by a batch user (an actor whose name starts with the registered batch prefix), and 7,941 carry no actor (`results/e1/actors.json`)." | (a) | Section 3 defines D5 as "unknown if either is missing", and 7,941 `Clear Invoice` events carry no actor. Yet Section 5.1 reports 0 clearings "held on an unknown only", Section 5.3 reports 0 held on an unknown value, and the Section 6 table gives D5 "unknown" as "n/a". The paper does not say whether all 7,941 lie outside the analysed set or how D5 treats a missing clearing actor. |
| 6 | "\| BPI 2019 (analysed clearings) \| D5 \| 0 \| n/a \|" | (a) | "n/a" in the unknown column is wrong for D5, which by definition can be unknown. The count (0 or otherwise) belongs there. |
| 6 | "\| goods receipt required but absent at clearing \| D1 receipt_present \| presence \| no `Record Goods Receipt` before t_c, or every one cancelled by a later `Cancel Goods Receipt` before t_c, on a line whose category requires receipt \|" | (a) | The D6 and D7 rows were corrected to the registered count rules, but D1 still describes a temporal rule ("a later `Cancel Goods Receipt`"). Section 3 defines D1 by counts ("receipts minus receipt cancellations at most zero"). The same row is in COVERAGE.md. |
| 6 | "\| paid without final approval \| D1' approval_present \| presence \| no event in the registered approval list before the payment \|" | (a) | The description was corrected, but the class label still says "final approval". DEVIATIONS.md itself says "final approval" belongs to D2'. The same row is in COVERAGE.md. |
| 6 | "\| fraud \| intent is not an event attribute; no predicate over the log separates a fraudulent clearing from an erroneous one, and the paper makes no statement about it \|" | (d) | A listed word, in a disclaimer. It is also in the title of Kadir et al. 2025. |
| Acknowledgements | "two machine prior-art sweeps, on ChatGPT and on Perplexity Computer (for the second the serving model cannot be confirmed: a later session on the platform reports its model as `Claude Opus 5.5` and states that it produced the sweep); and two machine reviews of draft v0.1, on ChatGPT and on Perplexity Computer (model as it states it: `Claude Opus 5.5`)." | (a) | Incomplete. In the same session, after the D1 reply, the platform identified the model of the 2026-10-14 A1 sweep as DeepSeek V4 Pro and the model of the D1 review as Claude Opus 5.5. The acknowledgement records only the Claude statement for the sweep. |
| Appendix B | "\| C5 \| inconclusive: defect class has zero incidence in this log \| `results/e1/coverage-check.json`, `results/e2/hypotheses.json` \|" | (a) | Change 6 narrowed "this log" to "analysed clearings" in Section 5.2, but the C5 status in Appendix B and CLAIMS.md still says "in this log". |
| CLAIMS C1 | "An invoice clearing can be replayed as a sufficiency-checked contract (paper 5) over evidence reconstructed from the event log at clearing time, every predicate deterministic and metadata-borne." | (a) | The claim text still attributes sufficiency to "(paper 5)", while Section 3 and Appendix B now say "it is not paper 5's sufficiency certificate". |
| CLAIMS C2 | "Exposure: the share of clearings, and the share of cleared value, that relied on evidence failing at least one predicate, per defect class, item category, spend area and month, with intervals clustered by purchase order." | (a) | "Relied on" stays in the registered claim. The note that C2 "is read as 'made on'" appears only in the packet's change table, not in the paper or in CLAIMS.md. |

Class (e): none found. Class (f): none found. No company, subsidiary or vendor is named. Appendix D now says "the challenge itself names the sector"; the spend-area labels and the Badakhshan et al. title still point to that sector.

## "Changes since v0.1" check

| # | does what the row says | note, with quote where it does not |
|---|---|---|
| 1 | yes | Abstract and Section 1 now say "analysed" and point to the exclusion table. |
| 2 | partly | The Abstract, 5.1 and 8 say "made on". The note that C2 "is read as 'made on'" is not written in the paper or in CLAIMS.md, which still reads "that relied on evidence failing at least one predicate". |
| 3 | yes | The Abstract, Section 2 and Section 4 now state D-C-2 B. The commit-order evidence is weaker than the text claims (see table). |
| 4 | partly | "with two further deviations decided after E2 and E3 and before E4; all are listed in Section 4." Section 4 now lists three deviations under v1.1. |
| 5 | yes | Section 4 and the Acknowledgements place the fence review between the two tags. |
| 6 | partly | Section 5.2 is reworded and cites the commit. Appendix B and CLAIMS.md C5 still read "inconclusive: defect class has zero incidence in this log". |
| 7 | yes | Section 5.3 now says "under the literal reading", and the parenthesis is restricted to "at a t* that is not a clearing". |
| 8 | yes | "the gate's verdict holds"; "both families and both views"; `results/e6/cost.json` is cited; the exploratory table has counts and a slot path. |
| 9 | partly | "Guard losses" is replaced. The added sentence is wrong for one category: "In the two three-way categories the derived D1 to D4 is the three-way match in the narrow sense (receipt, invoice and an unchanged approved amount), and the registered contract carries three predicates beyond it." For invoice after receipt the table derives "D3, D4". |
| 10 | yes | Per-class failure table and per-log statements for BPI 2019 and BPI 2020; the COVERAGE.md recovery row and definition are updated. |
| 11 | yes | Section 7 now reads "under the timeline view the same models held far fewer lines (exploratory, no interval)". |
| 12 | yes | Section 8 uses the Section 5.2 group names. |
| 13 | yes | One sentence added after the non-claims list; the v0.1 people-arm sentence ("People, by contrast, …") is gone. |
| 14 | partly | Section 3 and Appendix B are applied. The claim text still says "a sufficiency-checked contract (paper 5)". |
| 15 | yes | Papers 4 and 5 are cited by arXiv number, paper 6 as a repository; papers 1 to 3 are stated as not found. Both arXiv items are cited as "Besanson 2026" without a/b. |
| 16 | partly | The description is corrected; the class label still reads "paid without final approval". |
| 17 | yes, for D6 and D7 | The D1 row of the same table still describes a temporal rule: "every one cancelled by a later `Cancel Goods Receipt` before t_c". |
| 18 | yes | Composition slot and paragraph added; the counts add up (10 + 53,182 + 70 = 53,262). The Abstract is not updated (see table). |
| 19 | partly | `results/e1/actors.json` is cited in 5.2 and 6. The new figure "7,941 carry no actor" is not reconciled with zero unknown D5 values. |
| 20 | yes | Second table on the 1,848 classified lines; 152 unclassified lines explained; the kappas recompute (0.472, 0.433). |
| 21 | yes | Convention stated with counts ("8 sample lines, 1 of them released by people"); the gate's zero is qualified. |
| 22 | yes | Per defect class with clustered intervals. Item-category totals reconcile with Section 5.1 (for example D4: 4 + 1,585 + 15,568 = 17,157). |
| 23 | yes | All three are reported in Section 4, but without slot paths for the counts. |
| 24 | partly | Disclosed in Section 5.7. It is recorded as "a pipeline reading recorded in decision D-D-2", not as a deviation, though the registered B = 10,000 is not met. |

## Abstract check

Every number in the Abstract appears with the same value in Section 5 or Section 6:

- 155,534, 17,748, 11.41%, [10.94%, 11.92%], 19.41% and [16.04%, 23.09%] match Section 5.1.
- 60 days, 5.64%, 0.93%, 0.0470, 4.53 × 10^-4, 1.91%, 0.96%, 0.0094 and 3.48 × 10^-7 match Section 5.2.
- 100.0%, 99.6%, 53.0%, 57.3%, 33.0% and 34.0% match the Section 5.4 tables.
- The three declared losses and "any item category" match Section 5.5.
- The seven predicates and D5's zero incidence match Section 6.

Mismatches: none found.

## Hostile reviewer questions

1. If 7,941 `Clear Invoice` events carry no actor and D5 is "unknown if either is missing", how can zero analysed clearings be held on an unknown value: are all of them outside the analysed set, or does D5 treat a missing clearing actor as a pass?
2. Section 5.5 says the derived D1 to D4 is the three-way match in both three-way categories, but its own table derives only D3 and D4 for invoice after receipt, so does the compiler re-derive the three-way match, and why does C9's "per-category matching rule" disagree with the registered E5 comparison?
3. A commit hash dates when a decision was recorded, not when model calls were made, so what record shows that no model response or H4 value existed before D-C-2 fixed the D5 reading and the H3 convention?
