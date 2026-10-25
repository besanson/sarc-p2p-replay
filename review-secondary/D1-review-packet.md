# D1 review packet, round 1: paper 7

| field | value |
|---|---|
| paper | Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process |
| author | Gaston Besanson, Universidad Torcuato Di Tella |
| registration | `p7-v1.1`, tag `prereg-p7-v1.1` on commit `d8cdb2d` (supersedes `p7-v1`, tag `prereg-p7-v1` on `e239864`) |
| draft | v0.1, generated from the slot files by `scripts/fill_paper.py` |
| packet date | 2026-10-25, built on the commit after `fa0c5ac` |
| repository | https://github.com/besanson/sarc-p2p-replay |

The registration itself is `prereg/p7-v1.1.md` in the repository; every number in the paper is traceable to its slot file through `results/filled-template.json`. The reply is committed to the repository unedited, with its SHA-256.

## Instructions to the reviewer

Read the paper against its registration. Say where a sentence claims more than its slot supports, where a number lacks a source, where the writing hides a deviation, and what a hostile reviewer would ask first. Reply in any form; your text is committed unedited.

## Part 1. The paper, draft v0.1 (paper/paper.md)

Source: `paper/paper.md`, SHA-256 `0239a377be8649078b0ae6b8e1bcf1f47d60755d935aaf041c2ddd452e5414db`. Copied verbatim between the rules.

---

---
title: "Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process"
author: "Gaston Besanson, Universidad Torcuato Di Tella"
---

<!-- paper/template.md: the source of paper/paper.md. Every number reaches the paper through a
placeholder filled by scripts/fill_paper.py from a slot file under results/. Draft v0.1. -->

## Abstract

Of 155,534 invoice clearings in a real purchase-to-pay event log,
17,748 (11.41%,
clustered bootstrap 95% interval [10.94%, 11.92%]) were made on evidence that
failed at least one of seven registered predicates, carrying 19.41%
of the cleared value ([16.04%, 23.09%]). We replay every clearing of the
BPI Challenge 2019 log through a deterministic min() gate declared before the data were read, reconstructing the evidence held
at clearing time. Clearings that relied on an absent or late goods receipt (D1/D2) were followed by a corrective event within
60 days at a rate of 5.64%, against 0.93%
for clean three-way clearings (difference 0.0470, Holm-adjusted
p = 4.53 × 10^-4^); clearings after a change of price or quantity since approval (D4), at
1.91% against 0.96%
(difference 0.0094, Holm-adjusted p = 3.48 × 10^-7^).
On the same registered sample of lines, the people in the log held 33.0% of
lines with a failed predicate and 34.0% of clean lines; two model families shown
the ERP view held 100.0% and 99.6% of the first
and 53.0% and 57.3% of the second; the gate holds the first
and allows the second by construction. Paper 5's compiler, given the three declared losses of the registration, does not
reproduce the registered contract in any item category. The coverage matrix states which defect classes this log cannot
expose; the authority defect class (D5) has zero incidence here. No causal claim is made.

## 1 Introduction

Papers 1 to 6 of this programme showed the mechanism of a silent evidence defect, a decision taken on evidence that fails a
metadata-borne predicate, on constructed domains, and made no prevalence claim. This paper is that number, on one real
process.

The unit is an invoice clearing in the BPI Challenge 2019 purchase-to-pay log. For each clearing we reconstruct the evidence
recorded on the purchase-order line at clearing time, evaluate the registered predicates D1 to D7, record what the gate would
have held, and read what followed in the log. We report exposure in count and in anonymised EUR, the corrective events that
follow a failed predicate, the reach of the gate, and, on a registered sample, what two model families decide on the same
ERP view beside the people in the log and the gate. Everything was registered before the log was parsed (tag `prereg-p7-v1`)
and amended once after the pilot, before any estimate (tag `prereg-p7-v1.1`); every deviation is listed in Section 4.

What this paper claims is in the claim table of Appendix B. What it does not claim is stated in the repository's claims file
and repeated here verbatim:

- No causal claim. Correctives are a proxy, observational, confounded by vendor, category and practice.
- No loss figure. A corrected payment is not money gone; recovery is not in the log.
- No claim that the gate stops anything. Held lines go somewhere the log does not show.
- No claim about the company or any vendor. No company, subsidiary or vendor is named in any finding.
- No agent acting on the live system and no agent with tools.
- No readiness threshold.

## 2 Related work

This paper does not introduce conformance checking, the three-way match or rework analysis. It replays each clearing as a
gate decision over the evidence reconstructed from the event log at clearing time, measures how often that evidence was
defective and what followed, and puts people, models and the gate on the same lines. The defect classes are the predicates
of Section 3.

**Conformance and compliance checking.** Checking recorded behaviour against a normative model or rule set is established
(van der Aalst 2016; Ly et al. 2015), and declarative constraints in the Declare
family take a process model as the conjunction of its constraints (Pesic et al. 2007). The predicates D1 to D7 are
compliance rules in this sense, and taking the decision as their conjunction is Declare's. Synthesising a sufficient contract
from declared losses is paper 5 of this programme (Besanson 2026); the compiler used in Section 5.5 is
paper 5's. Detecting that one resource performed two activities that must be separated is a standard compliance monitoring
functionality (Ly et al. 2015); predicate D5 is that check.

**The BPI Challenge 2019 reports.** The challenge posed the process owner's compliance questions on this very log, including
clearing before goods receipt and the three-way match per item category (ICPM 2019). The submitted
reports measured basic violation rates and are prior art for every basic rate reported here; among them
Diba et al. 2019 quantify receipt-before-clearing violations with their value, and
Porter et al. 2019 report compliance per item category both by number and by value. Measuring compliance by
count and by value is therefore not claimed; what is claimed is the tabulation per clearing and per defect class, with
clustered intervals. The three-way match itself is a textbook application control (PCAOB 2004); Section 5.5 asks
whether paper 5's compiler re-derives it from declared losses.

**Deviation and outcome.** Relating a deviation to a later outcome in the same case is established: the extension of process
mining to outcomes associated with deviations (Peleg et al. 2008), outcome-oriented predictive process
monitoring (Teinemaa et al. 2019) and deviance mining (Nguyen et al. 2016). On this log,
Porter et al. 2019 observe cancellations of invoice receipts long after clearing as a case-study observation.
Corrective events as rework signals are established on this log too: Meyer zu Wickern et al. 2019 count change,
cancel and delete activities as rework, and Badakhshan et al. 2019 list vendor debit memos among rework
activities. The outcome proxy of Section 3 is a rework signal of this kind; H1 to H3 are registered conditional-consequence
studies of the deviation-to-outcome shape.

**Detectability.** That some deviations leave no trace in an event log is established (Outmazgin and Soffer 2013).
The registered per-class coverage matrix of Section 6 is claimed; the principle is not.

**Deciders on the same cases.** Putting different deciders on the same cases is established: a human reviewer, a model agent
and learned rules on the same accounts (Palma et al. 2026), language models against audit baselines on
the same ledgers (Kadir et al. 2025), and algorithms against bank managers (Harding and Vasconcelos 2022).
None of these uses a deterministic contract declared before the data were read, or a human arm read from a process event log;
Section 5.4 does both.

**The BPI Challenge 2020 reports.** The 2020 challenge posed questions on the approval chain of travel declarations
(ICPM 2020); two reports received awards (ICPM 2020; Pufahl et al. 2020;
Kas et al. 2020). They are prior art for the basic rates of the replication in Section 5.7.

## 3 Formal core

**Lines, clearings and evidence.** A line is one case of the log: one purchase document and item. A clearing is one
`Clear Invoice` event on a line at time t_c. The evidence at t_c is every event on the line with timestamp at most t_c,
excluding the clearing itself; events sharing a timestamp count as available, and counts rather than event order decide
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

| id | name | dimension | fails when, on the line before t_c |
|---|---|---|---|
| D1 | receipt present | presence | no uncancelled goods receipt (receipts minus receipt cancellations at most zero) |
| D2 | receipt before clearing | freshness, order | no uncancelled receipt precedes t_c |
| D3 | invoice present | presence | no invoice receipt |
| D4 | unchanged since approval | validity | a price or quantity change after the last approval-bearing event |
| D5 | distinct actors | authority | the actor of the clearing equals an actor of the earliest creation (unknown if either is missing) |
| D6 | block respected | scope | a payment block set and not removed |
| D7 | not deleted | validity | the line deleted or blocked and not reactivated |

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

| record | DOI | licence | file | cases | events | SHA-256 |
| --- | --- | --- | --- | ---: | ---: | --- |
| BPI Challenge 2019 | doi:10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1 | CC BY 4.0 | `BPI_Challenge_2019.xes` | 251,734 | 1,595,923 | `af63bc687fc4152f2123b05c3af7772b37ef3fce2d3f67f812666c9e356baae7` |
| BPI Challenge 2020: International Declarations | doi:10.4121/uuid:2bbf8f6a-fc50-48eb-aa9e-c4ea5ef7e8c5 | CC BY-NC 4.0 | `InternationalDeclarations.xes.gz` | 6,449 | 72,151 | `b527c8d06255f4312c6ce8f36f7f4110243d84fd6ca48583cd9b80896c601494` |
| BPI Challenge 2020: Domestic Declarations | doi:10.4121/uuid:3f422315-ed9d-4882-891f-e180b5b4feb5 | CC BY-NC 4.0 | `DomesticDeclarations.xes.gz` | 10,500 | 56,437 | `0bc3312acf0b9ee5ae6f4ebe9df204005ef11665d62f2d21dd04995161d7532b` |

Values in the 2019 log are anonymised by a linear translation that respects zero; we report them as anonymised EUR.

**Window, observation end and frame.** A line is in the window if its earliest `Create Purchase Order Item` event lies in
calendar 2018. The observation end T_end is the latest timestamp in the last calendar month that carries at least 1,000
events; here T_end is 2019-01-18 and 9 later
events are excluded. A line is framed if it survives the exclusions below and its first clearing, or its creation if it has
none, lies at least W before T_end; the analysed clearings are every clearing on a framed line at least W before T_end, so
every outcome window is complete. The lines drawn for the pilot (E0) are removed before any estimate.

| step | lines |
| --- | ---: |
| lines in the log | 251,734 |
| 2.1 (1) no Create Purchase Order Item | 0 |
| 2.1 (2) consignment | 14,498 |
| 3.1 category undefined by the flags | 0 |
| 2.1 (3) zero or missing line value | 1,887 |
| 2.1 (4) more than K = 12 clearings | 78 |
| 2.1 (5) outside the window | 376 |
| 2.1 (5) failing the frame condition | 53,731 |
| framed lines | 181,164 |
| E0 pilot lines removed | 500 |
| framed lines analysed | 180,664 |
| analysed clearings | 155,534 |
| events after T_end excluded | 9 |

**Registration.** The registration was tagged `prereg-p7-v1` before any parse of the log beyond the published counts. The
pilot fired registered stop conditions (the latest timestamp lay outside the registered range, and a mapped attribute is
named differently in the log than on the record page); the registration was amended and tagged `prereg-p7-v1.1`, and the
pilot was drawn again, before any estimate. Every deviation, with the decision that records its reason:

- p7-v1 to p7-v1.1: T_end rule.
- p7-v1 to p7-v1.1: Mapping attribute name.
- p7-v1 to p7-v1.1: Section 3.6, explicit sentence.
- Under p7-v1.1: H3 convention.
- Under p7-v1.1: D5 applicability at a non-clearing decision point.

The H3 convention and the D5 reading were the author's decisions after E2 and E3 and before any model call (decision D-C-2 in
Appendix B). Before the tag, the prior-art fence was reviewed externally, after two machine sweeps whose output is committed
unedited.

## 5 Results

### 5.1 Exposure (E1)

| defect class | clearings | share | Wilson 95% | bootstrap 95% | share of value | bootstrap 95% |
| --- | ---: | ---: | --- | --- | ---: | --- |
| D1 class (absent receipt) | 610 | 0.39% | [0.36%, 0.42%] | [0.30%, 0.50%] | 0.12% | [0.08%, 0.17%] |
| D2 class (stale receipt) | 82 | 0.05% | [0.04%, 0.07%] | [0.02%, 0.10%] | 0.12% | [0.03%, 0.27%] |
| D3 | 362 | 0.23% | [0.21%, 0.26%] | [0.15%, 0.33%] | 0.03% | [0.02%, 0.05%] |
| D4 | 17,157 | 11.03% | [10.88%, 11.19%] | [10.55%, 11.53%] | 19.24% | [15.88%, 22.89%] |
| D5 | 0 | 0.00% | [0.00%, 0.00%] | [0.00%, 0.00%] | 0.00% | [0.00%, 0.00%] |
| D6 | 4 | 0.00% | [0.00%, 0.01%] | [0.00%, 0.01%] | 0.03% | [0.00%, 0.10%] |
| D7 | 19 | 0.01% | [0.01%, 0.02%] | [0.01%, 0.02%] | 0.01% | [0.00%, 0.02%] |
| at least one defect | 17,748 | 11.41% | [11.25%, 11.57%] | [10.94%, 11.92%] | 19.41% | [16.04%, 23.09%] |
| held on an unknown only (not a defect) | 0 | 0.00% | [0.00%, 0.00%] | [0.00%, 0.00%] | 0.00% | [0.00%, 0.00%] |

Figure 1 shows the shares with their intervals. Shares of clearings carry a Wilson and a purchase-document-clustered
bootstrap 95% interval (B = 10,000, seed 20261201); shares of value carry the clustered interval. The denominator is every
analysed clearing; D1 and D2 classes apply to 155,346 clearings
in the three-way categories. A change after approval (D4) is the largest defect class, 17,157
clearings and 19.24% of cleared value; no clearing fails D5. Appendix D gives the same
shares per item category, spend area, month, line value quartile and vendor activity quartile, reported beside the estimates and
never modelled in.

![Figure 1: share of analysed clearings and of cleared value per defect class, with clustered bootstrap 95% intervals.](figures/fig1-exposure.svg)

### 5.2 Consequence (E2)

| test | defect group (failed predicate): O rate | comparison: O rate | difference | bootstrap SE | z | p (raw, one-sided) | p (Holm) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| H1 | 39 of 692 (5.64%) | 1,286 of 137,602 (0.93%) | 0.0470 | 0.0127 | 3.688 | 1.13 × 10^-4^ | 4.53 × 10^-4^ |
| H2 | 327 of 17,157 (1.91%) | 1,332 of 138,377 (0.96%) | 0.0094 | 0.0018 | 5.266 | 6.96 × 10^-8^ | 3.48 × 10^-7^ |
| H3 | 0 of 0 (n/a) | 1,659 of 155,534 (1.07%) | n/a | n/a | n/a | not computable | 1 |

O is the registered corrective within W = 60 days. The H1 comparison group is three-way clearings with every applicable
predicate passing; against clean clearings of every category the difference is 0.0470,
descriptively. H2 compares D4 fail with D4 pass in every category. Standard errors come from the purchase-document-clustered
bootstrap. Holm's adjustment runs over the registered family of five tests, H1, H2, H3 and H4 for each model family, at
alpha = 0.05:

| test | p (raw) | rank | multiplier | p (Holm) | below alpha |
| --- | ---: | ---: | ---: | ---: | --- |
| H2 | 6.96 × 10^-8^ | 1 | 5 | 3.48 × 10^-7^ | yes |
| H1 | 1.13 × 10^-4^ | 2 | 4 | 4.53 × 10^-4^ | yes |
| H3 | 1 | 3 | 3 | 1 | no |
| H4-Haiku | 1 | 4 | 2 | 1 | no |
| H4-Jev | 1 | 5 | 1 | 1 | no |

H3, distinct actors, is not computable: defect group has no analysed clearings. No clearing in this log was
made by the person who created its line, so the defect class has zero incidence; H3 enters the family with p = 1, the
convention the author fixed before any H4 value existed. At W = 30 days the differences are 0.0354
for H1 and 0.0055 for H2, descriptively.

### 5.3 Gate effect and hold cost (E3)

The gate would have held 17,748 of 155,534 analysed clearings
(11.41%, 19.41% of cleared value); 0
of them were held on an unknown predicate value alone. Against the corrective at W = 60 days, in clearings and anonymised EUR (Figure 4):

| gate verdict | corrective within W | no corrective within W |
| --- | ---: | ---: |
| would have held | 368 (21,418,557) | 17,380 (145,068,897) |
| would have allowed | 1,291 (106,294,821) | 136,495 (584,977,346) |

![Figure 4: gate verdict against the corrective within W = 60 days, in clearings and in cleared value.](figures/fig4-verdict-outcome.svg)

For D1/D2 failures, the time from clearing to the first uncancelled receipt (Figure 3):

| lag band | clearings | cleared value |
| --- | ---: | ---: |
| [0, 1] days | 11 | 109,886 |
| (1, 7] days | 21 | 113,119 |
| (7, 30] days | 11 | 803,512 |
| over 30 days | 39 | 44,240 |
| never (by T_end) | 610 | 1,015,565 |

![Figure 3: D1/D2 failures by lag band, in clearings and cleared value.](figures/fig3-lag-bands.svg)

**Human hold.** Of 180,664 framed lines, people held 53,262 and
released 101,777; 25,625 had no invoice
receipt by T_end − W and are not classified. The status of a line is the gate verdict at the decision point t* of the agent
replay: the first clearing if it came within W of the first invoice receipt, otherwise that receipt plus W. The registered
text left D5 at a t* that is not a clearing undefined; read literally it is unknown, and then a line held by people can never
be clean. The author amended the reading before any model call (D5 is not applicable where the decider is the gate or a
model, decision D-C-2 B); both readings are reported:

| reading | predicate status at t* | classified lines | held by people | human hold rate |
| --- | --- | ---: | ---: | ---: |
| literal (registered text) | defective | 16,264 | 5,664 | 34.83% |
| literal (registered text) | clean | 91,178 | 1 | 0.00% |
| literal (registered text) | held unknown | 47,597 | 47,597 | 100.00% |
| amended (D-C-2 B) | defective | 16,264 | 5,664 | 34.83% |
| amended (D-C-2 B) | clean | 138,775 | 47,598 | 34.30% |
| amended (D-C-2 B) | held unknown | 0 | 0 | n/a |

Under the amended reading, people held 34.83% of
lines with a failed predicate at t* and 34.30% of clean
lines.

### 5.4 People, models and the gate on the same lines (E4)

**Sample and arms.** From the framed lines with an invoice receipt, 18,006 had at least
one failed predicate at t* and 147,240 were clean (under D-C-2 B). The registered sample
drew 1,000 defective and 1,000 clean lines, at most one per purchase document, stratified by category and value quartile, with
seed 20261201; the draw was committed before any call. Each line was shown to two model families as the registered ERP view at
t*, a short record with no event timeline and no company, vendor, actor or line id: TypeSafe System One (Jev, returned model
`jev-1.14.0`) through `typesafe-sdk==0.7.2`, asked one choice question with labels clear and hold, and the Anthropic Messages API
(`claude-haiku-4-5-20251001`, temperature zero, assistant prefill), asked for a JSON decision and hold probability.
Invalid replies, after one re-request: 0 for Jev and 0 for Haiku. The people arm is read from the log (Section 3); the gate holds every
line with a failed predicate and allows every clean line by construction.

| arm | hold rate, lines with a failed predicate | hold rate, clean lines | kappa with gate | value released on lines with a failed predicate | expected correctives |
| --- | ---: | ---: | ---: | ---: | ---: |
| people (from the log) | 33.0% (301 of 912) | 34.0% (318 of 936) | n/a | 4,759,520 | 12.260 |
| Jev | 100.0% (1,000 of 1,000) | 53.0% (530 of 1,000) | 0.470 | 0 | 0.000 |
| Haiku | 99.6% (996 of 1,000) | 57.3% (573 of 1,000) | 0.423 | 7,307 | 0.076 |
| gate | 100.0% (1,000 of 1,000) | 0.0% (0 of 1,000) | n/a | 0 | 0.000 |

| family | d (failed predicate minus clean) | SE | p, lower | p, upper | p_TOST |
| --- | ---: | ---: | ---: | ---: | ---: |
| H4-Jev | 0.470 | 0.0158 | 2.33 × 10^-238^ | 1 | 1 |
| H4-Haiku | 0.423 | 0.0158 | 5.54 × 10^-198^ | 1 | 1 |

![Figure 2: hold rate on lines with a failed predicate and on clean lines, per arm; the exploratory timeline arm in its own panel.](figures/fig2-hold-rates.svg)

H4 asks whether each family's hold rate on defective lines (a failed predicate) is within m = 0.05 of its rate on clean lines.
Neither is: Jev held 100.0% and 53.0%, Haiku held
99.6% and 57.3%; p_TOST is
1 for Jev and 1 for Haiku, and H4 is below alpha after Holm for
neither. Both families track the gate's verdict on the lines
the gate would have held and hold about half of the lines it allows (Cohen's kappa with the gate
0.470 and 0.423). People, by contrast, held lines with and
without a failed predicate at nearly the same rate. Released on lines with a failed predicate, in anonymised EUR: people
4,759,520, Jev 0,
Haiku 7,307, gate 0;
the expected correctives (released lines with a failed predicate times the E2 O rate of their defect group) are in the table.
The ERP view hands each model the inputs of the predicates; this result is about the view as much as about the models.

**Exploratory: the event timeline instead of the ERP view.** Labelled exploratory and outside the Holm family: the same lines,
the same families and rules, with the line's events up to t* (date, activity, value) in place of the ERP view.

| family (timeline view, exploratory) | hold rate, lines with a failed predicate | hold rate, clean lines | kappa with gate | invalid replies |
| --- | ---: | ---: | ---: | ---: |
| Jev | 12.6% | 3.8% | 0.088 | 0 |
| Haiku | 9.5% | 3.9% | 0.056 | 0 |

Given the timeline, both families held far fewer lines with a failed predicate. Spend for both arms together was USD
1.57 against the registered cap of USD 60.

### 5.5 Derivation (E5)

Paper 5's compiler, at the pinned commit and unmodified, was given per category the observed states of the evidence set and
the three declared losses of the registration: L1, pay for goods not received (the category requires a goods receipt and none
is uncancelled); L2, pay twice (the clearing's position among the line's clearings exceeds the invoices recorded); L3, pay a
changed amount (a change since approval). The derived contract is the set of registered predicates whose observation is in
the compiler's minimum-cardinality sufficient set.

| category | clearings | states | L1 | L2 | L3 | fewest fields | derived contract | registered contract | result |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 2-way | 188 | 3 | 0 | 0 | 4 | `changes` | D4 | D3, D4, D5, D6, D7 | does not reproduce |
| 3-way, invoice after receipt | 9,640 | 896 | 0 | 81 | 1,585 | `changes`, `clearing_ordinal`, `invoices` | D3, D4 | D1, D2, D3, D4, D5, D6, D7 | does not reproduce |
| 3-way, invoice before receipt | 145,706 | 758 | 692 | 1,390 | 15,568 | `changes`, `clearing_ordinal`, `invoices`, `receipts` | D1, D2, D3, D4 | D1, D2, D3, D4, D5, D6, D7 | does not reproduce |

The compiler does not reproduce the registered contract in any category. The three losses derive at most D1 to D4: no
declared loss reads the observations of D5, D6 or D7, so those predicates guard losses the registration did not declare (an
authority loss, a blocked payment, a deleted line). Pay twice needs the clearing's position on its line, an observation no
registered predicate reads.

### 5.6 Governance cost (E6)

The full replay of every line, from reading the log to the written evidence set, took a median of
153.5 seconds over three runs on a 4-core machine,
0.000987 seconds per gate decision. A model decision cost USD
0.000022 with Jev and USD 0.000368 with Haiku.

### 5.7 Replication on travel declarations (E7)

The unit is a payment on a declaration case at least W before the latest timestamp of its log; D1' approval present, D2'
approval by the required role and D3' unchanged after approval are evaluated before the payment, and O' is a rejection or
resubmission within W after it. Descriptive and secondary, outside the Holm family.

| log | cases | payments | excluded after T_end' − W | units |
| --- | ---: | ---: | ---: | ---: |
| domestic | 10,500 | 10,044 | 2 | 10,042 |
| international | 6,449 | 6,187 | 0 | 6,187 |

| scope | predicate | failing payments | O' rate, failing | O' rate, all-pass | difference | bootstrap 95% |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| domestic | D1' | 2 | 0.500 | 0.000 | 0.500 | [0.0000, 1.0000] |
| domestic | D2' | 2 | 0.500 | 0.000 | 0.500 | [0.0000, 1.0000] |
| domestic | D3' | 0 | n/a | 0.000 | n/a | n/a |
| international | D1' | 0 | n/a | 0.000 | n/a | n/a |
| international | D2' | 0 | n/a | 0.000 | n/a | n/a |
| international | D3' | 0 | n/a | 0.000 | n/a | n/a |
| pooled | D1' | 2 | 0.500 | 0.000 | 0.500 | [0.0000, 1.0000] |
| pooled | D2' | 2 | 0.500 | 0.000 | 0.500 | [0.0000, 1.0000] |
| pooled | D3' | 0 | n/a | 0.000 | n/a | n/a |

The replication is inconclusive. Only 2 of 16,229
payments fail any predicate, and O' follows 0 of the
16,227 payments with every predicate passing; no comparison has an interval
excluding zero. The registered names `Declaration FINAL_APPROVED by DIRECTOR` and
`Declaration REJECTED by DIRECTOR` do not occur in the domestic log; they are reported with zero counts,
not replaced.

## 6 Coverage

What the replay can and cannot see, as registered:

**Detected (BPI 2019, E1 to E6)**

| defect class | predicate | dimension | detected from |
|---|---|---|---|
| goods receipt required but absent at clearing | D1 receipt_present | presence | no `Record Goods Receipt` before t_c, or every one cancelled by a later `Cancel Goods Receipt` before t_c, on a line whose category requires receipt |
| stale receipt: receipt recorded after clearing | D2 receipt_before_clearing | freshness, order | the first uncancelled `Record Goods Receipt` falls after t_c (lag band registered) |
| invoice absent at clearing | D3 invoice_present | presence | no `Record Invoice Receipt` before t_c |
| changed after approval | D4 unchanged_since_approval | validity | `Change Price` or `Change Quantity` between the last approval-bearing event and t_c |
| same actor created and cleared | D5 distinct_actors | authority | actor of `Create Purchase Order Item` equals actor of `Clear Invoice` |
| clearing under an open payment block | D6 block_respected | scope | `Set Payment Block` before t_c with no later `Remove Payment Block` before t_c |
| line deleted or blocked at clearing | D7 not_deleted | validity | `Delete Purchase Order Item` or `Block Purchase Order Item` before t_c with no later `Reactivate Purchase Order Item` before t_c |

**Detected (BPI 2020 declarations, E7, secondary)**

| defect class | predicate | dimension | detected from |
|---|---|---|---|
| paid without final approval | D1' approval_present | presence | no final approval event before the payment event |
| approved by a role other than the required one | D2' approval_by_required_role | authority | the approval chain before payment lacks the registered required role |
| declaration changed after approval | D3' unchanged_since_approval | validity | a resubmission by the employee between the last approval and payment |

**Undetected, with reason**

| defect class | reason |
|---|---|
| wrong amounts in the payload | values are anonymised by a linear translation; the log carries cumulative net worth per event, not invoice line content, so a mismatch between invoice text and goods is not observable |
| fraud | intent is not an event attribute; no predicate over the log separates a fraudulent clearing from an erroneous one, and the paper makes no statement about it |
| vendor identity (wrong, duplicate or fictitious vendor) | vendor names and ids are anonymised consistently; the log carries no master-data change history or bank details |
| recovery of corrected payments | the log ends at the corrective event; whether money was returned, offset or written off is not recorded |
| what a held line becomes | a gate hold is a replay verdict; the log records the human path only, so the fate of a line the gate would have held is not observable |
| approvals outside the log | approvals given by e-mail, in another system or verbally leave no event; D4's "last approval-bearing event" sees only logged approvals |
| partial receipt and value mismatch per receipt | the replay checks presence and order of the receipt, not the matched values; values are anonymised and the registered mapping reads no per-receipt quantity |
| duplicate invoice across lines | the case is one purchase-order line and the registered mapping carries no invoice document id, so an invoice cleared on two lines is not linked |

The authority class (D5) is detectable and has zero incidence in this log (0 failed
clearings); the coverage check found every other detected class with at least one failure.

## 7 Limitations and non-claims

The outcome is a proxy: a corrective event after a clearing is not proof that the clearing was wrong, and the study is
observational. Category, spend area, value, vendor activity and month are reported beside every estimate and never modelled
in. Values are anonymised. What a line the gate would have held becomes is not in the log. The ERP view hands the model the
inputs of the predicates; the exploratory timeline arm shows that a different view changes what the models decide, which is a
statement about views, not about the models alone. The derivation depends on how the three declared losses are expressed over
the evidence set; the expressions are recorded with the result. One company's process, one year.

## 8 Conclusion

11.41% of 155,534 invoice clearings in
this process relied on evidence that failed at least one registered predicate, carrying 19.41%
of the cleared value; those that relied on an absent or late receipt, or on a changed amount, were followed by a corrective at
a higher rate than clean clearings.

## Acknowledgements

The prior-art fence was reviewed externally by Eduardo Arana before the registration was tagged. AI tools were used as support:
builder sessions with Claude for the code, the runs and the drafting from slots, and two machine prior-art sweeps, with ChatGPT
and with DeepSeek, committed unedited. The author is solely responsible for every claim. We thank the organisers of the BPI
Challenges and 4TU.ResearchData for the logs.

## References

- <!-- ref:bpi2019-nonstudent-4-badakhshan -->Peyman Badakhshan, Samuel Gosling, Jerome Geyer-Klingeberg, Janina Nakladal, Johannes Schukat, Jennifer Gsenger (2019). Process Mining in the Coatings and Paints Industry: The Purchase Order Handling Process. BPI Challenge 2019 report, non-student category, ICPM 2019. https://icpmconference.org/2019/wp-content/uploads/sites/6/2019/07/BPI-Challenge-Submission-4.pdf
- <!-- ref:besanson-paper5-2026 -->Gaston Besanson (2026). Compiling Sufficient Governance Context from Declared Losses and Reachable States: Exact Observation-Contract Synthesis with Cardinality and Cost Objectives. arXiv:2609.26016 (paper 5 of this programme; CITATION.cff of sarc-authority-derivation). https://arxiv.org/pdf/2609.26016
- <!-- ref:bpi2019-nonstudent-6-diba -->Kiarash Diba, Simon Remy, Luise Pufahl (2019). BPI Challenge 2019: Performance and Compliance Analysis of Procurement Processes Using Process Mining. BPI Challenge 2019 report, non-student category, ICPM 2019. https://icpmconference.org/2019/wp-content/uploads/sites/6/2019/07/BPI-Challenge-Submission-6.pdf
- <!-- ref:harding-managers-machines-2022 -->Matthew Harding, Gabriel F. R. Vasconcelos (2022). Managers versus Machines: Do Algorithms Replicate Human Intuition in Credit Ratings?. arXiv:2202.04218 (submitted 2022-02-09). https://arxiv.org/abs/2202.04218
- <!-- ref:icpm-bpi-challenge-2019-page -->ICPM 2019 (2019). BPI Challenge 2019 (ICPM 2019 conference page). https://icpmconference.org/2019/bpi-challenge/
- <!-- ref:icpm-2020-awards-page -->ICPM 2020 (2020). Awards (ICPM 2020). https://icpmconference.org/2020/awards/
- <!-- ref:icpm-bpi-challenge-2020-page -->ICPM 2020 (2020). BPI Challenge 2020 (ICPM 2020 conference page). https://icpmconference.org/2020/bpi-challenge/
- <!-- ref:kadir-auditcopilot-2025 -->Md Abdul Kadir, Sai Suresh Macharla Vasu, Sidharth S. Nair, Daniel Sonntag (2025). AuditCopilot: Leveraging LLMs for Fraud Detection in Double-Entry Bookkeeping. arXiv:2512.02726 (submitted 2025-12-02). https://arxiv.org/abs/2512.02726
- <!-- ref:bpi2020-student-award-kas -->Stijn Kas, Ruben Post, Sebastiaan Wiewel (2020). Automated Machine Learning in a Process Mining Context. BPI Student Challenge Award, ICPM 2020. https://icpmconference.org/2020/wp-content/uploads/sites/4/2020/10/ICPM_2020_paper_44.pdf
- <!-- ref:ly-compliance-monitoring-2015 -->Linh Thao Ly, Fabrizio Maria Maggi, Marco Montali, Stefanie Rinderle-Ma, Wil M.P. van der Aalst (2015). Compliance monitoring in business processes: Functionalities, application, and tool-support. Information Systems 54, 209-234 (December 2015), Elsevier. doi:10.1016/j.is.2015.02.007
- <!-- ref:bpi2019-student-4-meyerzuwickern -->Vincent Finn Alexander Meyer zu Wickern, Mounisha Juluru, Anshu Roy, Viet-Hung Vu, Thi-Thu-Hang Nguyen (2019). Analysis and prediction of purchasing compliance using process mining. BPI Challenge 2019 report, student category, ICPM 2019. https://icpmconference.org/2019/wp-content/uploads/sites/6/2019/07/BPI-Challenge-Student-Submission-4.pdf
- <!-- ref:nguyen-deviance-mining-2016 -->Hoang Nguyen, Marlon Dumas, Marcello La Rosa, Fabrizio Maria Maggi, Suriadi Suriadi (2016). Business Process Deviance Mining: Review and Evaluation. arXiv:1608.08252 (submitted 2016-08-29). https://arxiv.org/abs/1608.08252
- <!-- ref:outmazgin-workarounds-2013 -->Nesi Outmazgin, Pnina Soffer (2013). Business Process Workarounds: What Can and Cannot Be Detected by Process Mining. Enterprise, Business-Process and Information Systems Modeling (BPMDS 2013, EMMSAD 2013), LNBIP vol. 147, pp. 48-62, Springer. doi:10.1007/978-3-642-38484-4_5
- <!-- ref:palma-business-compromise-2026 -->Diego Palma, Kyu Bin Kim, Zhen Han, Allbright Dsouza, Zhiyuan Liu (2026). Business Compromise Detection with Agentic AI and LLM-driven Knowledge Discovery. arXiv:2609.32643 (submitted 2026-09-26). https://arxiv.org/html/2609.32643
- <!-- ref:pcaob-release-2004-001 -->Public Company Accounting Oversight Board (2004). An Audit of Internal Control Over Financial Reporting Performed in Conjunction with an Audit of Financial Statements (PCAOB Release No. 2004-001). PCAOB Release 2004-001, March 9, 2004. https://pcaobus.org/Rulemaking/Docket008/2004-03-09_Release_2004-001-all.pdf
- <!-- ref:peleg-mining-outcomes-2008 -->Mor Peleg, Pnina Soffer, Johny Ghattas (2008). Mining Process Execution and Outcomes – Position Paper. Business Process Management Workshops (BPM 2007), LNCS vol. 4928, pp. 395-400, Springer. doi:10.1007/978-3-540-78238-4_40
- <!-- ref:pesic-declare-2007 -->Maja Pesic, Helen Schonenberg, Wil M.P. van der Aalst (2007). DECLARE: Full Support for Loosely-Structured Processes. 11th IEEE International Enterprise Distributed Object Computing Conference (EDOC 2007), p. 287, IEEE. doi:10.1109/EDOC.2007.14
- <!-- ref:bpi2019-nonstudent-8-porter -->Adrien Porter, David Masse, Nuss Visatemongkolchai, Jithendra Seneviratne, Tanvee Deokule, Nicholas Hartman (2019). Balancing Efficiency and Risk in Procure to Pay: Safely Realizing Cost Savings Using Process Mining Techniques. BPI Challenge 2019 report, non-student category, ICPM 2019. https://icpmconference.org/2019/wp-content/uploads/sites/6/2019/07/BPI-Challenge-Submission-8.pdf
- <!-- ref:bpi2020-award-hobeck -->Luise Pufahl, Richard Hobeck, Paul Binetruy, Wepan Chada, Mykola Digtiar, Kim Julian Gülle, Marta Slarzynska, Fabian Stiehle, Ingo Weber (2020). Performance, Variant, and Conformance Analysis of an Academic Travel Reimbursement Process. BPI Challenge Award, ICPM 2020. https://icpmconference.org/2020/wp-content/uploads/sites/4/2020/10/ICPM_2020_paper_148.pdf
- <!-- ref:teinemaa-outcome-ppm-2019 -->Irene Teinemaa, Marlon Dumas, Marcello La Rosa, Fabrizio Maria Maggi (2019). Outcome-Oriented Predictive Process Monitoring. ACM Transactions on Knowledge Discovery from Data 13(2), 2019. doi:10.1145/3301300
- <!-- ref:vanderaalst-process-mining-2016 -->Wil van der Aalst (2016). Process Mining: Data Science in Action. Springer Berlin, Heidelberg, second edition. doi:10.1007/978-3-662-49851-4
- Boudewijn van Dongen. BPI Challenge 2019. 4TU.ResearchData, CC BY 4.0. doi:10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1
- Boudewijn van Dongen. BPI Challenge 2020: International Declarations. 4TU.ResearchData, CC BY-NC 4.0. doi:10.4121/uuid:2bbf8f6a-fc50-48eb-aa9e-c4ea5ef7e8c5
- Boudewijn van Dongen. BPI Challenge 2020: Domestic Declarations. 4TU.ResearchData, CC BY-NC 4.0. doi:10.4121/uuid:3f422315-ed9d-4882-891f-e180b5b4feb5

## Appendix A: Registration summary

The registered numbers, Section 9 of the registration:

| item | value |
|---|---|
| window | Create Purchase Order Item in calendar 2018 (UTC) |
| W | 60 days; sensitivity 30 days |
| lag bands | [0, 1], (1, 7], (7, 30], over 30 days, never |
| K (framework exclusion) | more than 12 clearings |
| E0 | 500 lines |
| E4 | N_d = 1,000, N_c = 1,000; m = 0.05 |
| alpha | 0.05, Holm over H1, H2, H3, H4-Jev, H4-Haiku |
| bootstrap | B = 10,000, purchase-document clusters |
| seed | 20261201 |
| cap | USD 60 |
| pins | `engines.lock` at this commit |

## Appendix B: Claims, decisions and deviations

Claim statuses, each set from its slot file:

| claim | status | evidence |
| --- | --- | --- |
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

Every decision taken while the work ran is in the repository's decision log, from D-A0-1 to D-C-5, and every deviation from
the tagged registration is in its deviations file (Section 4).

## Appendix C: Reproduction

`make bootstrap` clones the sibling repositories at their pins, creates the environment, fetches the logs and checks their
hashes; `make test` and `make lint` run the tests and the lints; `make gates` runs the release gates G1 to G9; the experiment
runners regenerate every slot under `results/`, and `make paper` regenerates this paper and its figures from the slots. The
internal double runs were byte-identical (16 files for E1 to E3); external
reproduction from a clean clone is pending.

## Appendix D: Exposure by stratum

The share of analysed clearings with at least one failed predicate (any defect class), per stratum. Company and vendor strata
are in the slot file only, as hashed labels.

**Item category**

| stratum | clearings | at least one failed predicate | share | Wilson 95% | share of value |
| --- | ---: | ---: | ---: | --- | ---: |
| 2-way | 188 | 4 | 2.13% | [0.83%, 5.34%] | 2.68% |
| 3-way, invoice after receipt | 9,640 | 1,592 | 16.51% | [15.79%, 17.27%] | 15.67% |
| 3-way, invoice before receipt | 145,706 | 16,152 | 11.09% | [10.93%, 11.25%] | 22.21% |

**Spend area**

| stratum | clearings | at least one failed predicate | share | Wilson 95% | share of value |
| --- | ---: | ---: | ---: | --- | ---: |
| Additives | 10,206 | 1,219 | 11.94% | [11.33%, 12.59%] | 14.07% |
| CAPEX & SOCS | 4,672 | 332 | 7.11% | [6.40%, 7.88%] | 26.35% |
| Chemicals & Intermediates | 1 | 0 | 0.00% | [0.00%, 79.35%] | 0.00% |
| Commodity Resins | 306 | 81 | 26.47% | [21.84%, 31.68%] | 28.67% |
| Energy | 3 | 0 | 0.00% | [0.00%, 56.15%] | 0.00% |
| Enterprise Services | 370 | 22 | 5.95% | [3.96%, 8.84%] | 7.30% |
| Latex & Monomers | 2,584 | 488 | 18.89% | [17.42%, 20.44%] | 18.82% |
| Logistics | 2,069 | 114 | 5.51% | [4.61%, 6.58%] | 6.11% |
| Marketing | 1,220 | 114 | 9.34% | [7.84%, 11.11%] | 47.22% |
| Others | 1,776 | 94 | 5.29% | [4.34%, 6.43%] | 9.16% |
| Packaging | 63,561 | 7,035 | 11.07% | [10.83%, 11.31%] | 19.13% |
| Pigments & Colorants | 1,694 | 297 | 17.53% | [15.80%, 19.42%] | 29.37% |
| Real Estate | 151 | 5 | 3.31% | [1.42%, 7.52%] | 12.38% |
| Sales | 46,891 | 3,378 | 7.20% | [6.97%, 7.44%] | 16.24% |
| Solvents | 1,573 | 219 | 13.92% | [12.30%, 15.72%] | 16.64% |
| Specialty Resins | 1,295 | 228 | 17.61% | [15.63%, 19.78%] | 17.00% |
| Spend Area Unidentified | 18 | 3 | 16.67% | [5.84%, 39.22%] | 9.65% |
| Titanium Dioxides | 429 | 124 | 28.90% | [24.82%, 33.37%] | 37.05% |
| Trading & End Products | 15,104 | 3,556 | 23.54% | [22.87%, 24.23%] | 43.47% |
| Workforce Services | 281 | 62 | 22.06% | [17.61%, 27.27%] | 28.17% |
| missing | 1,330 | 377 | 28.35% | [25.99%, 30.83%] | 28.54% |

**Month of the clearing**

| stratum | clearings | at least one failed predicate | share | Wilson 95% | share of value |
| --- | ---: | ---: | ---: | --- | ---: |
| 2018-01 | 255 | 9 | 3.53% | [1.87%, 6.57%] | 12.88% |
| 2018-02 | 2,812 | 103 | 3.66% | [3.03%, 4.42%] | 2.75% |
| 2018-03 | 9,790 | 877 | 8.96% | [8.41%, 9.54%] | 8.51% |
| 2018-04 | 15,063 | 1,827 | 12.13% | [11.62%, 12.66%] | 15.54% |
| 2018-05 | 18,939 | 1,972 | 10.41% | [9.99%, 10.86%] | 17.03% |
| 2018-06 | 19,748 | 2,331 | 11.80% | [11.36%, 12.26%] | 15.28% |
| 2018-07 | 20,019 | 2,060 | 10.29% | [9.88%, 10.72%] | 17.38% |
| 2018-08 | 21,610 | 2,531 | 11.71% | [11.29%, 12.15%] | 22.66% |
| 2018-09 | 19,002 | 2,314 | 12.18% | [11.72%, 12.65%] | 27.67% |
| 2018-10 | 19,193 | 2,483 | 12.94% | [12.47%, 13.42%] | 26.87% |
| 2018-11 | 9,103 | 1,241 | 13.63% | [12.94%, 14.35%] | 22.36% |

**Line value quartile**

| stratum | clearings | at least one failed predicate | share | Wilson 95% | share of value |
| --- | ---: | ---: | ---: | --- | ---: |
| Q1 | 38,549 | 2,334 | 6.05% | [5.82%, 6.30%] | 5.60% |
| Q2 | 38,481 | 2,724 | 7.08% | [6.83%, 7.34%] | 7.24% |
| Q3 | 38,963 | 4,522 | 11.61% | [11.29%, 11.93%] | 12.53% |
| Q4 | 39,541 | 8,168 | 20.66% | [20.26%, 21.06%] | 20.07% |

**Vendor activity quartile**

| stratum | clearings | at least one failed predicate | share | Wilson 95% | share of value |
| --- | ---: | ---: | ---: | --- | ---: |
| Q1 | 38,820 | 6,194 | 15.96% | [15.59%, 16.32%] | 19.08% |
| Q2 | 39,580 | 5,391 | 13.62% | [13.29%, 13.96%] | 21.74% |
| Q3 | 42,763 | 3,829 | 8.95% | [8.69%, 9.23%] | 28.48% |
| Q4 | 34,371 | 2,334 | 6.79% | [6.53%, 7.06%] | 7.65% |

---

## Part 2. Claims and statuses (CLAIMS.md)

Source: `CLAIMS.md`, SHA-256 `ba51342733730bbada8fd63679a6b31889cb28e61ecbe5c83d07291b5906eb4e`. Copied verbatim between the rules.

---

# Claims

Status vocabulary: `unregistered` (before the tag `prereg-p7-v1`), `registered`
(after the tag, before a result), then `supported`, `not supported`,
`inconclusive` or `withdrawn`, each with the evidence path. A status changes
only with a slot in `results/` behind it.

| id | claim | type | status | evidence |
|---|---|---|---|---|
| C1 | An invoice clearing can be replayed as a sufficiency-checked contract (paper 5) over evidence reconstructed from the event log at clearing time, every predicate deterministic and metadata-borne. | architecture | supported | `results/e1/exclusions.json`, `results/e1/evidence-set.jsonl.gz`, `results/mutation.json` |
| C2 | Exposure: the share of clearings, and the share of cleared value, that relied on evidence failing at least one predicate, per defect class, item category, spend area and month, with intervals clustered by purchase order. | empirical, registered, descriptive | supported | `results/e1/exposure.json`, `results/e1/exposure-by-stratum.json` |
| C3 | Consequence H1: clearings in a category requiring goods receipt, where the receipt was absent or recorded after clearing, are followed by a corrective event within the registered window at a higher rate than clearings with every predicate passing. | empirical, registered, tested | supported | `results/e2/hypotheses.json` |
| C4 | Consequence H2: clearings where price or quantity changed between approval and clearing are followed by a corrective event at a higher rate than unchanged clearings. | empirical, registered, tested | supported | `results/e2/hypotheses.json` |
| C5 | Authority H3: clearings where the same actor created the line and cleared the invoice are followed by a corrective event at a higher rate than clearings with distinct actors. | empirical, registered, tested | inconclusive: defect class has zero incidence in this log | `results/e1/coverage-check.json`, `results/e2/hypotheses.json` |
| C6 | Agent replay H4: on a registered stratified sample, each model family's hold rate on defective lines is within a registered margin of its hold rate on clean lines (Flat Ladder on live data). Reported beside the human hold rate from the log and the gate's. | empirical, registered, tested | not supported for both families | `results/e4/h4.json` |
| C7 | Gate effect: share of clearings the gate would have held; share of correctives behind a hold; share of holds with no corrective after; euros in each cell. | empirical, registered, descriptive | supported | `results/e3/gate-held.json`, `results/e3/verdict-by-outcome.json`, `results/e3/lag-bands.json` |
| C8 | Exposure of an ungated agent: euros the sample agent would have released on defective evidence and the expected correctives, beside the human and gate columns. | empirical, registered, descriptive | supported | `results/e4/arms.json` |
| C9 | Derivation: paper 5's compiler, given three declared losses (pay for goods not received, pay twice, pay a changed amount), reproduces or does not reproduce the per-category matching rule; and the fewest fields per category a gate must read. | descriptive | not supported: 2-way does not reproduce; 3-way, invoice after receipt does not reproduce; 3-way, invoice before receipt does not reproduce | `results/e5/derivation.json` |
| C10 | Governance cost: wall time and cost per decision of the deterministic gate over the full log, beside cost per decision of each model family in the sample. | descriptive | supported | `results/e6/timing-e1.json`, `results/e6/cost.json` |
| C11 | Replication: H1's shape on BPI 2020 (paid with a missing or wrong-role approval, followed by rejection or resubmission). | empirical, registered, secondary | inconclusive | `results/e7/comparisons.json` |
| C12 | Coverage honesty: defect classes the log cannot expose are declared undetected. | coverage | supported; D5 class zero incidence | `results/e1/coverage-check.json` |
| C13 | Everything reproduces from the committed dataset hash and caches; no number is hand-entered; the replay runs on any XES or CSV event log with the registered column mapping. | reproducibility, deliverable | supported for the internal double runs; external reproduction pending (FINAL-AUDIT item 11) | `results/reproducibility.json`, `results/e4/double-run.json` |

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

## Part 3. Coverage matrix (COVERAGE.md)

Source: `COVERAGE.md`, SHA-256 `801d61ba880ab172a8bc133c0f08fd728a94cb2d6f5f07f05c88236c5ec3b0f3`. Copied verbatim between the rules.

---

# Coverage matrix

Format as dqSarc's coverage matrix (pinned in `engines.lock`): every defect
class the paper speaks about, whether the replay detects it from the log, the
predicate or reason, and the SARC-DQ dimension. "Detected" means a
deterministic predicate over events recorded before the clearing time t_c
(`prereg/p7-v1.md` section 3). "Undetected" means the log does not carry the
evidence; the paper reports nothing about that class.

## Detected (BPI 2019, E1 to E6)

| defect class | predicate | dimension | detected from |
|---|---|---|---|
| goods receipt required but absent at clearing | D1 receipt_present | presence | no `Record Goods Receipt` before t_c, or every one cancelled by a later `Cancel Goods Receipt` before t_c, on a line whose category requires receipt |
| stale receipt: receipt recorded after clearing | D2 receipt_before_clearing | freshness, order | the first uncancelled `Record Goods Receipt` falls after t_c (lag band registered) |
| invoice absent at clearing | D3 invoice_present | presence | no `Record Invoice Receipt` before t_c |
| changed after approval | D4 unchanged_since_approval | validity | `Change Price` or `Change Quantity` between the last approval-bearing event and t_c |
| same actor created and cleared | D5 distinct_actors | authority | actor of `Create Purchase Order Item` equals actor of `Clear Invoice` |
| clearing under an open payment block | D6 block_respected | scope | `Set Payment Block` before t_c with no later `Remove Payment Block` before t_c |
| line deleted or blocked at clearing | D7 not_deleted | validity | `Delete Purchase Order Item` or `Block Purchase Order Item` before t_c with no later `Reactivate Purchase Order Item` before t_c |

## Detected (BPI 2020 declarations, E7, secondary)

| defect class | predicate | dimension | detected from |
|---|---|---|---|
| paid without final approval | D1' approval_present | presence | no final approval event before the payment event |
| approved by a role other than the required one | D2' approval_by_required_role | authority | the approval chain before payment lacks the registered required role |
| declaration changed after approval | D3' unchanged_since_approval | validity | a resubmission by the employee between the last approval and payment |

## Undetected, with reason

| defect class | reason |
|---|---|
| wrong amounts in the payload | values are anonymised by a linear translation; the log carries cumulative net worth per event, not invoice line content, so a mismatch between invoice text and goods is not observable |
| fraud | intent is not an event attribute; no predicate over the log separates a fraudulent clearing from an erroneous one, and the paper makes no statement about it |
| vendor identity (wrong, duplicate or fictitious vendor) | vendor names and ids are anonymised consistently; the log carries no master-data change history or bank details |
| recovery of corrected payments | the log ends at the corrective event; whether money was returned, offset or written off is not recorded |
| what a held line becomes | a gate hold is a replay verdict; the log records the human path only, so the fate of a line the gate would have held is not observable |
| approvals outside the log | approvals given by e-mail, in another system or verbally leave no event; D4's "last approval-bearing event" sees only logged approvals |
| partial receipt and value mismatch per receipt | the replay checks presence and order of the receipt, not the matched values; values are anonymised and the registered mapping reads no per-receipt quantity |
| duplicate invoice across lines | the case is one purchase-order line and the registered mapping carries no invoice document id, so an invoice cleared on two lines is not linked |

Any reclassification after the tag is a deviation (`prereg/DEVIATIONS.md`).

---

## Part 4. Deviations from the registration (prereg/DEVIATIONS.md)

Source: `prereg/DEVIATIONS.md`, SHA-256 `3c29361def6c1f38f9f91689cb01d79947b207b1c67830a35e506e8eb13fb369`. Copied verbatim between the rules.

---

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

---
