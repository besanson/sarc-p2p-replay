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

Porter et al. report compliance per item category both by number and by EUR
value (Table 3, p. 8; for 3-way after receipt, 80.5% by number and 80.2% by EUR
value; `bpi2019-nonstudent-8-porter`), and Diba et al. quantify
receipt-before-clearing violations with their value (Table 2, p. 15: rule
"Record Goods Receipt -> Clear Invoice", 31 violations, 5.80% of traces;
section 4.1: average amount 130,322.85 EUR; `bpi2019-nonstudent-6-diba`). Both
passages verified 2026-10-14.

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
later outcome in the same case is established. H1 to H3 are studies of this
shape. (No source cited yet.)

**Revert and rework analysis.** Corrective events (cancellations, changes,
deletions, debit memos, subsequent invoices) as rework signals are
established. The outcome proxy O is a rework signal. On this log, Meyer zu
Wickern et al. count rework activities as those that "generally include
'change,' 'cancel,' or 'delete' keywords in their activity names" (section 5.1,
p. 17; `bpi2019-student-4-meyerzuwickern`), and Badakhshan et al. list "Vendor
Creates Debit Memo" among rework activities (Table 5, p. 22: 4,680 cases, 4,801
occurrences; `bpi2019-nonstudent-4-badakhshan`). Both quotes verified
2026-10-14; neither covers every activity in the registered outcome list.

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
