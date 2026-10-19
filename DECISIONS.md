# Decisions

One entry per decision, append-only. A decision that changes a registered item
after the tag `prereg-p7-v1` is a deviation and also goes in
`prereg/DEVIATIONS.md`.

## D-A0-1 Datasets, licences and hashes (2026-10-12)

Verified from the 4TU.ResearchData record pages and the 4TU v2 API, not from
memory:

- **BPI Challenge 2019.** DOI `10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1`.
  Licence as the page states it: CC BY 4.0. One file, `BPI_Challenge_2019.xes`,
  728,558,522 bytes, SHA-256
  `af63bc687fc4152f2123b05c3af7772b37ef3fce2d3f67f812666c9e356baae7`. Published
  counts 251,734 cases and 1,595,923 events, confirmed by tag count.
- **BPI Challenge 2020**, collection DOI
  `10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51` (no collection-level
  licence; each member states its own). E7 uses the two declaration logs:
  - International Declarations, DOI `10.4121/uuid:2bbf8f6a-fc50-48eb-aa9e-c4ea5ef7e8c5`,
    CC BY-NC 4.0, `InternationalDeclarations.xes.gz`, 1,581,144 bytes, SHA-256
    `b527c8d06255f4312c6ce8f36f7f4110243d84fd6ca48583cd9b80896c601494`, 6,449
    cases and 72,151 events, confirmed.
  - Domestic Declarations, DOI `10.4121/uuid:3f422315-ed9d-4882-891f-e180b5b4feb5`,
    CC BY-NC 4.0, `DomesticDeclarations.xes.gz`, 933,930 bytes, SHA-256
    `0bc3312acf0b9ee5ae6f4ebe9df204005ef11665d62f2d21dd04995161d7532b`, 10,500
    cases and 56,437 events, confirmed.

Neither licence forbids redistribution. The logs are still not committed: the
2019 file is 728 MB, and the 2020 files carry a non-commercial term that the
repository's Apache 2.0 licence should not appear to cover. `data/` is
gitignored; `make bootstrap` fetches by URL and checks SHA-256 against
`prereg/data.lock`. The paper cites both licences and attributes 4TU and the
challenge organisers. The non-commercial term binds use of the BPI 2020 logs, not
the replay code.

"Travel declarations" in the brief is read as the two declaration datasets. The
other three BPI 2020 members are not used.

## D-A0-2 Sibling pins (2026-10-12)

`engines.lock` pins the three siblings at their `main` heads on 2026-10-12:
dqSarc `db6c396128a4df7fe12d13be163b1e7d32087177`, sarc-authority-derivation
`cfb321ec220e83e81a771a048276571f6edf08fb`, gigo-jev-probe
`e1fc75b6686beecd3f4abdd57241ffc46c96e019`. The first two equal paper 6's own
pins. Each is cloned at `../<name>`.

## D-A0-3 Where "as paper 6" resolves (2026-10-12)

gigo-jev-probe (paper 6) carries the preflight shape, `engines.lock`, the
`.env.example` discipline, `prereg/DEVIATIONS.md`, the arm health rule and the
two model families. It carries no Makefile, no lint modules, no gate layout and
no `FINAL-AUDIT.md`; those live in sarc-authority-derivation (paper 5), which
paper 6 pins. "As paper 6" is therefore read as paper 6 where paper 6 has the
item and paper 5 otherwise: the 12-item audit, the G1 to G9 gate names, and the
lint conventions (local negation, fenced and inline code stripped) come from
paper 5.

At A0 only the terminology lint is written (`lint/terminology.py`). The
typed-numeral and proof-status lints need paper prose and property tests to
act on; they are ported from paper 5 in Phases B and D, before any number is in
the draft.

## D-A0-4 Preflight reports, it does not gate, at A0 (2026-10-12)

Paper 6's preflight exits non-zero when a key is missing, because it ran before
model calls. At A0 the brief requires preflight to pass with keys and data
absent. `preflight.py` therefore reports each item (keys, data, siblings) as
present or absent and exits 0; `--require keys,data,siblings` turns any named
item into a hard failure for Phases C and later. It never prints a key and never
raises.

## D-A0-5 Registration choices the brief left open (2026-10-12)

Each is registered in `prereg/p7-v1.md`; listed here with the reason.

- **Window = calendar 2018.** The 4TU record states time coverage 2018. E0 stops
  the run if fewer than half of the creation events fall in it (section 2.2).
- **T_end = latest timestamp in the log**, with a stop if it lies after 2019:
  the rule is fixed before the data are read, and outliers trigger
  re-registration rather than a silent trim.
- **K = 12 clearings** for the framework-agreement exclusion: the record's own
  ordinary recurring example (rent) has twelve.
- **Category from the two flags** (plus consignment by item type), as the record
  states the rules; the `Item Category` string is a cross-check.
- **Unknown predicate values** (missing actor) make the gate hold but are not
  defects; H3 excludes them and reports the count. This keeps D5 failures from
  being inflated by missing data.
- **D1 and D2 coincide at t_c.** Both fail iff no uncancelled receipt precedes
  t_c. The brief's split into absent and stale receipt is kept as a reporting
  class assigned from what the log records after t_c, never as gate input.
- **Counts, not event order, for cancellations, blocks and deletions,** so the
  verdict is invariant under reordering of equal-timestamp events, as the
  property test requires.
- **H1 comparison restricted to 3-way categories,** where D1 and D2 apply to both
  groups; the all-category comparison is reported beside it.
- **Clustered bootstrap z-test** for H1 to H3 and **TOST** with unpooled standard
  error for H4; Holm over five tests (H4 once per family).
- **E4 decision point t*:** the first clearing if the human cleared within W of
  the first invoice receipt, else the end of that window; the view is the
  evidence as it stood when the human decision was made. At most one line per
  purchase document.
- **E4 families as paper 6:** TypeSafe System One (Jev) and Claude Haiku 4.5
  pinned `claude-haiku-4-5-20251001`, request and parser shape of jev-v3, arm
  health rule with a second check after 200 lines, before the full sample.
- **Activity and attribute names not read from the log.** Names the brief gives
  are used verbatim. Other names (approval-bearing events, line block and
  reactivation, every BPI 2020 activity, the event attribute keys) come from the
  record and challenge documentation and are marked `unverified` in the YAML
  files. Reading them from the log before the tag would be parsing beyond the
  published counts. C0 reports frequencies; a missing mapped attribute stops the
  run for re-registration; a missing activity is reported with a zero count.

## D-B-1 Phase B readings of the registration (2026-10-12)

Phase B implements `prereg/p7-v1.md` against synthetic fixtures only
(`tests/fixtures/`, generated by `make_fixtures.py`). No registered item is
changed. Where the registration text needed a reading to become code, the
reading is listed here; each is covered by a named test.

- **Human hold (3.6).** "No clearing within W days after the first invoice
  receipt" counts any clearing at most W days after that receipt as a release,
  including a clearing recorded before the receipt (that clearing is a D3
  defect, but the person did release it). `test_human_hold`.
- **Ties at the earliest creation.** Line value is the value of the first
  creation event in canonical order (timestamp, activity, actor, value). D5
  compares the clearing actor with every non-missing actor at the earliest
  creation timestamp. `test_line_and_cleared_values`, `test_d5_actors`.
- **D4 with no approval-bearing event at or before t_c** (only possible when the
  line is created after the clearing) is unknown, not pass. `test_d4_...`.
- **Cleared-value fallback** "latest Record Invoice Receipt before t_c" is the
  last such event in canonical order at or before t_c.
- **ERP view.** Approved price is the first non-missing value among
  approval-bearing events at the last approval timestamp, else the line value;
  invoice date and value are those of the latest invoice receipt at or before
  t*; goods receipt date is the latest `Record Goods Receipt` at or before t*
  when the uncancelled count is positive, else "none".
  `test_view_renders_registered_template_without_timeline_or_ids`.
- **E7.** D3' is unknown when no approval precedes the payment (D1' then fails).
  A payment is allowed iff D1' to D3' all pass. `test_declarations_fixture`.
- **Evidence export.** The public sample export replaces line, purchase
  document, clearing actor, company and vendor ids with the first 16 hex digits
  of their SHA-256. `test_export_record_hashes_identifiers`.

## D-B-2 Property tests and mutation gate (2026-10-12)

Five properties (P1 determinism, P2 idempotence, P3 reorder invariance within
equal timestamps, P4 no look-ahead, P5 min() contract) run on 400 derandomised
generated lines each in every ordinary run, tagged `machine-checked` in
`tests/test_properties.py` and checked by `lint/proof_status.py` (ported from
paper 5). Under mutmut each mutant runs them at 60 lines, so that the gate's wall
time stays bounded; the tagged domain is the ordinary run's 400.

The mutation gate is mutmut 3.7.0 on `src/p2p_replay`, as paper 5, with the
engine's three test modules selected. Threshold 0.85 and no uncovered mutant
(`scripts/mutation_check.py`, `make mutate`).

Result on 2026-10-12, `make mutate` after the boundary tests below: 1,407
mutants, 1,321 killed, 86 survived, 0 without a covering test; kill score
0.9389, gate passed. A first run scored 0.9076; its survivors in decision
logic pointed to untested boundaries (a change at the approval timestamp, the
block and deletion balances in the evidence inputs, an early E4 decision point,
the E7 horizon and resubmission at the approval timestamp, view fields, the
one-day lag edge, the category kept on excluded lines, a pinned source hash, a
CSV log through the CLI with its own mapping file), each now tested. The
remaining survivors are equivalent or cosmetic: error-message and help strings,
`encoding="UTF-8"` against `"utf-8"`, `Z` suffix handling that
`datetime.fromisoformat` already does, and `>=` against `>` where the two
branches return the same value.

## D-A1-0 A1 begins after Phase B (2026-10-13)

Phase B (replay engine on fixtures, commits `2da2586` and `e97fab8`) ran before
A1. B changed no registered file: at the start of this session,
`git diff prereg-p7-v1..HEAD -- prereg/ CLAIMS.md COVERAGE.md NOVELTY.md engines.lock`
at HEAD `e97fab8` was empty (exit status 0, no output). A1 preparation then
edited only the "Not claimed as new" citations of `NOVELTY.md` and the one intro
sentence on verification (commit `03027f9`); `prereg/`, `CLAIMS.md`,
`COVERAGE.md` and `engines.lock` are unchanged.

`prereg/p7-v1.md` section 12 reads "A1 fence review, then this tag (or v1.1 if
section 6 changes)", while the brief and README place the tag at A0. The tag
stands as made by the author: `prereg-p7-v1` on `e239864`. Section 12 is read as
"then v1.1, if the review requires it". No file under `prereg/` is edited.

The fence packet is `review-secondary/A1-fence-packet.md`. No reviewer has been
chosen.

D-A1-1 is reserved for the adjudication of the review and is not written now.

## D-A1-0b Machine prior-art sweep (2026-10-14)

**What was run.** The author ran a prior-art sweep with OpenAI ChatGPT (Astra 6, as stated by the author;
web search on) on `review-secondary/A1-fence-packet.md` (commit `f0e6b90`), with
the packet's own reviewer instructions plus a rule that every source carries a
resolving URL and a quoted line. Hyperlinks were lost when the text was copied
from a tablet; the model's plain-text URL list was requested afterwards. Both
were committed unedited (commit `6d1248c`):

| file | SHA-256 |
|---|---|
| `review-secondary/A1-fence-sweep-gpt.md` | `aa007a0379381926060a9cd75861a02a5708f0eb85448e112d85a24729331600` |
| `review-secondary/A1-fence-sweep-gpt-urls.md` | `b9c2cf2e0d1f3efa0204622bfdb297d9dec33fd6a1c08dd9455daeceee6ca0b5` |
| `review-secondary/A1-fence-sweep-gpt.attestation.md` | attestation (model, date, prompt, both hashes) |

**Verification on 2026-10-14.** Every URL in the list was fetched from this
session; the sweep's quoted line was searched in the PDF text page by page, or
read on the page. No host was blocked by the network policy; four sites
refused the page (403 or 404). Records: `verified-citations.json` (new records,
or a `sweep_check` object on existing ones).

| source (record id) | status | where checked |
|---|---|---|
| Pesic, Schonenberg, van der Aalst 2007 (`pesic-declare-2007`) | verified | PDF p. 5, section II-B |
| Diba, Remy, Pufahl 2019 (`bpi2019-nonstudent-6-diba`) | verified | PDF p. 15, Table 2 rule 1 and section 4.1 |
| Porter et al. 2019, Table 3 (`bpi2019-nonstudent-8-porter`) | verified | PDF p. 8 |
| Porter et al. 2019, 120-day passage (same record) | verified | PDF p. 10, section 3.3 |
| Gutermuth et al. 2019 (`bpi2019-nonstudent-7-gutermuth`) | verified | PDF p. 22, section 6; the "6.3" label is not in the extracted text |
| Besanson 2026, paper 5 (`besanson-paper5-2026`) | verified | arXiv PDF p. 7, section 8, claim C3 |
| Outmazgin and Soffer 2013 (`outmazgin-workarounds-2013`) | verified | Springer abstract, last sentence, checked character for character |
| Ly et al. 2015 (`ly-compliance-monitoring-2015`) | verified | author-hosted PDF p. 15, section 4.1, CMF 3 |
| PCAOB Release 2004-001 (`pcaob-release-2004-001`) | verified | Appendix B, Example B-4, printed p. A-131 |
| Peleg, Soffer, Ghattas 2008, publisher page (`peleg-mining-outcomes-2008`) | reached, quote not checked | the page carries the abstract only; the "Objective 2" sentence is body text |
| Peleg et al. 2008, ResearchGate copy (`peleg-mining-outcomes-2008-researchgate`) | unreachable | 403 |
| Meyer zu Wickern et al. 2019 (`bpi2019-student-4-meyerzuwickern`) | verified | PDF p. 17, section 5.1 |
| Badakhshan et al. 2019 (`bpi2019-nonstudent-4-badakhshan`) | verified | PDF p. 22, Table 5 |
| Pufahl, Hobeck et al. 2020 (`bpi2020-award-hobeck`) | verified | PDF p. 20 Table 7, p. 21 Table 8 |
| Kas, Post, Wiewel 2020 (`bpi2020-student-award-kas`) | verified | PDF p. 10, question 9 |
| Chiu and Jans 2019 (`chiu-jans-2019`) | unreachable | 403 |
| ISACA 2010 (`isaca-2010`) | not found | 404 |
| Leonardi et al. 2025 (`leonardi-2025`) | unreachable | 403 |
| van der Aalst 2016 (`vanderaalst-process-mining-2016`) | reached, quote not checked | publisher page; the sweep quotes nothing from it |

No mismatch was found: every quote that could be read is where the sweep says
it is. Two small differences, recorded and not acted on: Diba et al.'s own title
page reads "Compliance and Performance Analysis of Procurement Processes Using
Process Mining" (the challenge page and NOVELTY.md use "BPI Challenge 2019:
Performance and Compliance Analysis ..."); the Pufahl, Hobeck et al. title page
lists Pufahl first, the ICPM 2020 awards page Hobeck first (NOVELTY.md now
follows the title page).

**Paragraphs of "Not claimed as new" that gained a source** (NOVELTY.md):
four-eyes (Ly et al. 2015, CMF 3); three-way match (PCAOB 2004-001, Example
B-4); rework (Meyer zu Wickern et al. 2019 section 5.1; Badakhshan et al. 2019
Table 5). The BPI 2019 paragraph gained one sentence on Porter et al. Table 3
and Diba et al. Table 2 and section 4.1. The BPI 2020 paragraph now links both
award reports' texts. **Deviation-to-outcome keeps "(No source cited yet.)"**:
Peleg et al.'s quotation could not be checked from here.

**Candidates against "Claimed" items: candidate, awaiting the author's
adjudication at D-A1-1.** None is applied to NOVELTY.md.

| Claimed item | candidate | status | quoted line |
|---|---|---|---|
| 1 (min() contract) | Pesic, Schonenberg, van der Aalst 2007, conjunction of constraints | verified | "A process model containing multiple constraints is defined as a conjunction of the constraints, i.e., actions of users during execution must fulfill all the constraints." (p. 5, II-B) |
| 2 (exposure in count and value) | Porter et al. 2019, Table 3 | verified | "Compliance by number" 80.5%, "Compliance by EUR value" 80.2% (3-Way After, p. 8) |
| 3 (consequence conditional on the defect) | Porter et al. 2019, section 3.3 | verified | "We identify a number of cases where a 'Cancel Invoice Receipt' event occurs over 120 days after the initial 'Clear Invoice' event, which would conclude a compliant cycle." (p. 10) |
| 4 (humans, models and gate on the same lines) | Gutermuth et al. 2019, anomaly classification | verified | "The results show that the presented approach can distinguish between normal and anomalous cases and confirms the anomalies from sections 6.1 and 6.2." (p. 22) |
| 1 and 5 (contract synthesis, fewest fields) | Besanson 2026, paper 5, claim C3 | verified | "The implementation selects minimum-cardinality or minimum-cost sufficient contracts using distinct objectives." (p. 7) |
| 6 (coverage matrix) | Outmazgin and Soffer 2013 | verified | "The remaining two types are not reflected in events logs and cannot be detected by process mining." (abstract) |

The sweep's own verdict: for each of the six Claimed items as a complete
combination it found no antecedent ("c"); every candidate above is a component
precedent. It adds that "c does not establish novelty".

**Proposed rewording of the related-work sentence (not applied).** The sweep
judges that the sentence "does not hold unqualified as written" and proposes
that "the evidence it relied on" become "the evidence reconstructed from the
event log at clearing time", because "the packet establishes a reconstruction,
not which information the original decision-maker actually consulted"; it adds
that the component precedents should delimit the contribution.

**Named by the sweep, not used as evidence.** Chiu and Jans 2019 (unreachable,
403), ISACA 2010 (not found, 404), Leonardi et al. 2025 (unreachable, 403). Not
cited in NOVELTY.md.

This sweep is AI support, to be disclosed in the acknowledgements; it is not the external fence review.

## D-A1-0c Second machine prior-art sweep (2026-10-14)

**What was run.** The author ran a second prior-art sweep with DeepSeek
(DeepSeek 4.0 Pro, as stated by the author; web search on) on the packet at commit `fc6447e`, asking for what the
first sweep (D-A1-0b) missed, in priority order: Claimed item 4, Claimed item 3,
the uncited deviation-to-outcome paragraph, then items 1, 2, 5 and 6, with a
resolving URL and a quoted line for every source. Committed unedited (commit
`f7593df`) as `review-secondary/A1-fence-sweep-deepseek.md`, SHA-256
`eba8dc4dd37a4055885e56b7ef3e1497b3e1e32893280565f3991d2a1da2e885`, with
`review-secondary/A1-fence-sweep-deepseek.attestation.md`. The author's file
name, A1-fence-review.md, is reserved for the external review.

**Verification on 2026-10-14.** Each URL fetched from this session. No host was
blocked by the network policy; dl.acm.org and sciencedirect.com refused pages
(403). Records in `verified-citations.json`.

| source (record id) | status | where checked |
|---|---|---|
| Palma et al. 2026, "Business Compromise Detection with Agentic AI and LLM-driven Knowledge Discovery", arXiv:2609.32643 (`palma-business-compromise-2026`) | **mismatch** | HTML and PDF; section 4.3, Tables 1 and 2 |
| Kadir et al. 2025, "AuditCopilot", arXiv:2512.02726 (`kadir-auditcopilot-2025`) | verified | arXiv abstract |
| Harding and Vasconcelos 2022, "Managers versus Machines", arXiv:2202.04218 (`harding-managers-machines-2022`) | verified | arXiv abstract (the sweep's ellipsis drops one clause) |
| Teinemaa, Dumas, La Rosa, Maggi 2019, "Outcome-Oriented Predictive Process Monitoring", ACM TKDD 13(2), doi:10.1145/3301300 (`teinemaa-outcome-ppm-2019`) | verified | ACM page 403; DOI registered (doi.org handle API); quote found in the publisher-deposited abstract in the Crossref record |
| Nguyen, Dumas, La Rosa, Maggi, Suriadi 2016, "Business Process Deviance Mining: Review and Evaluation", arXiv:1608.08252 (`nguyen-deviance-mining-2016`) | verified | arXiv abstract |
| Peleg, Soffer, Ghattas 2008, LNCS 4928, pp. 395-400 (`peleg-mining-outcomes-2008`) | verified (was "reached, quote not checked") | Springer abstract, sentence checked character for character |
| Ghattas, Soffer, Peleg 2014, Decision Support Systems 59 (`ghattas-decision-making-2014`) | unreachable | no URL or quote given; ScienceDirect search and volume page 403; existence not confirmed; not evidence |

**Mismatch.** The sweep says of Palma et al. 2026: "No deterministic rule is one
of the side-by-side deciders." The paper's Table 1 ("Comparison of different
approaches to ground truth (SME)", the same 397 accounts) lists Human Reviewer
(MCC 0.422), Agent Only (0.295), Gradient Boosting (0.338), Random Forest
(0.386), and rule-based deciders: FOIL-IE (L1, symbolic rules learned by
Inductive Logic Programming, 0.425) and the full neuro-symbolic stage
(L1+L2+L3, 0.435); Table 2 gives full stage minus Human Reviewer dMCC +0.012,
p = 0.881. The quoted sentence continues: "...replacing only who decides, the
agent's own verdict versus the knowledge stage, raises MCC from 0.295 to 0.435".
The MCC values the sweep quotes are correct. So the paper puts a human, an LLM
agent, tree ensembles and learned symbolic rules on the same cases; the rules are
learned, not a declared contract. This makes it a closer component precedent for
Claimed item 4 than the sweep reports.

**The sweep's verdict per Claimed item.** Item 4: complete combination not found
(c). Item 3: complete combination not found (c). Items 1, 2, 5, 6: nothing new
beyond the first sweep's component precedents (D-A1-0b).

**Candidates: candidate, awaiting the author's adjudication at D-A1-1.**

| Claimed item | candidate (record id) | status | quoted line |
|---|---|---|---|
| 4 | Palma et al. 2026 (`palma-business-compromise-2026`) | mismatch (see above) | Table 1: Human Reviewer 0.422, Agent Only 0.295, Gradient Boosting 0.338, Random Forest 0.386, FOIL-IE 0.425, Full 0.435 (397 accounts) |
| 4 | Kadir et al. 2025 (`kadir-auditcopilot-2025`) | verified | "Benchmarking SoTA LLMs such as LLaMA and Gemma on both synthetic and real-world anonymized ledgers, we compare them against JETs and machine learning baselines." |
| 4 | Harding and Vasconcelos 2022 (`harding-managers-machines-2022`) | verified | "Even though a typical bank already relies on an algorithmic scorecard process to evaluate risk, bank managers are given significant latitude in adjusting the risk score ... We show that it is possible to find machine learning algorithms that can replicate the behavior of the bank managers." |
| 3 | Teinemaa et al. 2019 (`teinemaa-outcome-ppm-2019`) | verified | "outcome-oriented predictive process monitoring, which refers to classifying each ongoing case of a process according to a given set of possible categorical outcomes" |
| 3 | Nguyen et al. 2016 (`nguyen-deviance-mining-2016`) | verified | "Business process deviance refers to the phenomenon whereby a subset of the executions of a business process deviate, in a negative or positive way, with respect to its expected or desirable outcomes." |

**Source for the deviation-to-outcome paragraph: to be cited at D-A1-1 if
verified.** Peleg, Soffer and Ghattas 2008 (`peleg-mining-outcomes-2008`), now
verified on its abstract: "This position paper motivates the extension of
process mining in order to capture not only deviations from the process model,
but also the outcomes associated with them (e.g., patient improving or
deteriorating)." NOVELTY.md is not changed now; the paragraph keeps its marker
until D-A1-1.

**Sentence rewording (same as the first sweep's, not applied).** Replace "the
evidence it relied on" with "the evidence reconstructed from the event log at
clearing time", because the design "does not establish which information the
original human approver actually consulted". The sweep otherwise finds that the
sentence holds and that "puts people, models and the gate on the same lines can
stand as the contribution".

The packet at fc6447e was not changed: it is with the external reviewer.

This sweep is AI support, to be disclosed in the acknowledgements; it is not the external fence review.

## D-A1-1 A1 adjudication (2026-10-18)

**Inputs.** The external fence review by Eduardo Arana, dated 2026-10-16, on the
packet at `fc6447e`, committed unedited as `review-secondary/A1-fence-review.md`
(commit `186cad3`, SHA-256
`75e42682837a377f735ba8176cbb1176244cefb52570f645faf7907f280b0673`, attestation
beside it); the first machine sweep (D-A1-0b); the second machine sweep
(D-A1-0c). The decisions below are the author's.

| finding | origin | class | decision | reason |
|---|---|---|---|---|
| Item 1, min() contract on reconstructed clearing-time evidence | review; sweep 1 (Declare, paper 5) | (c); components (a) | **Kept as claimed.** Declare (conjunction of constraints) and paper 5 (compiler, minimum-cardinality contracts) cited as components in "Not claimed as new". | The per-clearing gate verdict at t_c over a reconstructed evidence set with pass/fail/unknown is not found; the components are. |
| Item 2, exposure in count and value | review; sweep 1 (Porter et al. Table 3) | (a) | **Accepted.** The count-and-value measure moves to "Not claimed as new" (new paragraph "Compliance measured by count and by value"); item 2 reworded to the per-clearing, per-defect-class tabulation with purchase-order-clustered intervals. | Porter et al. 2019 Table 3 reports compliance by number and by EUR value on this log. |
| Item 3, consequence conditional on the defect, W and lag bands | review; sweep 1 (Porter 3.3); sweep 2 (Teinemaa, Nguyen) | (c) | **Kept.** Peleg, Soffer and Ghattas 2008 cited as the deviation-to-outcome precedent; Teinemaa et al. 2019 and Nguyen et al. 2016 as framing precedents; Porter et al. section 3.3 as a case-study observation on this log. | No registered conditional-consequence design with window and lag bands found. |
| Item 4, Gutermuth et al. as component | sweep 1 | rejected by review | **Withdrawn** (the D-A1-0b row for item 4). | The review: distinguishing normal from anomalous cases is not a three-way decision comparison on the same instances; accepted. |
| Item 4, humans, two model families and the gate on the same lines | review; sweep 2 (Palma, Kadir, Harding) | (c); components (b) | **Kept and sharpened.** Item 4 now states that the gate is declared before the data are read; comparing deciders on the same cases moves to "Not claimed as new" (new paragraph "Comparing deciders on the same cases"), citing Palma et al. 2026, Kadir et al. 2025 and Harding and Vasconcelos 2022. | Palma et al. surfaced after the packet was sent and was not seen by the reviewer; on its Table 1 it compares a human reviewer, an LLM agent, tree ensembles and learned symbolic rules on the same cases. None of the three uses a deterministic contract declared before the data are read, or a human arm read from a process event log. This is the author's adjudication; a follow-up to the reviewer on Palma et al. is pending and will be committed as an addendum if it arrives. |
| Item 5, control derived from declared losses | review; sweep 1 (paper 5) | (c) as empirical result | **Kept** as an empirical result on this log; the compiler is paper 5's and is not claimed (cited as a component). | No run of the compiler on this log re-deriving the per-category rule found. |
| Item 6, coverage matrix | review; sweep 1 (Outmazgin and Soffer) | (c) as artifact; (b) concept | **Accepted.** The detectability principle moves to "Not claimed as new" (new paragraph "Detectability limits of event logs"); item 6 reworded to the registered per-defect-class matrix. | Outmazgin and Soffer 2013 establish that some workaround types leave no trace in event logs. |
| Related-work sentence | review; sweeps 1 and 2 | rewording endorsed by all three | **Accepted.** "the evidence it relied on" becomes "the evidence reconstructed from the event log at clearing time". | The design reconstructs evidence; it does not establish what the original decision-maker consulted. |
| Deviation-to-outcome paragraph, missing source | review; sweep 2 | source supplied | **Applied.** Peleg, Soffer and Ghattas 2008 cited with its verified abstract sentence; "(No source cited yet.)" removed. | The review checked the quote; the builder verified it on 2026-10-14 (D-A1-0c). |
| Remaining sweep candidates (Declare for item 1; paper 5 for items 1 and 5) | sweep 1 | components | **Cited as components; no change to the claims.** | As item 1 and item 5. |

**Re-registration: none required.** No finding changes the claim text of
CLAIMS.md, `prereg/p7-v1.md` (section 5 or any other), a predicate, a pattern,
the ERP view template or the column mapping. The registration stays `p7-v1`,
tag `prereg-p7-v1` on `e239864`.

**Files changed in this session:**
- `review-secondary/A1-fence-review.md` and `review-secondary/A1-fence-review.attestation.md` (new; the review, unedited).
- `NOVELTY.md`: intro; "Not claimed as new" (four new paragraphs, the Porter sentence moved, the deviation-to-outcome paragraph cited); Claimed items 2, 4 and 6 replaced as above; the related-work sentence; the Fence status table. Items 1, 3 and 5 unchanged.
- `CLAIMS.md`: status column only, C1 to C13 from `unregistered` to `registered`, per the file's own vocabulary (the tag exists). No claim text changed.
- `prereg/DEVIATIONS.md`: its last line, a log update ("p7-v1: tagged `prereg-p7-v1` on e239864. No deviations."), not a registered item.
- `verified-citations.json`: the record `palma-business-compromise-2026` now carries status "verified" for the paper's own content, read on 2026-10-14; the "mismatch" with the second sweep's description is kept in its `sweep_check`, as for the other records. NOVELTY.md cites only records with status "verified".
- `review-secondary/A1-fence-packet.md`: rebuilt from the updated NOVELTY.md, with a note that the review is complete.
- `DECISIONS.md`: this entry.

Unchanged: `prereg/p7-v1.md`, `prereg/outcome-patterns.yaml`,
`prereg/erp-view-template.txt`, `prereg/column-mapping.yaml`,
`prereg/data.lock`, `COVERAGE.md`, `engines.lock`.

Phase A1 is closed.

## D-C0-1 E0 run 1: two stop conditions fire; E1 blocked (2026-10-18)

The author started C0. `experiments/e0.py` (tested on the fixture,
`tests/test_e0.py`) ran on `data/BPI_Challenge_2019.xes` (SHA-256 as
registered) in 1 min 50 s, with no pipeline error. Outputs, committed as run 1:
`results/e0/run-1/e0-report.json`, `e0-lines.txt` (the 500 lines drawn),
`e0-timing.json`, and `e0-timestamp-tail.json` (event counts past a few
dates, taken after the stop to inform the amendment).

**Stop conditions (prereg/p7-v1.md section 2.2):**

| condition | registered rule | E0 value | result |
|---|---|---|---|
| creation events in window | at least 50% in 2018 | 251,352 of 251,734 (99.85%) | clear |
| T_end | not after 2019-12-31T23:59:59Z | 2020-04-09T21:59:00Z | **fires** |
| mapped attributes present | every attribute in the mapping in the log | case attribute `Doc. Category name` absent; the log has `Purch. Doc. Category name` | **fires** |
| undefined category | at most 1% of lines | 0 of 251,734 | clear |

**What the log shows behind the two stops.** Timestamps: 45,128 events in
January 2019, then 9 events on or after 2019-02-01 (2 in February, 2 in April,
1 in October and 2 in December 2019, 2 in April 2020); 319 events before 2018.
The latest timestamp is set by two outlying events; with it, no framed line
has an incomplete outcome window (frame status count 0), which is the failure
the stop guards against. Attribute: the 4TU record page names the case
attribute `Doc. Category name`; the log names it `Purch. Doc. Category name`.
The engine never reads this field (`engine_fields` in the mapping).

**Other C0 observations, reported as registered (not stops):** every activity
name in `prereg/outcome-patterns.yaml` occurs in the log, including those
marked `unverified`; the flag-derived category agrees with the `Item Category`
string on every line (2-way 1,044; 3-way after receipt 15,182; 3-way before
receipt 221,010; consignment 14,498); every mapped event attribute is present;
on the 500 E0 lines (398 analysed clearings) the pipeline completes, and
`Delete Purchase Order Item`, `Change Quantity`, `Cancel Goods Receipt`,
`Vendor creates debit memo` and `Record Subsequent Invoice` do not follow any
of these 398 clearings within W, which E0's metric asks to report. Activities in
the log that no registered list names are listed in the report (among them
`Record Service Entry Sheet`, 164,975, and `Vendor creates invoice`, 219,919).

**Consequence.** As registered, E1 does not start. The registration must be
amended and re-tagged as p7-v1.1 by the author, then E0 drawn again under the
amended frame (run 1's draw used the out-of-range T_end, so its framed set is
not the v1.1 frame). Nothing under `prereg/` was changed. The amendment's
content is the author's decision; no fix is applied here.

## D-C0-2 Author confirmations and E0 observations (2026-10-19)

**(a) Human hold.** The author confirms the D-B-1 reading: a clearing recorded
before the first invoice receipt counts as a release by people (it is a D3
defect, not a hold). p7-v1.1 states it in section 3.6.

**(b) Observed at E0 run 1 and not acted on.** Five of the seven registered
outcome activities followed none of the 398 pilot clearings within W;
`Record Service Entry Sheet` (164,975 events) and `Vendor creates invoice`
(219,919) appear in no registered list; D1 failed on 1 of 398 clearings. No
predicate, pattern, template or mapping semantics change on these observations
(brief section 10: no tuning after seeing the log); they are reported as
registered.

**(c) Amendment p7-v1.1.** `prereg/p7-v1.1.md` is a copy of the tagged v1 with
five edits: header (id, status, supersedes, changes from v1); section 2
observation end (the T_end rule); section 2.2 (one sentence recording run 1);
section 3.6 (the sentence in (a)); section 12 (the tag `prereg-p7-v1.1`).
`prereg/p7-v1.md` is unchanged. `prereg/column-mapping.yaml`: `Doc. Category
name` renamed `Purch. Doc. Category name`. `prereg/DEVIATIONS.md` records the
three changes.

The v1.1 justification sentence ("The threshold is under one per cent of the
log's median monthly event count") is as the author wrote it. The builder
checked it against the timestamps (counts only): over the 13 months that carry
the log, January 2018 to January 2019, the 2018 median monthly count is
139,879.5 and 1,000 is 0.71% of it; over all 47 calendar months with at least
one event the median is 7. The sentence holds under the first reading only;
flagged to the author before the tag.

**(d) Engine for v1.1.** `observation_end` in `src/p2p_replay/replay.py`
implements the v1.1 rule (last calendar month in UTC with at least
`T_END_MONTH_MIN_EVENTS` = 1,000 events; T_end its latest timestamp; events
after it dropped and counted). `replay_log` and the E0 runner exclude events
after T_end from every computation (`Case.truncated`); the CLI's frame counts
carry `t_end`, `t_end_month` and `dropped_events_after_t_end`, and take
`--min-month-events` so that a small log can run (C13; the registered value is
the default). `log_end` (latest timestamp of any event) is kept only for E7,
whose T_end' section 8 leaves unchanged. Code that names the registration now
points at `prereg/p7-v1.1.md`. Tests at the registered threshold (1,000 events in
a month followed by a sparse tail) and on the K count (a clearing after T_end
does not count toward K). `make test` 110 passed; `make lint` clean;
`make mutate`: 1,471 mutants, 1,380 killed, 0 without a covering test, kill
score 0.9381 (gate 0.85, passed).

**(e) E0 run 2 under v1.1 (2026-10-19).** `python -m experiments.e0 --out
results/e0/run-2`, seed 20261201, 2 min 25 s, no pipeline error. All four stop
conditions clear: creation events in window 251,352 of 251,734; T_end
2019-01-18T13:34:00Z (month 2019-01, the last with at least 1,000 events), not
after 2019-12-31; every mapped attribute present; undefined category 0 of
251,734. Events after T_end excluded: 9 (latest timestamp in the log
2020-04-09T21:59:00Z).

Frame status counts (251,734 lines): no creation 0; consignment 14,498;
undefined category 0; zero or missing value 1,887; more than 12 clearings 78;
outside window 376; incomplete outcome window 53,731; framed 181,164.

E0 drew 500 of the 181,164 framed lines (424 analysed clearings). Run 1's lines
(`results/e0/run-1/e0-lines.txt`) are superseded by run 2's draw:
`results/e0/run-2/e0-lines.txt` is the E0 set removed from every later
estimate.
