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

**Addendum.** (2026-10-28) The sweep was run on Perplexity Computer; the author had selected DeepSeek 4.0 Pro on the platform. A later session on the same platform (the round-1 machine review, `review-secondary/D1-review-perplexity.md`) reports its model as Claude Opus 5.5 and states that it produced this sweep. The model that served the sweep cannot be confirmed. The file name and its SHA-256 are unchanged.

**Addendum.** (2026-10-30) In the same Perplexity Computer session, after the round-1 review, the platform identified the model of the 2026-10-14 sweep as DeepSeek V4 Pro and the model of the round-1 review as Claude Opus 5.5 (source: `review-secondary/D2-review-perplexity.md`, the Acknowledgements row). Both statements are now on record, in order: first that the round-1 session produced this sweep (2026-10-28 paragraph above), then that DeepSeek V4 Pro served it. The file name and its SHA-256 are unchanged.

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

Settled by the author before the tag (2026-10-20): the sentence now reads
"under one per cent of the median monthly event count over calendar 2018",
and the title line of `prereg/p7-v1.1.md` reads "Preregistration p7-v1.1".
No rule, number or threshold changed.

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

## D-C-1 E1 to E3 run (2026-10-22)

**What ran.** E1 (`experiments/e1.py`), E2 (`experiments/e2.py`) and E3
(`experiments/e3.py`) on `data/BPI_Challenge_2019.xes` (SHA-256 as registered,
recorded in `results/e1/exclusions.json`), on base commit `d8cdb2d` (tag
`prereg-p7-v1.1`) with the runners committed in this session; `src/` is
unchanged since the tag, so the mutation gate was not re-run. No model call.
Shared analysis code is `experiments/common.py`; the SHA-256 of every runner
and engine source file at run time is in `results/reproducibility.json`.

**Run times.** Run A (written to `results/`): E1 4 min 06 s, E2 28 s,
E3 29 s. Run B (`out/repro/run-b/`): E1 3 min 40 s, E2 25 s,
E3 30 s. E6 timing (`results/e6/timing-e1.json`): replay of the full
E1 over three further runs 2 min 34 s, 2 min 38 s, 2 min 33 s; median 2 min 34 s.

**Double run.** `experiments/repro.py` ran E1, E2 and E3 twice from the log and
compared every file they write: all 16 files byte-identical between run A and run B. The three E6 runs of E1 wrote
byte-identical files: yes.

**Holm deferred.** The Holm adjustment over the registered five-test family
(H1, H2, H3, H4-Jev, H4-Haiku; alpha 0.05) is applied once
H4-Jev and H4-Haiku exist, after E4. `results/e2/hypotheses.json` holds raw
one-sided p-values for H1 to H3 only, and its `holm` field says so.

**For the author (reported, nothing changed).** H3: the D5 defect group has
0 analysed clearings and the D5-unknown
exclusion 0, so the registered H3
statistic is not computable (defect group has no analysed clearings);
`results/e2/hypotheses.json` says so and carries no p-value for it. Across the
whole log no `Clear Invoice` actor equals an actor of the line's earliest
creation, and the clearings recorded with actor `NONE` lie on lines outside the
frame or after the outcome horizon. Coverage check: every detected row fired:
no; not fired: D5 (same actor created and cleared).
Human hold by gate status at t*: 47,597 classified
lines are held_unknown at t* (no failed predicate, at least one unknown; at a
t* that is not a clearing D5 is unknown, having no clearing actor), and their
human hold rate is 1.0. Under this reading a line
with no clearing within W can be defective or held_unknown but never clean, so
the defective and clean rates are read with that in mind. How E4 treats such lines
is the author's decision before E4.

**Pipeline readings (no registered item changed).**

- numpy is added as a pinned dependency (`numpy==2.3.4`, extras `dev` and
  `analysis`): section 5 registers the `numpy.random.Generator` (PCG64).
- Bootstrap clusters are the purchase documents of the analysed clearings,
  sorted by the id the evidence set carries (the first 16 hex digits of its
  SHA-256, section 3.9), so every interval can be recomputed from the committed
  evidence set. Each bootstrap starts one generator seeded 20261201 and draws
  B resamples in order; every statistic of a runner uses the same resamples.
  Counts and values (integer cents; the log's values carry at most two
  decimals, checked) are summed exactly. Percentile interval: 2.5 and 97.5
  (numpy linear). The H1 to H3 SE is the standard deviation (ddof 1) of the
  bootstrap differences.
- Shares per defect class use every analysed clearing as denominator; the
  number of clearings to which each class applies is reported beside them
  (D1 and D2 classes apply to 3-way categories). "D1 class" is the absent
  receipt and "D2 class" the stale receipt of section 3.3.
- Strata: quartiles are numpy linear quantiles over framed lines (E0 lines
  removed); vendor activity is the number of framed lines of the line's
  vendor, with quartiles over framed lines; a value at a cutpoint falls in the
  lower quartile.
- Category cross-check (3.1): a line disagrees when its `Item Category` string
  is not the record's string for the flag-derived category (`3-way match,
  invoice after GR`, `3-way match, invoice before GR`, `2-way match`,
  `Consignment`); counted over all lines and over framed lines.
- H2 excludes clearings with D4 unknown, and counts them, as H3 does for D5.
- Human hold rate on defective and clean lines (E3): a line's status is the
  gate verdict at the E4 decision point t* of section 7. At a t* that is not a
  clearing (first invoice receipt + W) there is no clearing actor, so D5 is
  unknown and such a line cannot be clean. This reading also fixes which lines
  E4 can sample as clean; it is flagged to the author before E4.
- The evidence-set sample (3.9) is `random.Random(20261201)` over the evidence
  set sorted by hashed line id and t_c.

**Exclusion counts** (generated from `results/e1/exclusions.json`):

| step | status | lines |
|---|---|---|
| lines in the log | | 251,734 |
| 2.1 (1) no Create Purchase Order Item | `no_creation` | 0 |
| 2.1 (2) consignment | `consignment` | 14,498 |
| 3.1 category undefined by the flags | `undefined_category` | 0 |
| 2.1 (3) zero or missing line value | `zero_or_missing_value` | 1,887 |
| 2.1 (4) more than K = 12 clearings | `more_than_k_clearings` | 78 |
| 2.1 (5) outside the window | `outside_window` | 376 |
| 2.1 (5) failing the frame condition | `incomplete_outcome_window` | 53,731 |
| framed | `framed` | 181,164 |
| E0 lines removed (section 2) | | 500 |
| framed lines after E0 removal | | 180,664 |
| analysed clearings | | 155,534 |
| events after T_end (2019-01-18T13:34:00+00:00) excluded | | 9 |

## D-C-2 Author decisions before E4 (2026-10-25)

The author's decisions, final; recorded here with their reasons and logged as
deviations in `prereg/DEVIATIONS.md` (A, B) or as a status correction there (C).

**A. H3 convention.** H3 is not computable: the D5 defect group is empty
(0 analysed clearings fail D5, D-C-1). The Holm family stays at five tests
and H3 enters it with p = 1. C5 will read "inconclusive: defect class has zero
incidence in this log" at the end of Phase C. Reason: the hypothesis cannot be
tested on this log, and p = 1 is the conservative convention.
Chosen after the raw p-values of H1 (0.000113) and H2 (6.96e-08) were known and
before any H4 value existed.

**B. D5 at a decision point that is not a clearing.** At a t* that is not a
clearing (first invoice receipt + W, section 7), D5 is not applicable and counts
as pass: the predicate asks whether the decider is the line's creator, and at a
replayed decision the decider is the gate or the model. Reason: a definitional
gap in section 7. Under the literal reading (D5 unknown, D-C-1) a line held by
people can never be clean: 1 of 91,178 clean lines
are held, against 47,597 held-unknown lines all held
(rate 1.0), so the human arm on clean lines would be degenerate by
construction. B changes line status at t* for E3's human-hold slot and for the
E4 sample; it changes no predicate at an actual clearing (E1 and E2 untouched).
Decided before any E4 call.

**C. Status line.** `prereg/DEVIATIONS.md`: "p7-v1.1: no deviations (pending
tag)" becomes "p7-v1.1: tagged `prereg-p7-v1.1` on d8cdb2d."

**Applied (2026-10-25).** `src/p2p_replay/replay.py` gains `verdict_at_decision_point`
(and `contract.decide` an optional `not_applicable` set): at a t* that is not a
clearing D5 is not applicable under B, at an actual clearing the registered
contract is unchanged. E1 keeps the literal status in `lines.jsonl.gz` and
writes the status under B to the new file `results/e1/lines-t-star-amended.jsonl.gz`.
Checks (`results/checks-d-c-2.json`, `scripts/recheck_d_c_2.py`): E1 re-run from the
log, all 9 committed E1 files byte-identical: yes;
E2 re-run, all 2 files byte-identical: yes;
E3 run twice, all 5 files byte-identical: yes.
`results/e3/human-hold.json` carries both readings, `registered_literal_reading`
and `amended_reading_D-C-2` (as does `results/e3/confounders.json` for its line
tables). Classified clean lines at t*: 91,178 under the literal reading,
138,775 under B; held-unknown: 47,597 and
0. Human hold rate on defective lines 0.3483,
on clean lines 0.000011 (literal) and 0.3430 (B).
Mutation gate (`make mutate`, `results/mutation.json`): 1,526 mutants,
1,432 killed, 94 survived, 0 without a covering
test; kill score 0.9384 (gate 0.85, passed).

## D-C-3 E4 run (2026-10-25)

**Sample (section 7, D-C-2 B; `results/e4/sample-frame.json`).** Framed lines after E0
removal 180,664; status at t* under B: defective 18,006,
clean 147,240, held-unknown 0, no invoice receipt 15,418.
Eligible: 18,006 defective, 147,240 clean. Drawn:
1,000 defective and 1,000 clean (shortfall 0 and
0), from 2,000 purchase documents. The draw was committed and
pushed before any call. Human arm from the log on these lines: unclassified 152.

**Families.** Statuses, invalid replies (after the one re-request), H4 and spend
(`results/e4/arms.json`, `results/e4/h4.json`):

| family | status | lines | invalid | hold rate, defective | hold rate, clean | d | p_TOST | kappa with gate | spend USD | USD per decision |
|---|---|---|---|---|---|---|---|---|---|---|
| jev | COMPLETE | 2,000 | 0 | 1.0000 | 0.5300 | 0.4700 | 1 | 0.4700 | 0.0446 | 0.000022 |
| haiku | COMPLETE | 2,000 | 0 | 0.9960 | 0.5730 | 0.4230 | 1 | 0.4230 | 0.7353 | 0.000368 |

People (from the log): hold rate on defective lines 0.3300, on clean
lines 0.3397. Gate: holds every defective line and allows every clean one.

**Spend.** Total USD 1.5698 against the cap of USD 60
(`results/e6/cost.json`): e4/haiku USD 0.7353; e4/jev USD 0.0446; e4-exploratory/haiku USD 0.7422; e4-exploratory/jev USD 0.0477.

**Holm over the five-test family** (alpha 0.05; H3 enters with p = 1, D-C-2 A;
written to `results/e2/hypotheses.json` under `holm` and to `results/e4/h4.json`):

| test | p raw | rank | multiplier | p Holm | below alpha |
|---|---|---|---|---|---|
| H2 | 6.96e-08 | 1 | 5 | 3.48e-07 | yes |
| H1 | 0.000113 | 2 | 4 | 0.000453 | yes |
| H3 | 1 | 3 | 3 | 1 | no |
| H4-Haiku | 1 | 4 | 2 | 1 | no |
| H4-Jev | 1 | 5 | 1 | 1 | no |

**Double run.** The E4 analysis run twice from the committed responses: byte-identical:
yes (`results/e4/double-run.json`). Exploratory timeline arm ran (labelled exploratory, never in Holm): jev COMPLETE (2,000 lines, 0 invalid), haiku COMPLETE (2,000 lines, 0 invalid); results in `results/e4-exploratory/`; analysis double run byte-identical: yes.

**Pipeline readings (no registered item changed).**

- Jev request. System One answers typed questions about a state; it has no free-text reply,
  so the registered template's JSON reply cannot apply to it. The view's task sentences
  (up to the reply-format sentence) are the state's `context`, the ERP record its `record`,
  and the question is one `choice` with labels `clear` and `hold`; `decision` is the selected
  label and `p_hold` the probability of `hold`. A reply without a valid choice or a `hold`
  probability in [0, 1] is invalid; a 422 is re-requested once, as an invalid reply. Model
  alias `jev-latest`; MODEL_VERSION_CHANGED for Jev means a returned model other than the
  first one it returned.
- Registered sample order: the sample sorted by hashed line id (field `order`). Line ids
  are the hashed ids of the evidence set, as for every E1 to E3 output (D-C-1).
- Draw: eligible lines sorted by hashed id, shuffled once with `random.Random(20261201)`, then
  taken in that order while the status x stratum quota is open and the purchase document is
  unused. Stratum quartiles are those of E1 (framed lines).
- Lines whose t* (first invoice receipt + W) falls after T_end stay in the frame as section 7
  defines it; their view is built from events up to T_end. Count in the sample:
  150.
- Hold rates, kappa and released value use valid replies only; an invalid reply counts as
  neither hold nor clear. The human arm uses classified lines only (3.6).
- Expected correctives: a released defective line carries the E2 O rate at W = 60 of the H1
  defect group if D1/D2 fails, else of the H2 defect group if D4 fails; lines failing
  neither (D3, D6 or D7 only) have no E2 group and are counted, not imputed.
- Cost: every attempt is charged from the reported token usage at the prices recorded in the
  manifest (paper 6's prices), or at the worst-case bound when no usage is reported;
  retries and re-requests included.
- Exploratory view: the template's task paragraph followed by the line's events up to t*
  (date, activity, value), with no actor, id, company or vendor.

## D-C-4 E5 and E7 run (2026-10-25)

**What ran.** E5 (`experiments/e5.py`) on the E1 evidence set, with paper 5's compiler; the E7
vocabulary check (`experiments/e7_check.py`) and the E7 replication (`experiments/e7.py`) on the
two BPI 2020 declaration logs (SHA-256 as registered, checked by the runner). No model call.

**Compiler.** `authority_compiler.derive_authority_contract` from `sarc-authority-derivation` at
`cfb321ec220e83e81a771a048276571f6edf08fb` (the engines.lock pin, checked by the runner), imported from the
sibling checkout unmodified (package version string `0+unknown` when not
installed); its dependency python-sat at the version of its own `constraints.txt` (pinned in
`pyproject.toml`). The adapter lives in `experiments/e5.py`: per category, one state per distinct
combination of the evidence-set observations (a frozen dataclass, as the compiler's
`participation` module reads states), the candidate context the values each observation takes,
and the three registered losses as predicates over the state. Observations: `receipts`
(uncancelled receipts, read by D1 and D2), `invoices` (D3), `changes` (changes since approval, D4),
`distinct_actors` (D5's recorded value; the evidence set does not carry the creator), `blocks`
(D6), `closed` (D7), and `clearing_ordinal` (the clearing's position among the line's analysed
clearings, from the evidence set's own case_id and t_c; read by no predicate). Losses: L1 pay for
goods not received = the category requires a goods receipt and `receipts <= 0`; L2 pay twice =
`clearing_ordinal > invoices`; L3 pay a changed amount = `changes > 0`. The derived contract is the
set of registered predicates whose observation is in the compiler's minimum-cardinality reduct.

**E5 result** (`results/e5/derivation.json`; the compiler's full output per category in
`results/e5/trace-*.json`):

| category | clearings | states | clearings per loss | minimum-cardinality field set | derived contract | registered contract | result |
|---|---|---|---|---|---|---|---|
| 2-way | 188 | 3 | L1 0, L2 0, L3 4 | changes | D4 | D3, D4, D5, D6, D7 | does not reproduce |
| 3-way, invoice after receipt | 9,640 | 896 | L1 0, L2 81, L3 1,585 | changes, clearing_ordinal, invoices | D3, D4 | D1, D2, D3, D4, D5, D6, D7 | does not reproduce |
| 3-way, invoice before receipt | 145,706 | 758 | L1 692, L2 1,390, L3 15,568 | changes, clearing_ordinal, invoices, receipts | D1, D2, D3, D4 | D1, D2, D3, D4, D5, D6, D7 | does not reproduce |

Each category has a single minimal reduct (`minimal_reducts` in the slot). No declared loss reads
the observations of D5, D6 or D7, so they never enter a sufficient set; L2 needs
`clearing_ordinal`, an observation no registered predicate reads.

**E7 vocabulary** (`results/e7/vocabulary.json`). Registered names absent from both logs:
none. Absent per log: domestic: `Declaration FINAL_APPROVED by DIRECTOR`, `Declaration REJECTED by DIRECTOR`; international: none; each
is reported with a zero count and stays in its list. Every attribute the registered bpi2020
mapping names is present in both logs: yes.

**E7 results** (`results/e7/`; descriptive, secondary, no p-value, not in the Holm family):

| log | cases | payments | excluded after T_end' - W | units | T_end' |
|---|---|---|---|---|---|
| domestic | 10,500 | 10,044 | 2 | 10,042 | 2019-06-17T15:30:58+00:00 |
| international | 6,449 | 6,187 | 0 | 6,187 | 2020-05-09T22:00:00+00:00 |

Predicates: domestic: D1' fail 2, unknown 0, D2' fail 2, unknown 0, D3' fail 0, unknown 2; international: D1' fail 0, unknown 0, D2' fail 0, unknown 0, D3' fail 0, unknown 0; pooled: D1' fail 2, unknown 0, D2' fail 2, unknown 0, D3' fail 0, unknown 2. Payments with at least one failed predicate: domestic 2 of 10,042 payments (value share 0.0001); international 0 of 6,187 payments (value share 0.0000); pooled 2 of 16,229 payments (value share 0.0000).

| scope | predicate | failing payments | O' rate | all-pass payments | O' rate | difference | 95% interval | H1 shape |
|---|---|---|---|---|---|---|---|---|
| domestic | D1' | 2 | 0.5000 | 10,040 | 0.0000 | 0.5000 | [0.0000, 1.0000] | no |
| domestic | D2' | 2 | 0.5000 | 10,040 | 0.0000 | 0.5000 | [0.0000, 1.0000] | no |
| domestic | D3' | 0 | n/a | 10,040 | 0.0000 | n/a | n/a | no |
| international | D1' | 0 | n/a | 6,187 | 0.0000 | n/a | n/a | no |
| international | D2' | 0 | n/a | 6,187 | 0.0000 | n/a | n/a | no |
| international | D3' | 0 | n/a | 6,187 | 0.0000 | n/a | n/a | no |
| pooled | D1' | 2 | 0.5000 | 16,227 | 0.0000 | 0.5000 | [0.0000, 1.0000] | no |
| pooled | D2' | 2 | 0.5000 | 16,227 | 0.0000 | 0.5000 | [0.0000, 1.0000] | no |
| pooled | D3' | 0 | n/a | 16,227 | 0.0000 | n/a | n/a | no |

**Double runs.** E5 twice, byte-identical: yes
(`results/e5/double-run.json`); E7 vocabulary check and replication twice, byte-identical:
yes (`results/e7/double-run.json`).

**Pipeline readings (no registered item changed).**

- The three losses are expressed over the evidence set as above. L1 is a loss only where the
  category requires a goods receipt (on a 2-way line no receipt is recorded by design). L2 has no
  single evidence-set field; it is expressed with the clearing's position on its line, derived from
  the evidence set's own line id and clearing time, against the invoice count. The compiler needs
  every loss to be a function of the candidate observations, so that position is a candidate.
- Identical observation vectors are one state; the number of clearings each stands for is in the
  trace. The compiler's partitions, core and reducts do not depend on repeats.
- E7 paid value is the case attribute `Amount`, read beside the registered bpi2020 mapping (which
  names no amount field) for the value share only; every payment of a case carries its case's
  amount; sums use `math.fsum` (the anonymised amounts carry many decimals).
- E7 bootstrap clusters are declaration cases, identified by the hash of log name and case id so
  that the pooled scope keeps the two logs' cases apart; sorted by that hash.
- T_end' is the latest timestamp of each log (section 8, unchanged by v1.1).

## D-C-5 Phase C closed (2026-10-25)

Every Phase C experiment of the registration (E0 to E7) has run; every figure is in a slot file
under `results/` (index: `results/README.md`). Claim statuses, set from the slots by
`scripts/claim_statuses.py` (`CLAIMS.md`):

| claim | status | evidence |
|---|---|---|
| C1 | supported | `results/e1/exclusions.json`, `results/e1/evidence-set.jsonl.gz`, `results/mutation.json` |
| C2 | supported | `results/e1/exposure.json`, `results/e1/exposure-by-stratum.json` |
| C3 | supported | `results/e2/hypotheses.json` |
| C4 | supported | `results/e2/hypotheses.json` |
| C5 | inconclusive: defect class has zero incidence in this log | `results/e1/coverage-check.json`, `results/e2/hypotheses.json` |
| C6 | not supported for both families | `results/e4/h4.json` |
| C7 | supported | `results/e3/gate-held.json`, `results/e3/verdict-by-outcome.json`, `results/e3/lag-bands.json` |
| C8 | supported | `results/e4/arms.json` |
| C9 | not supported: 2-way does not reproduce; 3-way, invoice after receipt does not reproduce; 3-way, invoice before receipt does not reproduce | `results/e5/derivation.json` |
| C10 | supported | `results/e6/timing-e1.json`, `results/e6/cost.json` |
| C11 | inconclusive | `results/e7/comparisons.json` |
| C12 | supported; D5 class zero incidence | `results/e1/coverage-check.json` |
| C13 | supported for the internal double runs; external reproduction pending (FINAL-AUDIT item 11) | `results/reproducibility.json`, `results/e4/double-run.json` |

**Deviations under p7-v1.1** (`prereg/DEVIATIONS.md`): H3 convention (2026-10-25); D5 applicability at a non-clearing decision point (2026-10-25).

**Spend.** USD 1.5698 of the USD 60 cap, E4 and the exploratory
arm together (`results/e6/cost.json`).

No registered item changed after the tag prereg-p7-v1.1 except as logged in prereg/DEVIATIONS.md.

## D-D-1 Draft v0.1 (2026-10-25)

**Ported from paper 5** (sarc-authority-derivation at the engines.lock pin; D-A0-3):
- The typed-numeral lint, `lint/typed_numerals.py`, from paper 5's `checkers/typed_numerals_lint.py`: the
  same strip-then-allowlist design. Paper 5 marks filled values inside the draft; here the paper is
  generated from `paper/template.md`, so the lint checks the template (any numeral outside a
  placeholder) and the generated `paper/paper.md` (any numeral outside the spans recorded in
  `results/filled-template.json`). Registered constants are allowlisted by literal value, each
  citing the registration section that fixes it (`REGISTERED` in the lint).
- The gate layout, `scripts/gates.py` and `make gates` (report in `out/gates/report.json`). Paper 5's
  G1 to G9 are LaTeX release-kit gates (build, token purity, number parity, prose and structure
  parity, disclosure, arXiv sidecar, citations, bibliography). Here G1 to G9 are the release list of
  the builder prompt (tests, lints, mutation, regeneration, claims, secrets, data and pins, package,
  paper), and paper 5's paper checks (build, token purity, number parity between source and typeset
  paper, verified references) sit inside G9.

**Gate report at v0.1** (`make gates`, full, with the log replays; passed: yes):

| gate | status | waiting on |
|---|---|---|
| G1 tests | waiting | CI run ids on Python 3.11 and 3.12 for the release commit: waiting on Phase E |
| G2 lints | pass |  |
| G3 mutation | pass |  |
| G4 regeneration | waiting | external reproduction from a clean clone (FINAL-AUDIT item 11): waiting on Phase F |
| G5 claims | pass |  |
| G6 secrets | pass |  |
| G7 data and pins | pass |  |
| G8 package | waiting | fresh-venv install and smoke test (make package-smoke-test, FINAL-AUDIT item 2): waiting on Phase E |
| G9 paper | waiting | PDF build: no LaTeX engine (tectonic, latexmk, pdflatex, xelatex) in this environment |

G4 files that differ from `results/` or the committed paper: none.

The first full gate run failed three gates, each on a real defect of this session's work, fixed in
`fa0c5ac`: G4 found that Figures 2 and 4 had been committed before a layout fix (legend and titles)
and no longer matched their regeneration; G8 built without isolation in a venv that has no
setuptools; G9 counted numerals inside HTML comments, which pandoc does not typeset, and read
ordinary LaTeX braces as template syntax. A gate whose checks pass but which still has an item for a
later phase now reports "waiting" rather than "pass".

**Lints on the draft.** Terminology: clean on `paper/paper.md`. Typed numerals: template
clean, generated paper clean
(114 filled spans). Proof status: clean. Placeholders filled:
18 block, 23 citation, 73 value; the draft has 7,628 words.

**Figures** (`scripts/figures.py`, deterministic SVG and PDF in `paper/figures/`): fig1-exposure, fig2-hold-rates, fig3-lag-bands, fig4-verdict-outcome.

**PDF.** `paper-tex/main.tex` is written by pandoc from `paper/paper.md` (`scripts/build_tex.py`,
`make paper`). No LaTeX engine is installed in this environment, so the PDF waits for one; G9 reports
it as waiting.

**Readings taken while writing (no registered item changed).**
- The human-hold table of Section 5.3 shows both readings as rows of one table (literal, then
  amended by D-C-2 B), with the decision named in the sentence before it.
- Tables whose cells say "defective" carry "predicate" in their header ("lines with a failed
  predicate"), so the terminology rule (defect only for a failed predicate) holds in every table.
- The References section is exempt from the terminology lint (`lint/terminology.py`): it quotes
  cited titles verbatim, and one verified title (Kadir et al. 2025) contains a banned word. The
  paper's own prose is linted in full.
- The coverage table is `COVERAGE.md` verbatim. Its D1' row reads "no final approval event before
  the payment event", while section 8 of the registration and the engine define D1' as no event of
  the approval list; the paper shows the file as registered and does not reword it. Raised for review
  round 1.
- An E7 sentence that payment is the last event of a declaration is not in the draft: the check
  behind it was run during session 3 and reported to the author, but no slot holds it. The draft
  states the slot values instead (failing payments, and O' after all-pass payments).
- Small design counts fixed by the registration (seven predicates, two model families, three losses,
  three runs) are written as words; every result count is a filled value.
- Company and vendor strata are left out of Appendix D (registration section 2.3: their ids appear
  only in machine output); they stay in `results/e1/exposure-by-stratum.json`.
- P-values below 0.001 are written as a mantissa times a power of ten; p-values at or above 0.9995
  are written as 1.
- In-text citations name the first author's surname and year; the dataset records are cited as by
  Boudewijn van Dongen on 4TU.ResearchData, with DOI and licence from `prereg/data.lock`.

## D-D-2 Round-1 adjudication (2026-10-28)

Three round-1 reviews of draft v0.1 (packet `review-secondary/D1-review-packet.md` at `76264dd`):
Eduardo Arana (external), and two machine reviews, AI support (ChatGPT; Perplexity Computer, model as
it states it: Claude Opus 5.5). Each is committed unedited with its attestation and SHA-256. The
decisions are the author's, applied as written: 24 accepted, 5 rejected with the reason.

| # | finding | raised by | class | decision | reason | where applied |
|---|---|---|---|---|---|---|
| 1 | "Every clearing" is broader than the analysed population | Arana; ChatGPT; Perplexity | (a) wording | accepted | the analysed clearings are those left after the registered exclusions and the E0 removal (results/e1/exclusions.json) | Abstract, Section 1: "every analysed clearing", with the count and a pointer to the exclusion table |
| 2 | "Relied on" says what the decider used; the design reconstructs the log at t_c | Perplexity | (a) wording | accepted | the evidence is reconstructed, not what the decider consulted (D-A1-1) | Abstract, Section 5.1, Section 8: "was made on evidence that failed"; CLAIMS.md C2 stays as registered and is read as "made on" |
| 3 | The E4 line status rests on D-C-2 B, decided after E3; the Abstract and Section 2 do not say so | Perplexity | (c) disclosure | accepted | the decision preceded every model call; the commit order is the evidence | Abstract, Section 2; Section 4 cites the D-C-2 commit `7aea13f` before the first response commit `a475068` |
| 4 | "Amended once ... before any estimate" omits the two later deviations | Perplexity | (a), (c) | accepted | the H3 convention and the D5 reading came after E2 and E3 | Section 1: amended once after the pilot (v1.1), with two further deviations decided after E2 and E3 and before E4, all listed in Section 4 |
| 5 | The fence review came after the p7-v1 tag | Perplexity | (a) timing | accepted | the review was run after `prereg-p7-v1` and before `prereg-p7-v1.1` (D-A1-0) | Section 4, Acknowledgements |
| 6 | H3: "this log" and "the person who created its line" overstate; the timing has no source | Perplexity | (a) | accepted | D5 compares with the actor of the earliest creation event, on analysed clearings | Section 5.2: "no analysed clearing was made by an actor of its line's earliest creation event"; the H3 convention cites the D-C-2 commit |
| 7 | "Never clean" is contradicted by the one held clean line; the D-C-2 B parenthesis is too broad | ChatGPT | (a) | accepted | the restriction concerns a t* that is not a clearing | Section 5.3: "a line with no clearing within W can never be clean under the literal reading"; the parenthesis restricted to "at a t* that is not a clearing" |
| 8 | "Holds" reads as the gate acting; "both arms" is ambiguous; spend and exploratory figures lack slots | Perplexity | (a), (b), (e) | accepted | the gate's verdict is a replay; every figure names its slot | Section 5.4: "the gate's verdict holds"; "both families and both views"; spend cites results/e6/cost.json; the exploratory table gets counts and its slot path |
| 9 | "Guard losses" is loss wording | Perplexity | (d), (e) | accepted | no loss claim is made | Section 5.5: "correspond to no declared loss", and one sentence on the three-way match in the narrow sense |
| 10 | Section 6: "every other detected class" is too broad (BPI 2020); the recovery row; the "detected" definition and the stale class | ChatGPT; Perplexity | (a) | accepted | the coverage check covers BPI 2019 only; the stale class uses events after t_c | Section 6: per-class statement for BPI 2019 and for BPI 2020; COVERAGE.md recovery row and definition |
| 11 | "Shows that a different view changes" is causal wording | ChatGPT; Perplexity | (d) | accepted | the exploratory arm has no interval and sits outside the Holm family | Section 7: "under the timeline view the same models held far fewer lines (exploratory, no interval)" |
| 12 | The H2 comparison group is called "clean clearings" in the Conclusion | Arana; ChatGPT; Perplexity | (a) | accepted | H2 compares D4 fail with D4 pass | Section 8: the group names of Section 5.2 |
| 13 | A prevalence statement and the people-arm sentence read as claims about the company | Perplexity | (e) | accepted | the non-claim concerns naming or characterising the company, its subsidiaries or vendors | Section 1: one sentence after the non-claims list |
| 14 | C1 "sufficiency-checked" has no certificate for D1 to D7 | ChatGPT | (a) | accepted | the term means each predicate checks presence, freshness, validity, authority and scope (the SARC-DQ dimensions); it is not paper 5's sufficiency certificate | Section 3 and Appendix B; CLAIMS.md C1 evidence column: results/e1/evidence-set.jsonl.gz and tests/test_properties.py, with results/mutation.json as engine evidence |
| 15 | Papers 1 to 6 are asserted but not cited | Perplexity | (a) | accepted | cite what has a verifiable record; name the rest | Section 1: paper 4 (arXiv:2608.18360) and paper 5 (arXiv:2609.26016) cited, paper 6 as its public repository; papers 1 to 3 have no record found (verified-citations.json) |
| 16 | COVERAGE.md D1' row says "final approval" | Arana; ChatGPT | (a) | accepted | registration section 8: any event of the approval list | COVERAGE.md, logged in prereg/DEVIATIONS.md |
| 17 | COVERAGE.md D6 and D7 rows describe a temporal rule, not the registered counts | ChatGPT | (a) | accepted | registration section 3.2 counts sets minus removals, and deletions plus blocks minus reactivations | COVERAGE.md, logged in prereg/DEVIATIONS.md |
| 18 | "Held by people" is an inferred non-release, not a decision like a model's hold | Arana; Perplexity | (a) | accepted | the log records no hold decision except a payment block | results/e3/human-hold-composition.json; Section 5.4 paragraph on what the human arm measures |
| 19 | Zero D5 failures: are clearing and creation actors separate populations, or is the field unusable? | Perplexity | question | accepted | answered from the log | results/e1/actors.json; Sections 5.2 and 6 worded from it |
| 20 | People and models are compared on different denominators | Arana; ChatGPT; Perplexity | (a) | accepted | the people arm classifies fewer lines (3.6) | results/e4/arms-classified-lines.json, a second table in Section 5.4; the unclassified lines and the eligible-versus-classified counts explained with their slots |
| 21 | Expected correctives: the rate assignment and the lines without an estimate are not stated; the gate's zero | Arana; ChatGPT; Perplexity | (a), (e) | accepted | registration section 7; H1 group first, else H2 | Section 5.4: the convention with the counts from results/e4/arms.json; "held lines go somewhere the log does not show" |
| 22 | Appendix D is not per defect class and shows Wilson, not clustered, intervals | ChatGPT | (a) | accepted | results/e1/exposure-by-stratum.json carries both | Appendix D |
| 23 | Three registered slots are never reported (category cross-check, value fallback, the sample export) | Perplexity | (c) | accepted | registration sections 3.1, 3.4, 3.9 | Sections 4 and 5.1 |
| 24 | E7 intervals discard bootstrap replicates with an empty comparison group, undisclosed | ChatGPT | (c) | accepted (pipeline reading) | retained replicates: 8,685 of 10,000 domestic, 8,696 of 10,000 pooled (results/e7/comparisons.json) | Section 5.7; this entry |
| 25 | "At most t_c" is an unlogged deviation | Perplexity | (c) | rejected | p7-v1 section 2 defines "before t_c" as less than or equal, excluding the clearing | Section 3 cites it |
| 26 | Section 5.5 changed the C9 comparator from the matching rule to D1 to D7 | Perplexity | (c) | rejected | registration section 6, E5: "whether the derived contract equals the category contract in 3.1" | Section 5.5 cites it |
| 27 | Spend-area labels in Appendix D narrow down the industry | Perplexity | (f) | rejected | they are the public log's own strings and the registered strata; the challenge names the sector | Appendix D, one sentence |
| 28 | Lexical hits on "fraud" | ChatGPT; Perplexity | (d) | rejected | the coverage row disclaims the class; the reference title is verbatim | none |
| 29 | D5 "not demonstrated" on this log | Perplexity | (a) | rejected | fixture and engine tests show D5 firing on synthetic lines (tests/test_engine_units.py::test_d5_actors, test_verdict_at_decision_point_d5_off_clearing; fixture line C in tests/test_pipeline.py); the actors slot answers the real question | Section 6 |

**Readings.** CLAIMS.md C2's "relied on" is read as "made on" (the claim text stays as registered).
The C1 clarification is placed in Section 3 and in the paper's claims table (Appendix B); in CLAIMS.md
only the evidence column of C1 changes. The E7 bootstrap convention (a replicate in which either
group is empty is discarded, and the percentiles are taken over the retained replicates) is a
pipeline reading of `experiments/e7.py`, recorded here; the retained counts are in
`results/e7/comparisons.json` (`bootstrap_resamples_used`). The A1 second sweep's attestation and
D-A1-0c carry the platform correction of 2026-10-28; the paper names machine sweeps and reviews by
platform with the model as self-reported.

## D-D-3 Round-2 adjudication (2026-10-30)

**Records.**

- *A1 sweep statements.* The attestation of the A1 second sweep
  (`review-secondary/A1-fence-sweep-deepseek.attestation.md`) and D-A1-0c carry a second dated
  paragraph: in the same Perplexity Computer session, after the round-1 review, the platform
  identified the model of the 2026-10-14 sweep as DeepSeek V4 Pro and the model of the round-1 review
  as Claude Opus 5.5 (`review-secondary/D2-review-perplexity.md`, the Acknowledgements row). Both
  statements are on record, in order; the Acknowledgements say the same.
- *Filled template moved.* `results/filled-template.json` is now `paper/filled-template.json`; its
  readers (the typed-numeral lint, G4 and G9 in `scripts/gates.py`, `tests/test_paper.py`,
  `scripts/fill_paper.py`, `scripts/review_packet.py`, the results and paper READMEs) follow. The
  rule: experiment slots under `results/` never change once committed (new slot files may be added);
  derived records of the paper live beside the paper and regenerate with it.
- *Paper-regeneration test.* Commits `a09c4b1` (D-D-2) and `08d860c` (round-1 slots) fail
  `tests/test_paper.py::test_committed_paper_matches_the_template`: the slots changed before the
  paper was regenerated, and the failing exit code was hidden by a pipe. `b01be29` (draft v0.2)
  passes. The builder's test runs now fail on a failing exit code (`set -o pipefail`).

**Adjudication.** Three round-2 reviews of draft v0.2 (packet `review-secondary/D2-review-packet.md` at
`b01be29`): Eduardo Arana (external), and two machine reviews, AI support (ChatGPT, model as it states it:
OpenAI Codex; Perplexity Computer, model as it states it: Claude Opus 5.5). Each is committed unedited
with its attestation and SHA-256. The decisions are the author's, applied as written: 19 accepted,
2 rejected with the reason. Papers 1 to 3: no record given, so the sentence stays as in v0.2.

| # | finding | raised by | class | decision | reason | where applied |
|---|---|---|---|---|---|---|
| 1 | C1 is supported without evidence of paper 5's sufficiency; Section 3 and Appendix B say each predicate checks all five SARC-DQ dimensions | ChatGPT; Perplexity | (a) | accepted, new evidence | paper 5's sufficiency function (reduct.sufficiency) run on the registered contract per category: sufficient for every declared loss in 2-way; sufficient for L1 and L3 and not for L2 in both three-way categories (L2 reads the clearing's position on its line, which no registered predicate reads); minimal in none; the derived contract is a subset of the registered one in every category (author, 2026-10-30: qualify, C1 stays supported) | results/e5/sufficiency.json; Section 3 and Appendix B (each predicate checks one SARC-DQ dimension, the table; the contract's sufficiency per category and loss, not minimal); C1 evidence column; one sentence in 5.5 (sufficient, not derived) |
| 2 | C9's claim text and status disagree with 5.5's narrow-sense sentence | Perplexity | (a) | accepted, new evidence | C9 stays not supported: the comparison is the registered one (registration section 6, E5); C1 and C9 are tied by one sentence: sufficient, not derived | Section 5.5 |
| 3 | Commit order does not date the model calls (D-C-2 and the H3 convention before any H4 value) | ChatGPT; Perplexity | (a) | accepted, new evidence | the response logs carry sent_utc for every request; the earliest call of each family follows the D-C-2 commit and the sample-draw commit | results/e4/timeline.json; Sections 4 and 5.2 (the commit-order sentences replaced) |
| 4 | Section 5.5: "in the two three-way categories the derived D1 to D4 is the three-way match" | Arana; ChatGPT; Perplexity | (a) | accepted, new evidence | in the after-receipt category the compiler derives D3 and D4 only, because L1 occurs on 0 analysed clearings there (clearings_per_loss in results/e5/derivation.json); a limit of deriving from one log | Section 5.5: before receipt, D1 to D4 and three predicates beyond; after receipt, D3 and D4 and five beyond |
| 5 | D5: 7,941 `Clear Invoice` events carry no actor, yet D5 has no unknown and the Section 6 table shows "n/a" | Perplexity | (a) | accepted, new evidence | the missing-actor clearings all lie outside the analysed set; those on framed lines fall after the horizon T_end - W | results/e1/analysed-clearing-actors.json; Sections 5.2 and 6; the Section 6 table shows the D5 unknown count |
| 6 | E7 intervals rest on fewer than the registered B replicates; recorded in D-D-2, not as a deviation | Perplexity | (b), (c) | accepted, new evidence | retained replicates: 8,685 of 10,000 domestic, 8,696 of 10,000 pooled (results/e7/comparisons.json) | prereg/DEVIATIONS.md, "E7 bootstrap replicates with an empty group discarded"; Sections 1 and 4 count and list it; 5.7 cites the slot |
| 7 | Expected correctives attributed to registration section 7 | ChatGPT | (a) | accepted, new evidence | the metric is registration section 6 (E4 row); the precedence and the unmatched-group rules are D-C-3 | Section 5.4 |
| 8 | Abstract puts "people held" beside "models held" as the same act | Arana; ChatGPT; Perplexity | (a) | accepted, wording | section 3.6: a people hold is inferred, the log records no hold decision except a payment block | Abstract: "where a hold is an inferred non-release within 60 days, not a recorded decision" |
| 9 | Section 7 compares the people column with the model verdicts as if they were the same act | Arana; ChatGPT; Perplexity | (a) | accepted, wording | the comparison is of outcomes of three deciders, not three acts | Section 7, one sentence: the people column reports what the process did within W |
| 10 | Section 1 counts two deviations after v1.1 | Perplexity | (c) | accepted, wording | DEVIATIONS.md lists four under p7-v1.1 with the E7 entry | Section 1 |
| 11 | 5.7: 16,227 all-pass payments is right only if the 2 D3' unknowns are the 2 that fail | Perplexity | (a) | accepted, wording | they are the same 2 payments (results/e7/unknown-overlap.json, a new slot) | Section 5.7, citing results/e7/unknown-overlap.json |
| 12 | Section 4: no slot path for the category cross-check and the value fallbacks | Perplexity | (b) | accepted, wording | results/e1/category-crosscheck.json, results/e1/value-fallback.json | Section 4 |
| 13 | 5.5: "would be such losses" names undeclared losses | Perplexity | (d) | accepted, wording | the registration declares three losses only | Section 5.5, the parenthesis removed |
| 14 | Papers 4 and 5 are both cited as "Besanson 2026" | Perplexity | (a) | accepted, wording | two records, one author-year | References and in-text: "Besanson 2026a/2026b" (paper 6's repository, the third record of that author-year, becomes 2026c, and the same rule gives the two ICPM 2020 pages 2020a/2020b) |
| 15 | CLAIMS.md C1 still says "(paper 5)" and C2 still says "relied on" | Perplexity | (a) | accepted, wording | claim text stays as registered; the readings are stated beside it | CLAIMS.md "Reading notes" under the table; Appendix B follows |
| 16 | C5 status says "in this log" where 5.2 says "analysed clearings" | Perplexity | (a) | accepted, wording | the zero incidence is over the analysed clearings | CLAIMS.md and Appendix B: "inconclusive: defect class has zero incidence in the analysed clearings" |
| 17 | Acknowledgements record only the Claude statement for the second sweep | Perplexity | (a) | accepted, wording | the platform also identified the sweep's model as DeepSeek V4 Pro | Acknowledgements; the A1 attestation and D-A1-0c (Records above) |
| 18 | COVERAGE.md D1 row describes a temporal rule | Perplexity | (a) | accepted, COVERAGE.md | section 3.2 defines D1 by counts | COVERAGE.md and the paper's coverage table: "receipts minus cancellations at most zero before t_c, on a line whose category requires receipt"; DEVIATIONS.md addendum |
| 19 | D1' class label "paid without final approval" | Arana; ChatGPT; Perplexity | (a) | accepted, COVERAGE.md | D1' fails when no registered approval event exists; final approval is D2' | COVERAGE.md and the paper's coverage table: "paid without an approval event"; DEVIATIONS.md addendum |
| 20 | Lexical hits on "fraud" | Perplexity | (d) | rejected | as in D-D-2: the coverage row disclaims the class; the reference title is verbatim | none |
| 21 | Spend-area labels and a reference title point to the sector | Perplexity | (f) | rejected | as in D-D-2: they are the public log's own strings and the registered strata; the challenge names the sector | none |

**C1 and paper 5's sufficiency.** The author's decision as given read: "per category, the derived
contract is a subset of the registered one, so the registered contract is sufficient for the three
declared losses over the observed states in paper 5's sense, and minimal in none". Before applying it,
the builder ran paper 5's sufficiency function on the registered contract. The subset relation holds in
every category, but it does not imply sufficiency, because the derived field sets of the three-way
categories include the clearing's position on its line, which no registered predicate reads. The
registered contract is sufficient for every declared loss in 2-way, and in both three-way categories
for L1 and L3 but not for L2; it is minimal in none (`results/e5/sufficiency.json`). The author chose
(2026-10-30) to qualify the statement and keep C1 supported: Section 3, Appendix B and the slot state
sufficiency per category and per loss.

**Rule.** Experiment slots under `results/` never change once committed; new slot files may be added.
The analysed-clearing actor count is therefore a new slot (`results/e1/analysed-clearing-actors.json`),
not a field added to `results/e1/actors.json`.

## D-D-4 Round-3 adjudication (2026-10-30)

Three round-3 reviews of draft v0.3 (packet `review-secondary/D3-review-packet.md` at `a75be8d`):
Eduardo Arana (external), and two machine reviews, AI support (ChatGPT, model as it states it:
gpt-6-astra; Perplexity, which names no serving model and quotes the session label GPT-6 Astra). Each
is committed unedited with its attestation and SHA-256. The decisions are the author's, applied as
written: 8 accepted, 2 rejected with the reason.

- Arana: nothing further of substance ("I have nothing further of substance to add within the scope
  of this review").
- ChatGPT: "none found" in all six classes, (a) to (f), with 113 generated scalar
  entries checked against their cited files (its count); every row of "Changes since v0.2" marked yes.
  Its three hostile-reviewer questions are answered in rows 5 to 7.
- Perplexity: the findings below. Of "Changes since v0.2" it marked rows 2 and 8 partly and row 10
  yes for the listed deviations only; these are rows 3, 2 and 1 here. Its three hostile-reviewer
  questions are answered in rows 3, 1 and 6.

| # | finding | raised by | class | decision | reason | where applied |
|---|---|---|---|---|---|---|
| 1 | The Jev reply-template adaptation (typed choice instead of the registered JSON reply) is recorded as a pipeline reading in D-C-3, not as a deviation | Perplexity | (c) | accepted, deviation | the registration makes the companion templates binding and calls any post-tag template change a deviation; the first Jev decision request (2026-10-25 18:42:18 UTC, results/e4/timeline.json) already carries the typed choice; the Haiku family received the template as registered; no result changes | prereg/DEVIATIONS.md, "E4 Jev request format"; Section 1 counts five deviations under v1.1; Section 4 lists it; one sentence in 5.4 |
| 2 | The Abstract calls every people hold an inferred non-release; the measure also includes a recorded payment block | Perplexity | (a) | accepted, wording | 80 of 53,262 people holds involve a payment block (results/e3/human-hold-composition.json) | Abstract: "where a hold is a recorded payment block or, in nearly every case, an inferred non-release within 60 days, not a recorded decision" |
| 3 | C9's "per-category matching rule" and its status "not supported" are not aligned with 5.5 | Perplexity | (a) | accepted, wording | the matching rule is the category contract of section 3.1, the comparator the registration's E5 row fixes; the before-receipt category recovers the narrow three-way match (D1 to D4) | CLAIMS.md reading notes and Appendix B: a C9 note; the status refers to the registered comparison |
| 4 | Section 7: "reported beside every estimate" overstates what the paper shows for 5.2 and 5.3 | Perplexity | (a) | accepted, wording | the per-stratum estimates exist in results/e2/confounders.json and results/e3/confounders.json | Appendix E (H1, H2 and gate by outcome per category, spend area, value quartile, vendor activity quartile and month), pointed to from 5.2, 5.3 and 7 |
| 5 | What substantive assurance C1's sufficiency check adds | ChatGPT | question | accepted, wording | results/e5/sufficiency.json | Conclusion, one sentence: sufficient for "goods not received" and "changed amount", not for "pay twice" in the three-way categories, because no registered predicate reads the clearing's position |
| 6 | Which inferences the people, model and gate comparison supports | ChatGPT; Perplexity | question | accepted, wording | the people column is a process outcome, not a decision at t* | Section 7, one sentence: the only inference the three columns support; no decision quality is inferred for people |
| 7 | What the expected-correctives totals estimate | ChatGPT | question | accepted, wording | E2 rates applied to the lines each arm released, under the stated assignment | 5.4, one sentence: a projection from observed rates onto the sample, not an observed count |
| 8 | Section 6 table: "n/a" for the unknown counts of every predicate but D5 | author (from the D-D-3 report) | (b) | accepted, wording | the evidence set records each predicate's value per analysed clearing | results/e1/predicate-unknowns.json (a new slot); the Section 6 table |
| 9 | Lexical hits on "fraud" (the coverage row and a reference title) | Perplexity | (d) | rejected | as in D-D-2 and D-D-3: the coverage row disclaims the class; the reference title is verbatim | none |
| 10 | Provider names in 5.4 (TypeSafe, Anthropic) | Perplexity | (f) | rejected | methodological attribution of the services the replay called, not the studied company or its vendors | none |

Row 8 was not raised in round 3: the D-D-3 report noted that no slot counted the unknowns of the
predicates other than D5, and the author decided to add one.

## D-D-5 Phase D closed (2026-10-30)

**Review rounds.** Findings are the rows of each adjudication table (round 3 includes one row the
author added, D-D-4 row 8).

| round | draft reviewed | reviewers | findings | accepted | rejected | adjudication | draft produced |
|---|---|---|---:|---:|---:|---|---|
| 1 | v0.1 | Arana (external); ChatGPT, Perplexity (machine, AI support) | 29 | 24 | 5 | D-D-2 | v0.2 |
| 2 | v0.2 | Arana (external); ChatGPT, Perplexity (machine, AI support) | 21 | 19 | 2 | D-D-3 | v0.3 |
| 3 | v0.3 | Arana (external); ChatGPT, Perplexity (machine, AI support) | 10 | 8 | 2 | D-D-4 | v1.0 candidate |

**Slots.** No committed experiment slot under `results/` changed during Phase D (git, from `14842cc`, Phase C closed, to this commit). Under `results/`
only the index (`results/README.md`) changed, and the paper's filled template, which was written there
in Phase D, regenerated with each draft and moved to `paper/filled-template.json` in D-D-3. Slot files
added in Phase D, each with its first commit:

| file | first commit | date |
|---|---|---|
| `results/e1/actors.json` | `08d860c` | 2026-10-28 |
| `results/e3/human-hold-composition.json` | `08d860c` | 2026-10-28 |
| `results/e4/arms-classified-lines.json` | `08d860c` | 2026-10-28 |
| `results/round1-double-run.json` | `08d860c` | 2026-10-28 |
| `results/e1/analysed-clearing-actors.json` | `aad3359` | 2026-10-30 |
| `results/e4/timeline.json` | `aad3359` | 2026-10-30 |
| `results/e5/sufficiency.json` | `aad3359` | 2026-10-30 |
| `results/e7/unknown-overlap.json` | `aad3359` | 2026-10-30 |
| `results/round2-double-run.json` | `aad3359` | 2026-10-30 |
| `results/e1/predicate-unknowns.json` | `d7e72ee` | 2026-10-30 |
| `results/round3-double-run.json` | `d7e72ee` | 2026-10-30 |

**Deviations under p7-v1.1 (5).**

1. H3 convention (2026-10-25)
2. D5 applicability at a non-clearing decision point (2026-10-25)
3. Description corrections in COVERAGE.md, no predicate changes (2026-10-28)
4. E7 bootstrap replicates with an empty group discarded (2026-10-25)
5. E4 Jev request format (2026-10-25)

**Lints and gates.** The terminology, typed-numeral and proof-status lints pass on the v1.0 candidate.
`make gates` (`out/gates/report.json`): 5 pass, 4 waiting, 0 fail.

| gate | status | waiting on |
|---|---|---|
| G1 tests | waiting | CI run ids on Python 3.11 and 3.12 for the release commit: waiting on Phase E |
| G2 lints | pass |  |
| G3 mutation | pass |  |
| G4 regeneration | waiting | external reproduction from a clean clone (FINAL-AUDIT item 11): waiting on Phase F |
| G5 claims | pass |  |
| G6 secrets | pass |  |
| G7 data and pins | pass |  |
| G8 package | waiting | fresh-venv install and smoke test (make package-smoke-test, FINAL-AUDIT item 2): waiting on Phase E |
| G9 paper | waiting | PDF build: no LaTeX engine (tectonic, latexmk, pdflatex, xelatex) in this environment |

**Phase E (release) needs:** CI run ids on Python 3.11 and 3.12 for the release commit (G1); a LaTeX
engine to build the PDF from `paper-tex/main.tex` (G9); the fresh-venv package smoke test (G8,
`make package-smoke-test`); FINAL-AUDIT items 1 to 10; a Zenodo DOI; an arXiv id; the release tag,
which the author sets.

**Phase F needs:** external reproduction from a clean clone (FINAL-AUDIT item 11, G4), which settles
C13's pending part ("external reproduction pending").

## D-E-1 Release preparation (2026-10-30)

Phase E session 1: tooling only. No model call, no change to the paper's wording, to any slot under
`results/` or to any registered file.

**CI.** `.github/workflows/ci.yml` runs on pushes to main and on pull requests: Python 3.11 and 3.12
on ubuntu-latest; install `.[dev]`; `make test` (the sibling-dependent tests skip); `make lint`;
`python preflight.py` (data, keys and siblings absent: it reports and exits 0); `make gates-ci` (G2,
G5, G6, G7, G8; G1, G3, G4 and G9 are marked "not run in CI": they need the log, a TeX engine or the
mutation run). No secret, no data fetch. The workflow was green on its first run. Runs, from the
GitHub API (`results/ci-runs.json`, written by `scripts/ci_runs.py`):

- `25281ea`: run [41109377073](https://github.com/besanson/sarc-p2p-replay/actions/runs/41109377073) success (test (3.11) success, test (3.12) success)
- `d00b776`: run [41110135191](https://github.com/besanson/sarc-p2p-replay/actions/runs/41110135191) success (test (3.11) success, test (3.12) success)

**TeX.** TeX Live 2023 (Debian packages texlive-latex-base, texlive-latex-recommended,
texlive-latex-extra, texlive-fonts-recommended, lmodern) installed in this environment; `make paper`
builds `paper-tex/main.pdf` with pdflatex, twice. The build is deterministic: no dates, no trailer
id, no pdfTeX info entry, `SOURCE_DATE_EPOCH` from the commit date of `paper/paper.md`. Two builds
gave the same bytes, so the PDF is committed; G9 rebuilds it twice and compares both with the
committed file (engine pdflatex, two builds identical: True, committed
equals build: True). The layout has overfull boxes from the widest tables
(no wording changed); the author's read of the PDF is pending.

**Package smoke test.** `make package-smoke-test` (`scripts/package_smoke.py`): sdist and wheel
built, the wheel installed in a fresh venv, the fixture logs (XES with the registered mapping and
patterns beside it; CSV with its own mapping) replayed by the installed package from a directory
outside the checkout, and the evidence compared with the fixture's expected verdicts and byte for
byte with the source-tree replay: passed (10 of
10 checks; `results/package-smoke.json`, Python 3.13.16). G8 runs it
again, locally and in CI.

**README.** The headline block (exposure per defect class, the gate column, the hold rates of the
four arms) is generated by `scripts/fill_paper.py` from `paper/readme-headline.md` and the slots;
the typed-numeral lint checks the block against its recorded SHA-256 and lints the rest of the
README.

**Data.** `make check-data` (`results/data-check.json`): the three registered files at their
SHA-256: True. The fetch URLs are in `prereg/data.lock` and were used at A0 (D-A0-1);
a dry run against them could not be made from this environment (the host resets the connection).

**Gates** (`make gates`, `results/gates-report.json`): {'fail': 0, 'not run in CI': 0, 'pass': 8, 'waiting': 1}.

| gate | status | waiting on |
|---|---|---|
| G1 tests | pass |  |
| G2 lints | pass |  |
| G3 mutation | pass |  |
| G4 regeneration | waiting | external reproduction from a clean clone (FINAL-AUDIT item 11): waiting on Phase F |
| G5 claims | pass |  |
| G6 secrets | pass |  |
| G7 data and pins | pass |  |
| G8 package | pass |  |
| G9 paper | pass |  |

**FINAL-AUDIT.** 10 of 12 items met. Open: 4 (mutation re-run on the release commit) and 11 (external reproduction, Phase F). Closed: items 1, 2, 3, 5, 6, 7, 8, 9, 10, 12. Open: items 4, 11.

**Left for the release session:** the mutation re-run on the release commit (item 4); the CI runs
on the release commit recorded in `results/ci-runs.json`; the Zenodo DOI and the arXiv id (in
`CITATION.cff` and the README); the release tag, which the author sets. External reproduction from
a clean clone (item 11, C13) is Phase F. The package version in `pyproject.toml` is still 0.0.1;
`CITATION.cff` carries 1.0.0-rc1.
