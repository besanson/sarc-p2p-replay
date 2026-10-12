# Claims

Status vocabulary: `unregistered` (before the tag `prereg-p7-v1`), `registered`
(after the tag, before a result), then `supported`, `not supported`,
`inconclusive` or `withdrawn`, each with the evidence path. A status changes
only with a slot in `results/` behind it.

| id | claim | type | status |
|---|---|---|---|
| C1 | An invoice clearing can be replayed as a sufficiency-checked contract (paper 5) over evidence reconstructed from the event log at clearing time, every predicate deterministic and metadata-borne. | architecture | unregistered |
| C2 | Exposure: the share of clearings, and the share of cleared value, that relied on evidence failing at least one predicate, per defect class, item category, spend area and month, with intervals clustered by purchase order. | empirical, registered, descriptive | unregistered |
| C3 | Consequence H1: clearings in a category requiring goods receipt, where the receipt was absent or recorded after clearing, are followed by a corrective event within the registered window at a higher rate than clearings with every predicate passing. | empirical, registered, tested | unregistered |
| C4 | Consequence H2: clearings where price or quantity changed between approval and clearing are followed by a corrective event at a higher rate than unchanged clearings. | empirical, registered, tested | unregistered |
| C5 | Authority H3: clearings where the same actor created the line and cleared the invoice are followed by a corrective event at a higher rate than clearings with distinct actors. | empirical, registered, tested | unregistered |
| C6 | Agent replay H4: on a registered stratified sample, each model family's hold rate on defective lines is within a registered margin of its hold rate on clean lines (Flat Ladder on live data). Reported beside the human hold rate from the log and the gate's. | empirical, registered, tested | unregistered |
| C7 | Gate effect: share of clearings the gate would have held; share of correctives behind a hold; share of holds with no corrective after; euros in each cell. | empirical, registered, descriptive | unregistered |
| C8 | Exposure of an ungated agent: euros the sample agent would have released on defective evidence and the expected correctives, beside the human and gate columns. | empirical, registered, descriptive | unregistered |
| C9 | Derivation: paper 5's compiler, given three declared losses (pay for goods not received, pay twice, pay a changed amount), reproduces or does not reproduce the per-category matching rule; and the fewest fields per category a gate must read. | descriptive | unregistered |
| C10 | Governance cost: wall time and cost per decision of the deterministic gate over the full log, beside cost per decision of each model family in the sample. | descriptive | unregistered |
| C11 | Replication: H1's shape on BPI 2020 (paid with a missing or wrong-role approval, followed by rejection or resubmission). | empirical, registered, secondary | unregistered |
| C12 | Coverage honesty: defect classes the log cannot expose are declared undetected. | coverage | unregistered |
| C13 | Everything reproduces from the committed dataset hash and caches; no number is hand-entered; the replay runs on any XES or CSV event log with the registered column mapping. | reproducibility, deliverable | unregistered |

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
