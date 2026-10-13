# Novelty: prior-art fence

Written before the preregistration (brief section 4). An external reviewer runs
this fence before the registration is public (Phase A1); the review is
committed unedited to `review-secondary/` and adjudicated in `DECISIONS.md`.
Every source below was fetched on 2026-10-13 (A1 preparation) and recorded in
`verified-citations.json`, as in paper 5; each citation carries its status and
record id. Paragraphs with no source name none yet; the A1 reviewer may supply
one.

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

**Four-eyes and segregation-of-duties detection in event logs.** Detecting
that the same resource performed two activities that must be separated is a
standard conformance check. D5 is that check. (No source cited yet.)

**The BPI Challenge 2019 reports.** The challenge posed the process owner's
compliance questions, including clearing before goods receipt and the
three-way match per item category, and the submitted reports measured basic
violation rates on this very log. They are prior art for every basic rate this
paper reports. Reports listed on the challenge page
(https://icpmconference.org/2019/bpi-challenge/; verified,
`icpm-bpi-challenge-2019-page`), among them (titles and author lists as the
page states them, each PDF link reached; report contents not read in A1
preparation):

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

**The BPI Challenge 2020 reports.** The 2020 challenge posed questions on the
travel-declaration approval chain, including approvals by role and rejection
and resubmission. The reports are prior art for the basic rates in E7.
Challenge page (https://icpmconference.org/2020/bpi-challenge/; verified,
`icpm-bpi-challenge-2020-page`); it lists no reports, winners or proceedings.
The ICPM 2020 awards page (https://icpmconference.org/2020/awards/; verified,
`icpm-2020-awards-page`) names two BPI Challenge reports given awards at
ICPM 2020:

- Hobeck, Pufahl, Binetruy, Chada, Digtiar, Gülle, Slarzynska, Stiehle and
  Weber, "Performance, Variant, and Conformance Analysis of an Academic Travel
  Reimbursement Process" (BPI Challenge Award; `bpi2020-award-hobeck`).
- Kas, Post and Wiewel, "Automated Machine Learning in a Process Mining
  Context" (BPI Student Challenge Award; `bpi2020-student-award-kas`).

No link to either report's text was found, and no list of the other submitted
reports was found (`bpi2020-report-list`, status "not found").

**Three-way match as an audit control.** Matching purchase order, goods receipt
and invoice before payment is a textbook internal control. The paper does not
propose it; E5 asks whether paper 5's compiler re-derives it from declared
losses. (No source cited yet.)

**Deviation-to-outcome studies in process mining.** Relating a deviation to a
later outcome in the same case is established. H1 to H3 are studies of this
shape. (No source cited yet.)

**Revert and rework analysis.** Corrective events (cancellations, changes,
deletions, debit memos, subsequent invoices) as rework signals are
established. The outcome proxy O is a rework signal. (No source cited yet.)

## Claimed

The unit and the comparison:

1. Per action, a min() contract over sufficiency-checked, metadata-borne
   predicates (paper 5), evaluated on the evidence reconstructed at clearing
   time.
2. Exposure in count and in value per Silent Evidence Defect class.
3. Consequence conditional on the defect, with the registered window W and lag
   bands.
4. The same evidence decided by humans (read from the log), by two model
   families (replayed on the registered ERP view) and by the gate, side by side
   on the same lines.
5. The control derived from declared losses with paper 5's compiler, not
   assumed, with the fewest fields per category a gate must read.
6. A coverage matrix for what the log cannot show (`COVERAGE.md`).

Sentence for the related-work section:

> This paper does not introduce conformance checking, the three-way match or
> rework analysis. It replays each clearing as a gate decision over the
> evidence it relied on, measures how often that evidence was defective and
> what followed, and puts people, models and the gate on the same lines.

## Fence status

| item | status |
|---|---|
| external fence review (A1) | open |
| citations fetch-verified | open |
| BPI 2020 reports located and cited | open |
