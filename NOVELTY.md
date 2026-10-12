# Novelty: prior-art fence

Written before the preregistration (brief section 4). An external reviewer runs
this fence before the registration is public (Phase A1); the review is
committed unedited to `review-secondary/` and adjudicated in `DECISIONS.md`.
Every source below is to be fetch-verified into `verified-citations.json` in
A1, as in paper 5. Sources marked *(link checked 2026-10-12)* were reached over
HTTPS during A0; the others are cited from the standard literature and are
not yet verified.

## Not claimed as new

**Conformance and compliance checking in process mining.** Checking recorded
behaviour against a normative model or rule set is established: van der Aalst,
*Process Mining: Data Science in Action* (Springer, 2nd ed., 2016); Ly, Maggi,
Montali, Rinderle-Ma and van der Aalst, "Compliance monitoring in business
processes: functionalities, application, and tool-support", *Information
Systems* 54 (2015); declarative constraints in the Declare family (Pesic,
Schonenberg and van der Aalst, "DECLARE: full support for loosely-structured
processes", EDOC 2007). Our predicates D1 to D7 are compliance rules in this
sense.

**Four-eyes and segregation-of-duties detection in event logs.** Detecting
that the same resource performed two activities that must be separated is a
standard conformance check. D5 is that check.

**The BPI Challenge 2019 reports.** The challenge posed the process owner's
compliance questions, including clearing before goods receipt and the
three-way match per item category, and the submitted reports measured basic
violation rates on this very log. They are prior art for every basic rate this
paper reports. Reports listed on the challenge page *(link checked 2026-10-12:
https://icpmconference.org/2019/bpi-challenge/)*, among them:

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
- The remaining student and non-student submissions on the same page.

**The BPI Challenge 2020 reports.** The 2020 challenge posed questions on the
travel-declaration approval chain, including approvals by role and rejection
and resubmission. The reports are prior art for the basic rates in E7.
Challenge page *(link checked 2026-10-12:
https://icpmconference.org/2020/bpi-challenge/)*; the page does not list the
reports, so the individual reports are to be located and cited in A1.

**Three-way match as an audit control.** Matching purchase order, goods receipt
and invoice before payment is a textbook internal control. The paper does not
propose it; E5 asks whether paper 5's compiler re-derives it from declared
losses.

**Deviation-to-outcome studies in process mining.** Relating a deviation to a
later outcome in the same case is established. H1 to H3 are studies of this
shape.

**Revert and rework analysis.** Corrective events (cancellations, changes,
deletions, debit memos, subsequent invoices) as rework signals are
established. The outcome proxy O is a rework signal.

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
