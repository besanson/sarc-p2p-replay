# Coverage matrix

Format as dqSarc's coverage matrix (pinned in `engines.lock`): every defect
class the paper speaks about, whether the replay detects it from the log, the
predicate or reason, and the SARC-DQ dimension. "Detected" means a
deterministic predicate over events recorded before the clearing time t_c
(`prereg/p7-v1.md` section 3). The split of a D1/D2 failure into absent and
stale receipt uses events after t_c and is for reporting only (section 3.3); it
never enters the gate. "Undetected" means the log does not carry the
evidence; the paper reports nothing about that class.

## Detected (BPI 2019, E1 to E6)

| defect class | predicate | dimension | detected from |
|---|---|---|---|
| goods receipt required but absent at clearing | D1 receipt_present | presence | no `Record Goods Receipt` before t_c, or every one cancelled by a later `Cancel Goods Receipt` before t_c, on a line whose category requires receipt |
| stale receipt: receipt recorded after clearing | D2 receipt_before_clearing | freshness, order | the first uncancelled `Record Goods Receipt` falls after t_c (lag band registered) |
| invoice absent at clearing | D3 invoice_present | presence | no `Record Invoice Receipt` before t_c |
| changed after approval | D4 unchanged_since_approval | validity | `Change Price` or `Change Quantity` between the last approval-bearing event and t_c |
| same actor created and cleared | D5 distinct_actors | authority | actor of `Create Purchase Order Item` equals actor of `Clear Invoice` |
| clearing under an open payment block | D6 block_respected | scope | count of `Set Payment Block` minus count of `Remove Payment Block` before t_c greater than zero |
| line deleted or blocked at clearing | D7 not_deleted | validity | count of `Delete Purchase Order Item` plus `Block Purchase Order Item` minus `Reactivate Purchase Order Item` before t_c greater than zero |

## Detected (BPI 2020 declarations, E7, secondary)

| defect class | predicate | dimension | detected from |
|---|---|---|---|
| paid without final approval | D1' approval_present | presence | no event in the registered approval list before the payment |
| approved by a role other than the required one | D2' approval_by_required_role | authority | the approval chain before payment lacks the registered required role |
| declaration changed after approval | D3' unchanged_since_approval | validity | a resubmission by the employee between the last approval and payment |

## Undetected, with reason

| defect class | reason |
|---|---|
| wrong amounts in the payload | values are anonymised by a linear translation; the log carries cumulative net worth per event, not invoice line content, so a mismatch between invoice text and goods is not observable |
| fraud | intent is not an event attribute; no predicate over the log separates a fraudulent clearing from an erroneous one, and the paper makes no statement about it |
| vendor identity (wrong, duplicate or fictitious vendor) | vendor names and ids are anonymised consistently; the log carries no master-data change history or bank details |
| recovery of corrected payments | the log records the corrective event and nothing about recovery; whether money was returned, offset or written off is not recorded |
| what a held line becomes | a gate hold is a replay verdict; the log records the human path only, so the fate of a line the gate would have held is not observable |
| approvals outside the log | approvals given by e-mail, in another system or verbally leave no event; D4's "last approval-bearing event" sees only logged approvals |
| partial receipt and value mismatch per receipt | the replay checks presence and order of the receipt, not the matched values; values are anonymised and the registered mapping reads no per-receipt quantity |
| duplicate invoice across lines | the case is one purchase-order line and the registered mapping carries no invoice document id, so an invoice cleared on two lines is not linked |

Any reclassification after the tag is a deviation (`prereg/DEVIATIONS.md`).
