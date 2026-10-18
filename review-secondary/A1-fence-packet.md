Fence review completed 2026-10-16; this version reflects the adjudication D-A1-1. Kept for the record and for any addendum.

# A1 fence packet: paper 7

| field | value |
|---|---|
| paper (working title) | Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process |
| author | Gaston Besanson, Universidad Torcuato Di Tella |
| registration | `p7-v1`, tag `prereg-p7-v1` on commit `e239864` |
| packet date | 2026-10-18 (post-adjudication; versions of 2026-10-13 at `f0e6b90` and 2026-10-14 at `fc6447e`, the one reviewed) |
| repository | https://github.com/besanson/sarc-p2p-replay |

This packet is sent to an external reviewer with no hand in SARC papers 1 to 6. The reply is committed to the repository unedited.

## Instructions to the reviewer

For each item under 'Claimed' in the Novelty section, say one of: (a) already in the listed prior art, with the source; (b) in prior art not listed here, with the source; (c) not found. Then say whether the sentence for the related-work section holds as written. Reply in writing, in any form. Your text will be committed unedited with its SHA-256; tell us whether to name you or to record you as anonymous.

## Part 1. Novelty section (NOVELTY.md)

Source: `NOVELTY.md` as committed together with this packet (the commit after `186cad3`), SHA-256 of the file `94d044037b6a6ed7ba87db763e9beacbb17d3336ff84a1eb8164619b29495cdc` (after D-A1-1; records in `verified-citations.json` in the same commit). Copied verbatim between the rules.

---

# Novelty: prior-art fence

Written before the preregistration (brief section 4). The external fence review
(Eduardo Arana, 2026-10-16) is committed unedited in
`review-secondary/A1-fence-review.md` and adjudicated in `DECISIONS.md`
D-A1-1; two machine sweeps preceded it (D-A1-0b, D-A1-0c). Every source below
was fetched (2026-10-13 and 2026-10-14) and recorded in
`verified-citations.json`, as in paper 5; each citation carries its record id.

## Not claimed as new

**Conformance and compliance checking in process mining.** Checking recorded
behaviour against a normative model or rule set is established: van der Aalst,
*Process Mining: Data Science in Action* (Springer, 2nd ed., 2016,
doi:10.1007/978-3-662-49851-4; verified, `vanderaalst-process-mining-2016`);
Ly, Maggi, Montali, Rinderle-Ma and van der Aalst, "Compliance monitoring in
business processes: Functionalities, application, and tool-support",
*Information Systems* 54, 209-234 (2015, doi:10.1016/j.is.2015.02.007;
verified from the DOI record, `ly-compliance-monitoring-2015`); declarative
constraints in the Declare family (Pesic, Schonenberg and van der Aalst,
"DECLARE: Full Support for Loosely-Structured Processes", EDOC 2007,
doi:10.1109/EDOC.2007.14; verified from the DOI record, `pesic-declare-2007`).
Our predicates D1 to D7 are compliance rules in this sense.

**Conjunction of constraints and sufficient-contract synthesis.** Taking a
decision as the conjunction of its rules is Declare's: "A process model
containing multiple constraints is defined as a conjunction of the constraints,
i.e., actions of users during execution must fulfill all the constraints."
(Pesic, Schonenberg and van der Aalst 2007, section II-B, p. 5;
`pesic-declare-2007`). Synthesising a sufficient contract from declared losses,
with minimum-cardinality and minimum-cost objectives, is paper 5 of this
programme: "The implementation selects minimum-cardinality or minimum-cost
sufficient contracts using distinct objectives." (Besanson 2026,
arXiv:2609.26016, section 8, claim C3, p. 7; `besanson-paper5-2026`). The
compiler E5 runs is paper 5's and is not claimed here.

**Four-eyes and segregation-of-duties detection in event logs.** Detecting
that the same resource performed two activities that must be separated is a
standard conformance check. D5 is that check. Ly et al. (2015, above) list it
among compliance monitoring functionalities: CMF 3, "Every closed project must
be validated by a person who did not participate in the project. (4-eyes
principle, also called Separation of Duties (SoD).)" (section 4.1, p. 15 of the
author-hosted PDF; quote verified 2026-10-14, `ly-compliance-monitoring-2015`).

**The BPI Challenge 2019 reports.** The challenge posed the process owner's
compliance questions, including clearing before goods receipt and the
three-way match per item category, and the submitted reports measured basic
violation rates on this very log. They are prior art for every basic rate this
paper reports. Reports listed on the challenge page
(https://icpmconference.org/2019/bpi-challenge/; verified,
`icpm-bpi-challenge-2019-page`), among them (titles and author lists as the
page states them, each PDF link reached; report contents read only where a
passage is cited below):

- Diba, Remy and Pufahl, "BPI Challenge 2019: Performance and Compliance
  Analysis of Procurement Processes Using Process Mining" (overall winner).
- Meyer zu Wickern, Juluru, Roy, Vu and Nguyen, "Analysis and prediction of
  purchasing compliance using process mining" (best student submission).
- Gutermuth, Lahann, Rehse, Scheid, Schuhmann, Stephan and Fettke, "Efficient
  and Compliant Purchase Order Handling: A Contribution to BPI Challenge 2019".
- Porter, Masse, Visatemongkolchai, Seneviratne, Deokule and Hartman,
  "Balancing Efficiency and Risk in Procure to Pay: Safely Realizing Cost
  Savings Using Process Mining Techniques".
- Augusto, Leno and Reissner, "BPI Challenge 2019 Report: a Purchase-to-Pay
  Process Analysis".
- The remaining student and non-student submissions on the same page, fifteen
  in all (six student, nine non-student), each recorded in
  `verified-citations.json` under `bpi2019-student-*` and
  `bpi2019-nonstudent-*`.

Diba et al. quantify receipt-before-clearing violations with their value
(Table 2, p. 15: rule "Record Goods Receipt -> Clear Invoice", 31 violations,
5.80% of traces; section 4.1: average amount 130,322.85 EUR;
`bpi2019-nonstudent-6-diba`; verified 2026-10-14).

**Compliance measured by count and by value.** Measuring compliance both by the
number of cases and by their value is established on this very log: Porter et
al. report compliance per item category "by number" and "by EUR value" (Table 3,
p. 8; for 3-way after receipt, 80.5% by number and 80.2% by EUR value;
`bpi2019-nonstudent-8-porter`; verified 2026-10-14). The count-and-value
measure is not claimed; Claimed item 2 is the per-clearing, per-defect-class
tabulation.

**The BPI Challenge 2020 reports.** The 2020 challenge posed questions on the
travel-declaration approval chain, including approvals by role and rejection
and resubmission. The reports are prior art for the basic rates in E7.
Challenge page (https://icpmconference.org/2020/bpi-challenge/; verified,
`icpm-bpi-challenge-2020-page`); it lists no reports, winners or proceedings.
The ICPM 2020 awards page (https://icpmconference.org/2020/awards/; verified,
`icpm-2020-awards-page`) names two BPI Challenge reports given awards at
ICPM 2020:

- Pufahl, Hobeck, Binetruy, Chada, Digtiar, Gülle, Slarzynska, Stiehle and
  Weber, "Performance, Variant, and Conformance Analysis of an Academic Travel
  Reimbursement Process" (BPI Challenge Award; author order as the report's
  title page states it, the awards page lists Hobeck first; text:
  https://icpmconference.org/2020/wp-content/uploads/sites/4/2020/10/ICPM_2020_paper_148.pdf;
  `bpi2020-award-hobeck`).
- Kas, Post and Wiewel, "Automated Machine Learning in a Process Mining
  Context" (BPI Student Challenge Award; text:
  https://icpmconference.org/2020/wp-content/uploads/sites/4/2020/10/ICPM_2020_paper_44.pdf;
  `bpi2020-student-award-kas`).

Both texts reached 2026-10-14. No list of the other submitted reports was found
(`bpi2020-report-list`, status "not found").

**Three-way match as an audit control.** Matching purchase order, goods receipt
and invoice before payment is a textbook internal control. The paper does not
propose it; E5 asks whether paper 5's compiler re-derives it from declared
losses. PCAOB Release No. 2004-001 (March 9, 2004), Appendix B, Example B-4,
gives it as an example application control: "An invoice will not be paid
unless the system can match the receipt and vendor invoice to an approved
purchase order." (printed page A-131; quote verified 2026-10-14,
`pcaob-release-2004-001`).

**Deviation-to-outcome studies in process mining.** Relating a deviation to a
later outcome in the same case is established. Peleg, Soffer and Ghattas
(2008), LNCS 4928, pp. 395-400, doi:10.1007/978-3-540-78238-4_40: "This
position paper motivates the extension of process mining in order to capture
not only deviations from the process model, but also the outcomes associated
with them (e.g., patient improving or deteriorating)." (abstract;
`peleg-mining-outcomes-2008`). Framing precedents: outcome-oriented predictive
process monitoring, "classifying each ongoing case of a process according to a
given set of possible categorical outcomes" (Teinemaa, Dumas, La Rosa and
Maggi 2019, ACM TKDD 13(2), doi:10.1145/3301300; `teinemaa-outcome-ppm-2019`),
and deviance mining, where "a subset of the executions of a business process
deviate, in a negative or positive way, with respect to its expected or
desirable outcomes" (Nguyen, Dumas, La Rosa, Maggi and Suriadi 2016,
arXiv:1608.08252; `nguyen-deviance-mining-2016`). On this log, Porter et al.
observe cases "where a 'Cancel Invoice Receipt' event occurs over 120 days
after the initial 'Clear Invoice' event" (section 3.3, p. 10;
`bpi2019-nonstudent-8-porter`), a case-study observation, not a registered
conditional-consequence study. H1 to H3 are studies of this shape.

**Revert and rework analysis.** Corrective events (cancellations, changes,
deletions, debit memos, subsequent invoices) as rework signals are
established. The outcome proxy O is a rework signal. On this log, Meyer zu
Wickern et al. count rework activities as those that "generally include
'change,' 'cancel,' or 'delete' keywords in their activity names" (section 5.1,
p. 17; `bpi2019-student-4-meyerzuwickern`), and Badakhshan et al. list "Vendor
Creates Debit Memo" among rework activities (Table 5, p. 22: 4,680 cases, 4,801
occurrences; `bpi2019-nonstudent-4-badakhshan`). Both quotes verified
2026-10-14; neither covers every activity in the registered outcome list.

**Detectability limits of event logs.** That some deviations leave no trace in
an event log is established: of the workaround types Outmazgin and Soffer
examine, "The remaining two types are not reflected in events logs and cannot
be detected by process mining." (2013, LNBIP 147, pp. 48-62,
doi:10.1007/978-3-642-38484-4_5, abstract; `outmazgin-workarounds-2013`). The
principle is not claimed; Claimed item 6 is the registered per-class matrix.

**Comparing deciders on the same cases.** Putting different deciders on the
same cases is established. Palma et al. (2026, arXiv:2609.32643) compare, on
the same 397 accounts, a human reviewer (MCC 0.422), an LLM agent (0.295), tree
ensembles (0.338, 0.386) and learned symbolic rules (FOIL-IE 0.425; the full
neuro-symbolic stage 0.435) (Table 1; `palma-business-compromise-2026`). Kadir
et al. (2025, arXiv:2512.02726): "Benchmarking SoTA LLMs such as LLaMA and
Gemma on both synthetic and real-world anonymized ledgers, we compare them
against JETs and machine learning baselines." (abstract;
`kadir-auditcopilot-2025`). Harding and Vasconcelos (2022, arXiv:2202.04218):
"We show that it is possible to find machine learning algorithms that can
replicate the behavior of the bank managers." (abstract;
`harding-managers-machines-2022`). None of the three uses a deterministic
contract declared before the data are read, or a human arm read from a process
event log.

## Claimed

The unit and the comparison:

1. Per action, a min() contract over sufficiency-checked, metadata-borne
   predicates (paper 5), evaluated on the evidence reconstructed at clearing
   time.
2. Exposure per Silent Evidence Defect class at the level of the individual
   clearing: the share of clearings and of cleared value failing each
   predicate, per class and stratum, with purchase-order-clustered intervals.
   The count-and-value measure itself is not claimed (Porter et al. 2019).
3. Consequence conditional on the defect, with the registered window W and lag
   bands.
4. The same evidence decided by humans (read from the log), by two model
   families (replayed on the registered ERP view) and by a deterministic gate
   declared before the data were read, side by side on the same lines.
   Comparing deciders on the same cases is not claimed (Palma et al. 2026;
   Kadir et al. 2025; Harding and Vasconcelos 2022).
5. The control derived from declared losses with paper 5's compiler, not
   assumed, with the fewest fields per category a gate must read.
6. A registered per-defect-class coverage matrix (`COVERAGE.md`) stating, for
   each class the paper speaks about, whether this log can expose it and why.
   The principle that some deviations leave no trace in an event log is not
   claimed (Outmazgin and Soffer 2013).

Sentence for the related-work section:

> This paper does not introduce conformance checking, the three-way match or
> rework analysis. It replays each clearing as a gate decision over the
> evidence reconstructed from the event log at clearing time, measures how
> often that evidence was defective and what followed, and puts people, models
> and the gate on the same lines.

## Fence status

| item | status |
|---|---|
| external fence review (A1) | done: `review-secondary/A1-fence-review.md`, adjudicated in `DECISIONS.md` D-A1-1 |
| citations fetch-verified | done: `verified-citations.json` |
| BPI 2020 reports located and cited | done |

---

## Part 2. Claims (CLAIMS.md)

Source: `CLAIMS.md` as committed together with this packet, SHA-256 `c26dab0aaeedd87a2843dccf79a152f2883394f2e824543dadb0a24f0d217048`. The claim text is that of the tagged registration (`e239864`); only the status column changed, from `unregistered` to `registered` (D-A1-1). Copied verbatim between the rules.

---

# Claims

Status vocabulary: `unregistered` (before the tag `prereg-p7-v1`), `registered`
(after the tag, before a result), then `supported`, `not supported`,
`inconclusive` or `withdrawn`, each with the evidence path. A status changes
only with a slot in `results/` behind it.

| id | claim | type | status |
|---|---|---|---|
| C1 | An invoice clearing can be replayed as a sufficiency-checked contract (paper 5) over evidence reconstructed from the event log at clearing time, every predicate deterministic and metadata-borne. | architecture | registered |
| C2 | Exposure: the share of clearings, and the share of cleared value, that relied on evidence failing at least one predicate, per defect class, item category, spend area and month, with intervals clustered by purchase order. | empirical, registered, descriptive | registered |
| C3 | Consequence H1: clearings in a category requiring goods receipt, where the receipt was absent or recorded after clearing, are followed by a corrective event within the registered window at a higher rate than clearings with every predicate passing. | empirical, registered, tested | registered |
| C4 | Consequence H2: clearings where price or quantity changed between approval and clearing are followed by a corrective event at a higher rate than unchanged clearings. | empirical, registered, tested | registered |
| C5 | Authority H3: clearings where the same actor created the line and cleared the invoice are followed by a corrective event at a higher rate than clearings with distinct actors. | empirical, registered, tested | registered |
| C6 | Agent replay H4: on a registered stratified sample, each model family's hold rate on defective lines is within a registered margin of its hold rate on clean lines (Flat Ladder on live data). Reported beside the human hold rate from the log and the gate's. | empirical, registered, tested | registered |
| C7 | Gate effect: share of clearings the gate would have held; share of correctives behind a hold; share of holds with no corrective after; euros in each cell. | empirical, registered, descriptive | registered |
| C8 | Exposure of an ungated agent: euros the sample agent would have released on defective evidence and the expected correctives, beside the human and gate columns. | empirical, registered, descriptive | registered |
| C9 | Derivation: paper 5's compiler, given three declared losses (pay for goods not received, pay twice, pay a changed amount), reproduces or does not reproduce the per-category matching rule; and the fewest fields per category a gate must read. | descriptive | registered |
| C10 | Governance cost: wall time and cost per decision of the deterministic gate over the full log, beside cost per decision of each model family in the sample. | descriptive | registered |
| C11 | Replication: H1's shape on BPI 2020 (paid with a missing or wrong-role approval, followed by rejection or resubmission). | empirical, registered, secondary | registered |
| C12 | Coverage honesty: defect classes the log cannot expose are declared undetected. | coverage | registered |
| C13 | Everything reproduces from the committed dataset hash and caches; no number is hand-entered; the replay runs on any XES or CSV event log with the registered column mapping. | reproducibility, deliverable | registered |

## Non-claims (stated in the paper)

- No causal claim. Correctives are a proxy, observational, confounded by
  vendor, category and practice.
- No loss figure. A corrected payment is not money gone; recovery is not in
  the log.
- No claim that the gate stops anything. Held lines go somewhere the log does
  not show.
- No claim about the company or any vendor. No company, subsidiary or vendor is
  named in any finding.
- No agent acting on the live system and no agent with tools.
- No readiness threshold.

---

## Part 3. Registration section 3: Evidence, predicates and contract

Source: `prereg/p7-v1.md` section 3 at commit `e239864` (the tagged registration; unchanged since). Copied verbatim between the rules.

---

## 3. Evidence, predicates and contract (brief section 3)

### 3.1 Category

The contract is selected by the case flags, as the record states the rules:

| category | `GR-Based Inv. Verif.` | `Goods Receipt` | `Item Type` | contract |
|---|---|---|---|---|
| 3-way, invoice after receipt | true | true | any but consignment | D1 to D7 |
| 3-way, invoice before receipt | false | true | any but consignment | D1 to D7 (invoice may precede receipt; clearing must follow it) |
| 2-way | false | false | any but consignment | D3 to D7 (D1, D2 dropped) |
| consignment | (any) | (any) | consignment | excluded |

"Consignment" is matched case-insensitively in `Item Type` or `Item Category`.
The `Item Category` string is read as a cross-check; the count of lines where it
disagrees with the flag-derived category is a slot. A line with
`GR-Based Inv. Verif.` true and `Goods Receipt` false has no category in the
record's rules; it is reported and excluded under the stop condition in 2.2.

### 3.2 Predicates

Each predicate takes the value pass, fail or unknown. Unknown means a required
input is missing (for example an empty or `NONE` user). Activity lists are in
`prereg/outcome-patterns.yaml`; counts are over events on L before t_c.

| id | name | dimension | fails when (on L, before t_c) | applies to |
|---|---|---|---|---|
| D1 | receipt_present | presence | #`Record Goods Receipt` - #`Cancel Goods Receipt` <= 0 | 3-way categories |
| D2 | receipt_before_clearing | freshness, order | no uncancelled receipt precedes t_c (same count as D1; see 3.3) | 3-way categories |
| D3 | invoice_present | presence | no `Record Invoice Receipt` | all |
| D4 | unchanged_since_approval | validity | a `Change Price` or `Change Quantity` with timestamp after the last approval-bearing event and at most t_c | all |
| D5 | distinct_actors | authority | the actor of `Clear Invoice` equals an actor of the earliest `Create Purchase Order Item`; unknown if either actor is empty or `NONE` | all |
| D6 | block_respected | scope | #`Set Payment Block` - #`Remove Payment Block` > 0 | all |
| D7 | not_deleted | validity | #`Delete Purchase Order Item` + #`Block Purchase Order Item` - #`Reactivate Purchase Order Item` > 0 | all |

Approval-bearing events (D4) are listed in `prereg/outcome-patterns.yaml`; the
earliest `Create Purchase Order Item` is always one, so D4 is defined on every
framed line.

### 3.3 D1 and D2, and the receipt defect class

At t_c, D1 and D2 have the same truth value on every clearing: both fail iff no
uncancelled receipt is recorded before t_c. They are kept as two predicates
because they carry two SARC-DQ dimensions; the gate verdict is the same either
way. For reporting only, a clearing failing D1/D2 is assigned to one defect
class by what the log records after t_c: **stale receipt** (D2 class) if an
uncancelled receipt is recorded on L after t_c and at most T_end; **absent
receipt** (D1 class) otherwise. The class never enters the gate.

Counts and "after the last approval-bearing event" are evaluated on timestamps,
so the verdict is invariant under reordering of events with equal timestamps
(property test, Phase B).

### 3.4 Values

- Line value: the `Cumulative net worth (EUR)` value on the earliest
  `Create Purchase Order Item` event.
- Cleared value of a clearing: the value on the `Clear Invoice` event; if missing
  or not positive, the value on the latest `Record Invoice Receipt` on L before
  t_c; if that is missing too, the line value. Each fallback count is a slot.
- Values are in the record's anonymised euros (linear translation respecting
  0). The paper reports them as "anonymised EUR".

### 3.5 Contract and verdict

The contract of a clearing is the predicate set of its category (3.1). Verdict
**allow** iff every applicable predicate passes; otherwise the gate **would have
held** it. This is min() over the set with pass = 1 and fail = unknown = 0. A
clearing is **defective** if at least one applicable predicate fails; a clearing
whose only non-pass value is unknown is held but not defective, and is counted
separately. "Defect" is used only for a failed predicate.

### 3.6 Human hold

A line is **held by people** if a `Set Payment Block` is recorded on L before its
first clearing, or if no clearing is recorded within W days after its first
`Record Invoice Receipt`. Lines with no invoice receipt by T_end - W are not
classified (count is a slot).

### 3.7 Outcome proxy O

O = 1 for a clearing if any activity in the `outcome` list of
`prereg/outcome-patterns.yaml` is recorded on L with timestamp in
(t_c, t_c + W]. **W = 60 days**, primary. Sensitivity at **W = 30 days**,
descriptive only (the frame stays the W = 60 frame). Outcome activities:
`Cancel Invoice Receipt`, `Cancel Goods Receipt`, `Change Price`,
`Change Quantity`, `Delete Purchase Order Item`, `Vendor creates debit memo`,
`Record Subsequent Invoice`.

### 3.8 Lag bands (D1/D2 failures)

Time from t_c to the first uncancelled `Record Goods Receipt` on L after t_c,
in days: **[0, 1]**, **(1, 7]**, **(7, 30]**, **over 30**, and **never** (no
receipt by T_end). Reported per band in count and cleared value.

### 3.9 Evidence set

One record per analysed clearing: line id (hashed in any export), category,
t_c, predicate inputs, each predicate's value, verdict, defect classes, O at
W = 60 and W = 30, cleared value, line value, and the SHA-256 of the canonical
serialisation of the source events on L up to t_c. A 1,000-record sample
(seeded) is exported to `results/`.

---

## Candidate prior art from a machine sweep

The candidates from the two machine sweeps (`DECISIONS.md` D-A1-0b, D-A1-0c) were adjudicated with the external review in D-A1-1. Those accepted are now cited in Part 1 ("Not claimed as new"); the Gutermuth et al. row for item 4 was withdrawn. The sweep texts stay unedited in `review-secondary/A1-fence-sweep-gpt.md` and `review-secondary/A1-fence-sweep-deepseek.md`.

## What the reviewer is not asked

No comment on the data, the statistics, the code or the writing; only the fence.
