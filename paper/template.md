---
title: "Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process"
author: "Gaston Besanson, Universidad Torcuato Di Tella"
---

<!-- paper/template.md: the source of paper/paper.md. Every number reaches the paper through a
placeholder filled by scripts/fill_paper.py from a slot file under results/. Draft v0.3. -->

## Abstract

Of the {{e1/exposure.json>analysed_clearings|int}} analysed invoice clearings of a real purchase-to-pay event log (Section 4 gives the
registered exclusions),
{{e1/exposure.json>classes>at least one defect>clearings|int}} ({{e1/exposure.json>classes>at least one defect>share_of_clearings|pct}},
clustered bootstrap 95% interval {{e1/exposure.json>classes>at least one defect>bootstrap95|ivpct}}) were made on evidence that
failed at least one of seven registered predicates, carrying {{e1/exposure.json>classes>at least one defect>share_of_value|pct}}
of the cleared value ({{e1/exposure.json>classes>at least one defect>value_bootstrap95|ivpct}}). We replay every analysed clearing
of the BPI Challenge 2019 log through a deterministic min() gate declared before the data were read, over the evidence
reconstructed from the log at clearing time. Clearings made on evidence that failed on the goods receipt (absent or late, D1/D2)
were followed by a corrective event within
60 days at a rate of {{e2/hypotheses.json>estimates>H1>W60>defect_group>O_rate|pct}}, against {{e2/hypotheses.json>estimates>H1>W60>comparison_group>O_rate|pct}}
for three-way clearings with every applicable predicate passing (difference {{e2/hypotheses.json>estimates>H1>W60>difference|prop}}, Holm-adjusted
p = {{e2/hypotheses.json>holm>table>1>p_holm|p}}); clearings made after a change of price or quantity since approval (D4 fail), at
{{e2/hypotheses.json>estimates>H2>W60>defect_group>O_rate|pct}} against {{e2/hypotheses.json>estimates>H2>W60>comparison_group>O_rate|pct}}
for D4-pass clearings (difference {{e2/hypotheses.json>estimates>H2>W60>difference|prop}}, Holm-adjusted p = {{e2/hypotheses.json>holm>table>0>p_holm|p}}).
On a registered sample of lines with a failed predicate and of clean lines, two model families shown the ERP view held
{{e4/arms.json>arms>jev>hold_rate_defective|pct1}} and {{e4/arms.json>arms>haiku>hold_rate_defective|pct1}} of the first and
{{e4/arms.json>arms>jev>hold_rate_clean|pct1}} and {{e4/arms.json>arms>haiku>hold_rate_clean|pct1}} of the second; on the sample lines the
log lets us classify, people held {{e4/arms.json>arms>people>hold_rate_defective|pct1}} and {{e4/arms.json>arms>people>hold_rate_clean|pct1}},
where a hold is an inferred non-release within 60 days, not a recorded decision;
the gate's verdict holds the first and allows the second by construction. A line's status at the decision point follows a
reading of D5 (decision D-C-2 B) that the author fixed after E3 and before any model call (Section 4). Paper 5's compiler, given the three declared losses of the registration, does not
reproduce the registered contract in any item category. The coverage matrix states which defect classes this log cannot
expose; the authority defect class (D5) has zero incidence here. No causal claim is made.

## 1 Introduction

Earlier papers of this programme showed the mechanism of a silent evidence defect, a decision taken on evidence that fails a
metadata-borne predicate, on constructed domains, and made no prevalence claim: paper 4 ({{@cite>besanson-paper4-2026}}) and
paper 5 ({{@cite>besanson-paper5-2026}}) are on arXiv, and paper 6 is a public repository ({{@cite>besanson-paper6-repo-2026}}). We
found no record that identifies papers 1 to 3, and do not cite them. This paper is the number, on one real process.

The unit is an invoice clearing in the BPI Challenge 2019 purchase-to-pay log. For each of the
{{e1/exclusions.json>analysed_clearings|int}} analysed clearings (the exclusion table of Section 4) we reconstruct the evidence
recorded on the purchase-order line at clearing time, evaluate the registered predicates D1 to D7, record what the gate would
have held, and read what followed in the log. We report exposure in count and in anonymised EUR, the corrective events that
follow a failed predicate, the reach of the gate, and, on a registered sample, what two model families decide on the same
ERP view beside the people in the log and the gate. Everything was registered before the log was parsed beyond its published
counts (tag `prereg-p7-v1`) and amended once after the pilot (v1.1, tag `prereg-p7-v1.1`), with five deviations under v1.1:
two decided after E2 and E3 and before E4, and three found in review (corrected descriptions in the coverage matrix, the E7
bootstrap replicates with an empty group discarded, and the request format of the Jev family in E4); all are listed in
Section 4.

What this paper claims is in the claim table of Appendix B. What it does not claim is stated in the repository's claims file
and repeated here verbatim:

- No causal claim. Correctives are a proxy, observational, confounded by vendor, category and practice.
- No loss figure. A corrected payment is not money gone; recovery is not in the log.
- No claim that the gate stops anything. Held lines go somewhere the log does not show.
- No claim about the company or any vendor. No company, subsidiary or vendor is named in any finding.
- No agent acting on the live system and no agent with tools.
- No readiness threshold.

"No claim about the company" means that no company, subsidiary or vendor is named or characterised; the measured process is
the subject of every finding.

## 2 Related work

This paper does not introduce conformance checking, the three-way match or rework analysis. It replays each clearing as a
gate decision over the evidence reconstructed from the event log at clearing time, measures how often that evidence was
defective and what followed, and puts people, models and the gate on the same lines. The defect classes are the predicates
of Section 3.

**Conformance and compliance checking.** Checking recorded behaviour against a normative model or rule set is established
({{@cite>vanderaalst-process-mining-2016}}; {{@cite>ly-compliance-monitoring-2015}}), and declarative constraints in the Declare
family take a process model as the conjunction of its constraints ({{@cite>pesic-declare-2007}}). The predicates D1 to D7 are
compliance rules in this sense, and taking the decision as their conjunction is Declare's. Synthesising a sufficient contract
from declared losses is paper 5 of this programme ({{@cite>besanson-paper5-2026}}); the compiler used in Section 5.5 is
paper 5's. Detecting that one resource performed two activities that must be separated is a standard compliance monitoring
functionality ({{@cite>ly-compliance-monitoring-2015}}); predicate D5 is that check.

**The BPI Challenge 2019 reports.** The challenge posed the process owner's compliance questions on this very log, including
clearing before goods receipt and the three-way match per item category ({{@cite>icpm-bpi-challenge-2019-page}}). The submitted
reports measured basic violation rates and are prior art for every basic rate reported here; among them
{{@cite>bpi2019-nonstudent-6-diba}} quantify receipt-before-clearing violations with their value, and
{{@cite>bpi2019-nonstudent-8-porter}} report compliance per item category both by number and by value. Measuring compliance by
count and by value is therefore not claimed; what is claimed is the tabulation per clearing and per defect class, with
clustered intervals. The three-way match itself is a textbook application control ({{@cite>pcaob-release-2004-001}}); Section 5.5 asks
whether paper 5's compiler re-derives it from declared losses.

**Deviation and outcome.** Relating a deviation to a later outcome in the same case is established: the extension of process
mining to outcomes associated with deviations ({{@cite>peleg-mining-outcomes-2008}}), outcome-oriented predictive process
monitoring ({{@cite>teinemaa-outcome-ppm-2019}}) and deviance mining ({{@cite>nguyen-deviance-mining-2016}}). On this log,
{{@cite>bpi2019-nonstudent-8-porter}} observe cancellations of invoice receipts long after clearing as a case-study observation.
Corrective events as rework signals are established on this log too: {{@cite>bpi2019-student-4-meyerzuwickern}} count change,
cancel and delete activities as rework, and {{@cite>bpi2019-nonstudent-4-badakhshan}} list vendor debit memos among rework
activities. The outcome proxy of Section 3 is a rework signal of this kind; H1 to H3 are registered conditional-consequence
studies of the deviation-to-outcome shape.

**Detectability.** That some deviations leave no trace in an event log is established ({{@cite>outmazgin-workarounds-2013}}).
The registered per-class coverage matrix of Section 6 is claimed; the principle is not.

**Deciders on the same cases.** Putting different deciders on the same cases is established: a human reviewer, a model agent
and learned rules on the same accounts ({{@cite>palma-business-compromise-2026}}), language models against audit baselines on
the same ledgers ({{@cite>kadir-auditcopilot-2025}}), and algorithms against bank managers ({{@cite>harding-managers-machines-2022}}).
None of these uses a deterministic contract declared before the data were read, or a human arm read from a process event log;
Section 5.4 does both, with one qualification: the status of a line at the decision point follows a reading of D5 (decision
D-C-2 B) that the author fixed after E3 and before any model call (Section 4).

**The BPI Challenge 2020 reports.** The 2020 challenge posed questions on the approval chain of travel declarations
({{@cite>icpm-bpi-challenge-2020-page}}); two reports received awards ({{@cite>icpm-2020-awards-page}}; {{@cite>bpi2020-award-hobeck}};
{{@cite>bpi2020-student-award-kas}}). They are prior art for the basic rates of the replication in Section 5.7.

## 3 Formal core

**Lines, clearings and evidence.** A line is one case of the log: one purchase document and item. A clearing is one
`Clear Invoice` event on a line at time t_c. The evidence at t_c is every event on the line with timestamp at most t_c,
excluding the clearing itself, as the registration defines "before t_c" (section 2 of `prereg-p7-v1`, unchanged in v1.1); events sharing a timestamp count as available, and counts rather than event order decide
receipts, blocks and deletions, so the verdict does not depend on the order of events with equal timestamps (a property test
of the replay engine).

**Category and contract.** The case flags select the contract, as the data record states the rules:

| category | GR-based invoice verification | goods receipt | contract |
|---|---|---|---|
| three-way, invoice after receipt (`3-way`) | true | true | D1 to D7 |
| three-way, invoice before receipt (`3-way`) | false | true | D1 to D7 |
| two-way (`2-way`) | false | false | D3 to D7 |
| consignment | any | any | excluded |

**Predicates.** Each predicate takes the value pass, fail or unknown; unknown means a required input is missing.
Each predicate checks one SARC-DQ dimension (the table). The contract as a whole is checked with paper 5's own sufficiency
function over this log's observed states (E5, `results/e5/sufficiency.json`, Section 5.5): it is sufficient for the three
declared losses in the two-way category, and in the two three-way categories for L1 and L3 but not for L2; it is minimal in no
category.

| id | name | dimension | fails when, on the line before t_c |
|---|---|---|---|
| D1 | receipt present | presence | no uncancelled goods receipt (receipts minus receipt cancellations at most zero) |
| D2 | receipt before clearing | freshness, order | no uncancelled receipt precedes t_c |
| D3 | invoice present | presence | no invoice receipt |
| D4 | unchanged since approval | validity | a price or quantity change after the last approval-bearing event |
| D5 | distinct actors | authority | the actor of the clearing equals an actor of the earliest creation (unknown if either is missing) |
| D6 | block respected | scope | payment blocks set minus blocks removed greater than zero |
| D7 | not deleted | validity | deletions plus blocks minus reactivations of the line greater than zero |

At t_c, D1 and D2 have the same truth value; they are kept apart because they carry two dimensions. For reporting only, a
D1/D2 failure is assigned to a defect class by what the log records later: the stale receipt (D2 class) if an uncancelled
receipt is recorded after t_c and by the observation end, the absent receipt (D1 class) otherwise.

**Verdict.** The verdict is min() over the category's contract with pass as one and fail or unknown as zero: the gate allows a
clearing if and only if every applicable predicate passes, and otherwise would have held it. A clearing is defective if at
least one applicable predicate fails; one whose only non-pass value is unknown is held but not defective, and is counted
separately. "Defect" is used only for a failed predicate.

**Human hold.** A line is held by people if a payment block is recorded before its first clearing, or if no clearing is
recorded within W days of its first invoice receipt; a clearing before the first invoice receipt counts as a release.

**Outcome proxy and lag bands.** O = 1 for a clearing if a registered corrective activity (an invoice receipt or goods receipt
cancelled, a price or quantity changed, the line deleted, a vendor debit memo, a subsequent invoice) is recorded on the line
within W after t_c; W = 60 days, with W = 30 days as a descriptive sensitivity. For a D1/D2 failure, the lag from t_c to the
first uncancelled receipt falls in one of the registered bands [0, 1], (1, 7], (7, 30] days, over 30 days, or never.

**Evidence set.** One record per analysed clearing carries the line id (hashed in every export), category, t_c, every
predicate input and value, the verdict, the defect classes, O at both windows, the cleared and line values, and the SHA-256 of
the canonical serialisation of the line's events up to t_c.

## 4 Data and registration

**Data.** The primary log is the BPI Challenge 2019 record; the replication uses the two declaration logs of the BPI Challenge
2020 collection. All three are by Boudewijn van Dongen on 4TU.ResearchData; each file was checked against the hash the
registration records.

{{#datasets}}

Values in the 2019 log are anonymised by a linear translation that respects zero; we report them as anonymised EUR.

**Window, observation end and frame.** A line is in the window if its earliest `Create Purchase Order Item` event lies in
calendar 2018. The observation end T_end is the latest timestamp in the last calendar month that carries at least 1,000
events; here T_end is {{e1/exclusions.json>t_end|date}} and {{e1/exclusions.json>events_after_t_end_excluded|int}} later
events are excluded. A line is framed if it survives the exclusions below and its first clearing, or its creation if it has
none, lies at least W before T_end; the analysed clearings are every clearing on a framed line at least W before T_end, so
every outcome window is complete. The lines drawn for the pilot (E0) are removed before any estimate. As registered, the
`Item Category` string disagrees with the flag-derived category on {{e1/category-crosscheck.json>all_lines_disagreeing|int}} of
{{e1/category-crosscheck.json>all_lines|int}} lines (section 3.1; `results/e1/category-crosscheck.json`); every analysed clearing took its value from the clearing event
itself ({{e1/value-fallback.json>cleared_value_source>clearing|int}} clearings; {{e1/value-fallback.json>cleared_value_source>invoice_receipt|int}}
fell back to the invoice receipt and {{e1/value-fallback.json>cleared_value_source>line_value|int}} to the line value, section 3.4; `results/e1/value-fallback.json`);
and the seeded 1,000-record sample of the evidence set, identifiers hashed, is exported as `results/e1/evidence-sample.jsonl`
(section 3.9).

{{#exclusions}}

**Registration.** The registration was tagged `prereg-p7-v1` before any parse of the log beyond the published counts. The
pilot fired registered stop conditions (the latest timestamp lay outside the registered range, and a mapped attribute is
named differently in the log than on the record page); the registration was amended and tagged `prereg-p7-v1.1`, and the
pilot was drawn again, before any estimate. Every deviation, with the decision that records its reason:

{{#deviations}}

The H3 convention and the D5 reading were the author's decisions after E2 and E3 and before any model call (decision D-C-2 in
the decision log). The response logs date the calls: D-C-2 was committed at {{e4/timeline.json>commits>D-C-2 decision (D5 reading, H3 convention)>committer_utc|utc}} (`7aea13f`) and the E4 sample drawn at
{{e4/timeline.json>commits>E4 sample draw>committer_utc|utc}} (`5ffd887`); the first request was sent at {{e4/timeline.json>calls>e4/jev>earliest_sent_utc|utc}} for Jev and at {{e4/timeline.json>calls>e4/haiku>earliest_sent_utc|utc}} for Haiku
(`results/e4/timeline.json`; request times as the client wrote them before sending, commit times as git records them). The prior-art fence was reviewed externally after the tag `prereg-p7-v1` and before `prereg-p7-v1.1`,
after two machine sweeps whose output is committed unedited.

## 5 Results

### 5.1 Exposure (E1)

{{#exposure}}

Figure 1 shows the shares with their intervals. Shares of clearings carry a Wilson and a purchase-document-clustered
bootstrap 95% interval (B = 10,000, seed 20261201); shares of value carry the clustered interval. The denominator is every
analysed clearing, and a share counts the clearings made on evidence that failed the predicate; D1 and D2 classes apply to {{e1/exposure.json>applicable_clearings>D1 class (absent receipt)|int}} clearings
in the three-way categories. A change after approval (D4) is the largest defect class, {{e1/exposure.json>classes>D4>clearings|int}}
clearings and {{e1/exposure.json>classes>D4>share_of_value|pct}} of cleared value; no clearing fails D5. Appendix D gives the same
shares per defect class, with the clustered intervals, per item category, spend area, month, line value quartile and vendor
activity quartile, reported beside the estimates and never modelled in. Section 4 reports the registered category cross-check,
the cleared-value sources and the exported sample.

![Figure 1: share of analysed clearings and of cleared value per defect class, with clustered bootstrap 95% intervals.](figures/fig1-exposure.svg)

### 5.2 Consequence (E2)

{{#hypotheses}}

O is the registered corrective within W = 60 days. The H1 comparison group is three-way clearings with every applicable
predicate passing; against clearings of every category with every applicable predicate passing the difference is {{e2/hypotheses.json>estimates>H1 all-category comparison>W60>difference|prop}},
descriptively. H2 compares D4 fail with D4 pass in every category. Standard errors come from the purchase-document-clustered
bootstrap. Holm's adjustment runs over the registered family of five tests, H1, H2, H3 and H4 for each model family, at
alpha = 0.05:

{{#holm}}

H3, distinct actors, is not computable: {{e2/hypotheses.json>estimates>H3>W60>not_computable}}. No analysed clearing was made by
an actor of its line's earliest creation event, so the defect class has zero incidence; across the log the actors who record a
`Clear Invoice` and those who record the earliest creation of a line are separate populations
({{e1/actors.json>scopes>all>distinct_clear_invoice_actors|int}} and {{e1/actors.json>scopes>all>distinct_earliest_creation_actors|int}}
actors, {{e1/actors.json>scopes>all>intersection|int}} in common; Section 6). No analysed clearing has D5 unknown
({{e1/analysed-clearing-actors.json>analysed_clearings_D5_unknown|int}}): the {{e1/actors.json>scopes>all>clear_invoice_events>missing|int}}
`Clear Invoice` events with no actor all lie outside the analysed set: of the
{{e1/analysed-clearing-actors.json>framed_lines_clear_invoice_missing_actor>total|int}} on framed lines,
{{e1/analysed-clearing-actors.json>framed_lines_clear_invoice_missing_actor>after_horizon|int}} fall after the horizon T_end − W
(`results/e1/analysed-clearing-actors.json`). H3 enters the family with p = 1, the convention the author fixed in decision D-C-2,
committed at {{e4/timeline.json>commits>D-C-2 decision (D5 reading, H3 convention)>committer_utc|utc}}, before the first model request at {{e4/timeline.json>calls>e4/jev>earliest_sent_utc|utc}} (`results/e4/timeline.json`). At W = 30 days the differences are {{e2/hypotheses.json>estimates>H1>W30>difference|prop}}
for H1 and {{e2/hypotheses.json>estimates>H2>W30>difference|prop}} for H2, descriptively. Appendix E gives H1 and H2 per item
category, spend area, value quartile, vendor activity quartile and month, descriptively and never modelled in.

### 5.3 Gate effect and hold cost (E3)

The gate would have held {{e3/gate-held.json>held>clearings|int}} of {{e3/gate-held.json>analysed_clearings|int}} analysed clearings
({{e3/gate-held.json>held>share_of_clearings|pct}}, {{e3/gate-held.json>held>share_of_value|pct}} of cleared value); {{e3/gate-held.json>held_unknown_only|int}}
of them were held on an unknown predicate value alone. Against the corrective at W = 60 days, in clearings and anonymised EUR (Figure 4):

{{#two_by_two}}

Appendix E gives the same table per stratum.

![Figure 4: gate verdict against the corrective within W = 60 days, in clearings and in cleared value.](figures/fig4-verdict-outcome.svg)

For D1/D2 failures, the time from clearing to the first uncancelled receipt (Figure 3):

{{#lag_bands}}

![Figure 3: D1/D2 failures by lag band, in clearings and cleared value.](figures/fig3-lag-bands.svg)

**Human hold.** Of {{e3/human-hold.json>framed_lines|int}} framed lines, people held {{e3/human-hold.json>held_by_people|int}} and
released {{e3/human-hold.json>released_by_people|int}}; {{e3/human-hold.json>unclassified_no_invoice_receipt_by_t_end_minus_w|int}} had no invoice
receipt by T_end − W and are not classified. The status of a line is the gate verdict at the decision point t* of the agent
replay: the first clearing if it came within W of the first invoice receipt, otherwise that receipt plus W. The registered
text left D5 at a t* that is not a clearing undefined; read literally it is unknown, and then a line with no clearing within W
can never be clean under the literal reading. The author amended the reading before any model call (at a t* that is not a
clearing, D5 is not applicable: the decider there is the gate or a model; decision D-C-2 B); both readings are reported:

{{#human_hold}}

Under the amended reading, people held {{e3/human-hold.json>amended_reading_D-C-2>by_gate_status_at_t_star>defective>human_hold_rate|pct}} of
lines with a failed predicate at t* and {{e3/human-hold.json>amended_reading_D-C-2>by_gate_status_at_t_star>clean>human_hold_rate|pct}} of clean
lines.

### 5.4 People, models and the gate on the same lines (E4)

**Sample and arms.** From the framed lines with an invoice receipt, {{e4/sample-frame.json>groups>defective>eligible_lines|int}} had at least
one failed predicate at t* and {{e4/sample-frame.json>groups>clean>eligible_lines|int}} were clean, under D-C-2 B (`results/e4/sample-frame.json`).
These differ from the {{e3/human-hold.json>amended_reading_D-C-2>by_gate_status_at_t_star>defective>classified_lines|int}} and
{{e3/human-hold.json>amended_reading_D-C-2>by_gate_status_at_t_star>clean>classified_lines|int}} lines of Section 5.3 (`results/e3/human-hold.json`),
which are the lines the people arm can classify: a line whose first invoice receipt comes later than T_end − W is eligible
for the sample but not classified (section 3.6). The registered sample
drew 1,000 defective and 1,000 clean lines, at most one per purchase document, stratified by category and value quartile, with
seed 20261201; the draw was committed before any call. Each line was shown to two model families as the registered ERP view at
t*, a short record with no event timeline and no company, vendor, actor or line id: TypeSafe System One (Jev, returned model
`jev-1.14.0`) through `typesafe-sdk==0.7.2`, asked one choice question with labels clear and hold, and the Anthropic Messages API
(`claude-haiku-4-5-20251001`, temperature zero, assistant prefill), asked for a JSON decision and hold probability.
For Jev the template's closing reply-format sentence was replaced by that typed choice, a deviation (Section 4); Haiku
received the template as registered.
Invalid replies, after one re-request: {{e4/arms.json>arms>jev>invalid|int}} for Jev and {{e4/arms.json>arms>haiku>invalid|int}} for Haiku. The people arm is read from the log (Section 3);
{{e4/arms.json>arms>people>unclassified|int}} sample lines have no invoice receipt by T_end − W and are not classified (section 3.6), so
its denominators are smaller. The gate's verdict holds every line with a failed predicate and allows every clean line by
construction.

{{#arms}}

![Figure 2: hold rate on lines with a failed predicate and on clean lines, per arm; the exploratory timeline arm in its own panel.](figures/fig2-hold-rates.svg)

H4 asks whether each family's hold rate on defective lines (a failed predicate) is within m = 0.05 of its rate on clean lines.
Neither is: Jev held {{e4/arms.json>arms>jev>hold_rate_defective|pct1}} and {{e4/arms.json>arms>jev>hold_rate_clean|pct1}}, Haiku held
{{e4/arms.json>arms>haiku>hold_rate_defective|pct1}} and {{e4/arms.json>arms>haiku>hold_rate_clean|pct1}}; p_TOST is
{{e4/h4.json>families>H4-Jev>p_tost|p}} for Jev and {{e4/h4.json>families>H4-Haiku>p_tost|p}} for Haiku, and H4 is below alpha after Holm for
neither. Both families track the gate's verdict on the lines
the gate would have held and hold about half of the lines it allows (Cohen's kappa with the gate
{{e4/arms.json>arms>jev>kappa_with_gate|prop3}} and {{e4/arms.json>arms>haiku>kappa_with_gate|prop3}}). Released on lines with a failed
predicate, in anonymised EUR: people {{e4/arms.json>arms>people>value_released_on_defective_lines_eur|eur}}, Jev
{{e4/arms.json>arms>jev>value_released_on_defective_lines_eur|eur}}, Haiku {{e4/arms.json>arms>haiku>value_released_on_defective_lines_eur|eur}},
gate {{e4/arms.json>arms>gate>value_released_on_defective_lines_eur|eur}}; for the gate, held lines go somewhere the log does not show.
The expected correctives are the metric of registration section 6 (E4 row): each released line with a failed predicate
carries the E2 O rate at W = 60 days of its defect group. The precedence and the unmatched-group rule are decision D-C-3:
the H1 group if D1/D2 fails and otherwise the H2 group if D4 fails; a line failing neither (only D3, D6 or D7) has no E2 group
and is counted, not imputed ({{e4/arms.json>defective_lines_without_e2_group|int}} sample lines,
{{e4/arms.json>arms>people>released_defective_lines_without_e2_group|int}} of them released by people). The ERP view hands each model the
inputs of the predicates; this result is about the view as much as about the models.

**On the lines the people arm classifies.** The same four arms, re-tabulated on the
{{e4/arms-classified-lines.json>classified_lines|int}} sample lines the people arm classifies; the table above, on all sample lines, stays
primary:

{{#arms_classified}}

**What the people arm measures.** The log records no hold decision except a payment block. "Held by people" (section 3.6)
is a payment block before the first clearing, or no clearing within W of the first invoice receipt: an inferred non-release,
not the same act as a model's hold verdict at t*. Of the {{e3/human-hold-composition.json>held_by_people|int}} framed lines held by
people, {{e3/human-hold-composition.json>by_reason>payment_block_before_first_clearing|int}} were held by a payment block alone,
{{e3/human-hold-composition.json>by_reason>no_clearing_within_W_of_first_invoice|int}} by no clearing within W alone, and
{{e3/human-hold-composition.json>by_reason>both|int}} by both:

{{#hold_composition}}

**Exploratory: the event timeline instead of the ERP view.** Labelled exploratory and outside the Holm family: the same lines,
the same families and rules, with the line's events up to t* (date, activity, value) in place of the ERP view.

{{#exploratory}}

Under the timeline view the same models held far fewer lines with a failed predicate (exploratory, no interval). Spend for
both families and both views together was USD {{e6/cost.json>spend_usd_total|usd}} against the registered cap of USD 60
(`results/e6/cost.json`).

### 5.5 Derivation (E5)

Paper 5's compiler, at the pinned commit and unmodified, was given per category the observed states of the evidence set and
the three declared losses of the registration: L1, pay for goods not received (the category requires a goods receipt and none
is uncancelled); L2, pay twice (the clearing's position among the line's clearings exceeds the invoices recorded); L3, pay a
changed amount (a change since approval). The derived contract is the set of registered predicates whose observation is in
the compiler's minimum-cardinality sufficient set. The comparison is the registered one (registration section 6, E5):
"whether the derived contract equals the category contract in 3.1".

{{#e5}}

The compiler does not reproduce the registered contract in any category. The three losses derive at most D1 to D4: no
declared loss reads the observations of D5, D6 or D7, so those predicates correspond to no declared loss. In the before-receipt
category the derived D1 to D4 is the three-way match in the narrow sense (receipt, invoice and an unchanged approved amount),
and the registered contract carries three predicates beyond it. In the after-receipt category the compiler derives D3 and D4
only, because L1 occurs on {{e5/derivation.json>categories>3-way, invoice after receipt>clearings_per_loss>L1|int}} analysed
clearings there, and the registered contract carries five predicates beyond it. This is a limit of deriving from one log: a
loss the log never shows calls for no observation. Pay twice needs the clearing's position on its line, an observation no
registered predicate reads.

Read the other way, paper 5's sufficiency function applied to the registered contract over the same states
(`results/e5/sufficiency.json`):

{{#sufficiency}}

The registered contract is sufficient, not derived: sufficient for the three declared losses in the two-way category, and in
the three-way categories for L1 and L3 but not for L2, for the reason above; minimal in no category (C1). The compiler's
contract is smaller in every category, and so C9, which asks whether it equals the registered one, is not supported.

### 5.6 Governance cost (E6)

The full replay of every line, from reading the log to the written evidence set, took a median of
{{e6/timing-e1.json>median_replay_seconds|sec}} seconds over three runs on a {{e6/timing-e1.json>hardware>cpu_cores|int}}-core machine,
{{e6/timing-e1.json>seconds_per_decision|f6}} seconds per gate decision. A model decision cost USD
{{e6/cost.json>arms>e4>jev>usd_per_decision|usd6}} with Jev and USD {{e6/cost.json>arms>e4>haiku>usd_per_decision|usd6}} with Haiku.

### 5.7 Replication on travel declarations (E7)

The unit is a payment on a declaration case at least W before the latest timestamp of its log; D1' approval present, D2'
approval by the required role and D3' unchanged after approval are evaluated before the payment, and O' is a rejection or
resubmission within W after it. Descriptive and secondary, outside the Holm family.

{{#e7}}

The replication is inconclusive. Only {{e7/exposure.json>scopes>pooled>with_a_failed_predicate|int}} of {{e7/exposure.json>scopes>pooled>units|int}}
payments fail any predicate; the {{e7/unknown-overlap.json>logs>domestic>with_a_predicate_unknown|int}}
domestic payments with D3' unknown are the same {{e7/unknown-overlap.json>logs>domestic>with_a_predicate_unknown_and_another_failing|int}}
that fail D1' and D2' (`results/e7/unknown-overlap.json`). O' follows {{e7/comparisons.json>scopes>pooled>D1'>all_pass_group>with_O_prime|int}} of the
{{e7/comparisons.json>scopes>pooled>D1'>all_pass_group>payments|int}} payments with every predicate passing; no comparison has an interval
excluding zero. A bootstrap replicate in which either group is empty is discarded and the percentiles are taken over the
retained replicates ({{e7/comparisons.json>scopes>domestic>D1'>bootstrap_resamples_used|int}} of {{e7/comparisons.json>bootstrap>B|int}}
for the domestic log and {{e7/comparisons.json>scopes>pooled>D1'>bootstrap_resamples_used|int}} pooled,
`results/e7/comparisons.json`; a deviation, Section 4). The registered names `{{e7/vocabulary.json>registered_names_absent_per_log>domestic>0}}` and
`{{e7/vocabulary.json>registered_names_absent_per_log>domestic>1}}` do not occur in the domestic log; they are reported with zero counts,
not replaced.

## 6 Coverage

What the replay can and cannot see, as registered:

{{#coverage}}

Per class, the failures found (BPI 2019 on analysed clearings, BPI 2020 on payments):

{{#coverage_status}}

On BPI 2019 every detected class fails at least once except the authority class (D5), with
{{e1/coverage-check.json>rows>4>failed_clearings|int}} failed clearings: across the log, the
{{e1/actors.json>scopes>all>distinct_clear_invoice_actors|int}} actors who record a `Clear Invoice` and the
{{e1/actors.json>scopes>all>distinct_earliest_creation_actors|int}} who record a line's earliest creation share
{{e1/actors.json>scopes>all>intersection|int}}, so the two are separate populations; no `Clear Invoice` is recorded by a batch user (an
actor whose name starts with the registered batch prefix), and {{e1/actors.json>scopes>all>clear_invoice_events>missing|int}} carry no
actor (`results/e1/actors.json`), none of them on an analysed clearing
({{e1/analysed-clearing-actors.json>analysed_clearings_clearing_actor_missing|int}}; Section 5.2). D5 fires on synthetic lines in the engine's tests (`test_d5_actors` and
`test_verdict_at_decision_point_d5_off_clearing` in `tests/test_engine_units.py`, and fixture line C in `tests/test_pipeline.py`). On BPI 2020, D3' fails on no payment in
either log, and in the international log no predicate fails at all.

## 7 Limitations and non-claims

The outcome is a proxy: a corrective event after a clearing is not proof that the clearing was wrong, and the study is
observational. Category, spend area, value, vendor activity and month are reported beside every estimate (Appendix D for
exposure, Appendix E for H1, H2 and the gate by outcome) and never modelled in. Values are anonymised. What a line the gate would have held becomes is not in the log. The people column reports what the process did within W; the comparison across the people, the
models and the gate is of outcomes of three deciders, not of three acts. The ERP view hands the model the
inputs of the predicates; under the timeline view the same models held far fewer lines (exploratory, no interval), which is
a statement about views, not about the models alone. The derivation depends on how the three declared losses are expressed over
the evidence set; the expressions are recorded with the result. One company's process, one year.

## 8 Conclusion

{{e1/exposure.json>classes>at least one defect>share_of_clearings|pct}} of the {{e1/exposure.json>analysed_clearings|int}} analysed invoice
clearings in this process were made on evidence that failed at least one registered predicate, carrying
{{e1/exposure.json>classes>at least one defect>share_of_value|pct}} of the cleared value; those made with an absent or late receipt
(D1/D2) were followed by a corrective at a higher rate than three-way clearings with every applicable predicate passing, and
those made after a change since approval (D4 fail) at a higher rate than D4-pass clearings.

## Acknowledgements

The prior-art fence was reviewed externally by Eduardo Arana after the tag `prereg-p7-v1` and before `prereg-p7-v1.1`, and
he reviewed drafts v0.1 and v0.2. AI tools were used as support: builder sessions with Claude for the code, the runs and the
drafting from slots; two machine prior-art sweeps, on ChatGPT and on Perplexity Computer (for the second, the platform made two
statements, in this order: a later session reported its own model as `Claude Opus 5.5` and stated that it produced the sweep,
and the same session then identified the sweep's model as `DeepSeek V4 Pro`); and machine reviews of drafts v0.1 and v0.2, on
ChatGPT and on Perplexity Computer (model as it states it: `Claude Opus 5.5`). All are committed unedited. The author is solely responsible for every claim. We thank the organisers of the BPI
Challenges and 4TU.ResearchData for the logs.

## References

{{#references}}

## Appendix A: Registration summary

The registered numbers, Section 9 of the registration:

{{#registered_numbers}}

## Appendix B: Claims, decisions and deviations

Claim statuses, each set from its slot file:

{{#claims}}

Reading notes, as in the claims file. C1's "(paper 5)" refers to paper 5's contract construct, whose sufficiency for the
declared losses over the observed states E5 checks with paper 5's own function, per category and per loss
(`results/e5/sufficiency.json`): sufficient for every declared loss in the two-way category, and for L1 and L3 but not L2 in the
three-way categories; minimal in none; each predicate checks one SARC-DQ dimension (Section 3). C2's "relied on" is read as
"made on evidence that failed". C9's "per-category matching rule" is the category contract of section 3.1, the comparator the
registration's E5 row fixes; the before-receipt category recovers the narrow three-way match (D1 to D4), and the status "not
supported" refers to the registered comparison (Section 5.5).

Every decision taken while the work ran is in the repository's decision log, from D-A0-1 to D-D-4, and every deviation from
the tagged registration is in its deviations file (Section 4).

## Appendix C: Reproduction

`make bootstrap` clones the sibling repositories at their pins, creates the environment, fetches the logs and checks their
hashes; `make test` and `make lint` run the tests and the lints; `make gates` runs the release gates G1 to G9; the experiment
runners regenerate every slot under `results/`, and `make paper` regenerates this paper and its figures from the slots. The
internal double runs were byte-identical ({{reproducibility.json>files_compared|int}} files for E1 to E3); external
reproduction from a clean clone is pending.

## Appendix D: Exposure by stratum

The share of analysed clearings and of cleared value per defect class (a failed predicate), per stratum, with the
purchase-document-clustered 95% intervals; classes with no clearing in a stratum are omitted here and kept in
`results/e1/exposure-by-stratum.json`. Company and vendor strata are in the slot file only, as hashed labels. The spend-area
labels are the public log's own strings and the registered strata; the challenge itself names the sector.

{{#strata}}

## Appendix E: Consequence and gate effect by stratum

The H1 and H2 comparisons (Section 5.2) and the gate verdict against the corrective (Section 5.3), at W = 60 days, per stratum.
Each cell gives the O rate with the corrective events and the clearings of its group; "none" marks an empty group. These are
descriptive: the strata are reported beside the estimates and never modelled in. Company and vendor strata are in the slot
files only, as hashed labels.

{{#confounders}}
