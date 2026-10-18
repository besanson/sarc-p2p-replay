Fence Review: SARC paper 7

Paper (working title): Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process. Author: Gaston Besanson. Registration: p7-v1.
Packet reviewed: review-secondary/A1-fence-packet.md at commit fc6447e (2026-10-14). Review date: 2026-10-16.

Note on method: the literature checks below were run with AI assistance; the verdicts are my own. I am external to SARC papers 1-6.

Verdicts

Item 1 (min() contract over sufficiency-checked, metadata-borne predicates, evaluated on evidence reconstructed at clearing time): (c) not found. The pieces are precedented, the combination is not. Conjunction of constraints is DECLARE (Pesic, Schonenberg & van der Aalst 2007, listed); minimum-cardinality sufficient contracts from declared losses are paper 5 of this programme (Besanson 2026, arXiv:2609.26016). I found no prior art for that contract run as a per-clearing gate verdict at t_c over a reconstructed evidence set with pass/fail/unknown. (The D1-D7 predicates themselves are compliance rules; the fence already concedes that.)

Item 2 (exposure in count and in value per Silent Evidence Defect class): (a) in the listed prior art. Porter et al. (2019), BPI Challenge 2019 report, Table 3, gives compliance per category by number and by EUR value (3-way after receipt: 80.5% by number, 80.2% by EUR value). The SED taxonomy is the paper's own; the count-and-value measure is not new.

Item 3 (consequence conditional on the defect, registered window W, lag bands): (c) not found as a design. Deviation-to-outcome is established (source below). Porter et al. note late "Cancel Invoice Receipt" events long after a compliant "Clear Invoice" cycle, but that is a case-study observation, not a registered conditional-consequence study. The W=60/30 window plus lag bands: not found.

Item 4 (humans, two model families, and the gate side by side on the same lines): (c) not found. I do not accept the sweep's Gutermuth candidate: distinguishing normal from anomalous cases is not a three-way decision comparison on the same instances. I found no prior art that puts human decisions from the log, replayed model families and a deterministic gate on the same lines under one evidence frame.

Item 5 (control derived from declared losses with paper 5's compiler, fewest fields per category): (c) not found as an empirical result. The compiler is paper 5's (own programme; demonstrated on constructed domains, not this log). The three-way match itself is textbook (PCAOB 2004-001, conceded). The run, asking whether the compiler re-derives the per-category rule from the three declared losses on this log: not found.

Item 6 (coverage matrix for what the log cannot show): (c) not found as an artifact. (b) Outmazgin & Soffer (2013), LNBIP 147, pp. 48-62, doi:10.1007/978-3-642-38484-4_5: two workaround types not reflected in event logs and undetectable by process mining. That is the concept precedent; the registered per-class matrix is new. (Not listed in the fence; the sweep found it.)

Related-work sentence

The three disclaimers hold. The affirmative clause does not hold as written. "The evidence it relied on" should be "the evidence reconstructed from the event log at clearing time": the packet's own section 3.9 defines a reconstructed evidence set with unknown for missing inputs, and the coverage matrix declares what the log cannot show, so the gate does not see what the human saw. I endorse the sweep's rewording.

Missing source

Deviation-to-outcome paragraph: Peleg, Soffer & Ghattas (2008), "Mining Process Execution and Outcomes – Position Paper", BPM 2007 Workshops, LNCS 4928, Springer, doi:10.1007/978-3-540-78238-4_40. (The sweep named it but could not check the quote; I checked it.)

On the sweep

Agreed: no antecedent for any of the six as complete combinations; the rows are component precedents. Two corrections: Gutermuth does not support item 4 even as a component; Porter Table 3 for item 2 is a direct precedent, not a mere component.

Attribution

Eduardo Arana, independent researcher. I had no role in developing the repository.
