# Pre-Release Audit and Editorial Review: `paper-v1.0-candidate-ce73f31.md`

Your manuscript achieves an exceptional standard of empirical transparency, preregistration discipline, and precise boundary-setting around observational claims, placing it at an **Outstanding** proficiency level for a formal process-mining and AI-governance research paper.

---

## 1. Context & Evaluation Rubric

* **Context:** Academic empirical research paper (Computer Science / Process Mining / AI Governance) prepared for arXiv and peer-reviewed publication.
* **Evaluation Rubric (4-Point Scale):**
  1. **Methodological Rigor & Registration Adherence (4/4):** Complete traceability from `prereg-p7-v1` and `prereg-p7-v1.1` through the decision log (`D-C-2`, `D-C-3`) and commit timestamps.
  2. **Arithmetic & Cross-Table Consistency (4/4):** Every count, denominator, stratum total, and Holm-adjusted $p$-value reconciles across the main text and appendices.
  3. **Voice, Clarity & Framing (3.5/4):** Crisp, austere, and well-fenced prose, with minor builder-session artifacts and a subtle denominator transition in Section 7.
  4. **Reproducibility & Release Readiness (3.5/4):** Byte-identical internal double runs and complete slot-based templating, with one external clean-clone audit item marked pending.

---

## 2. Arithmetic & Internal Consistency Verification

All quantitative slots in `paper-v1.0-candidate-ce73f31.md` reconcile across Sections 4–7 and Appendices A–E:

* **Exclusion Funnel (Section 4):** Starting from $251,734$ cases in `BPI_Challenge_2019.xes`, the registered exclusions remove:
  $$0 + 14,498 + 0 + 1,887 + 78 + 376 + 53,731 = 70,570\text{ lines}$$
  leaving exactly $181,164$ framed lines. Removing the $500$ pilot lines (E0) yields $180,664$ analysed framed lines carrying $155,534$ analysed clearings.
* **Category Partition (Sections 5.1, 5.5, and Appendix D):** Analysed clearings across item categories sum to the exact total:
  $$188\text{ (2-way)} + 9,640\text{ (3-way after receipt)} + 145,706\text{ (3-way before receipt)} = 155,534\text{ clearings}$$
  The two three-way categories sum to $9,640 + 145,706 = 155,346$ clearings, matching the reported denominator for predicates D1 and D2 in Section 5.1.
* **Reconciliation Across E1, E2, E3, and Coverage (Sections 5.1–5.3 & 6):**
  * **D1/D2 Failures:** The $610$ absent-receipt clearings (D1 class) and $82$ stale-receipt clearings (D2 class) sum to $692$, matching the H1 defect group denominator ($39\text{ of }692$, or $5.64\%$), the sum of the five lag bands in E3 ($11 + 21 + 11 + 39 + 610 = 692$), and the BPI 2019 coverage table in Section 6.
  * **Corrective Outcomes ($O = 1$ at $W = 60\text{ days}$):** Total corrective events across all $155,534$ clearings sum to $1,659$ in every breakdown:
    * **E2 (H2):** $327\text{ (D4 fail)} + 1,332\text{ (D4 pass)} = 1,659$
    * **E2 (H3 comparison):** $1,659\text{ of }155,534\text{ } (1.07\%)$
    * **E3 (Gate Verdict by Outcome):** $368\text{ (would have held)} + 1,291\text{ (would have allowed)} = 1,659$
* **Human Hold Partition (Section 5.3):** The $180,664$ framed lines partition into:
  $$53,262\text{ (held by people)} + 101,777\text{ (released)} + 25,625\text{ (no invoice receipt by } T_{\text{end}} - W\text{)} = 180,664\text{ lines}$$
  Furthermore, the composition of the $53,262$ human-held lines sums to $10\text{ (payment block alone)} + 53,182\text{ (no clearing within } W\text{ alone)} + 70\text{ (both)} = 53,262$.

---

## 3. Primary Growth Areas & Pre-Release Action Items

* **Growth Area 1: Automated Builder Artifact in the Introduction (Section 1)**
  * **Text Cited:** *"paper 4 (Besanson 2026a) and paper 5 (Besanson 2026b) are on arXiv, and paper 6 is a public repository (Besanson 2026c). We found no record that identifies papers 1 to 3, and do not cite them."*
  * **The Issue:** Because you are the sole author of the entire SARC series, stating that *"We found no record that identifies papers 1 to 3"* reads like an unedited note written by the AI coding agent (Claude) when inspecting the workspace's `engines.lock` or citation files. A human reader or referee will find it jarring for an author to claim they could not locate records of their own earlier papers.
  * **Actionable Next Step:** Replace that sentence with a direct authorial statement explaining why the citation chain starts at Paper 4 (for instance, noting that the public release of the series began with Paper 4, or citing Papers 1–3 directly if they are public working papers).

* **Growth Area 2: Unannotated Denominator Shift Between the Abstract, Section 5.4, and Section 7**
  * **Text Cited:**
    * Abstract & Section 5.4 primary table ($N = 2,000$): *"two model families shown the ERP view held 100.0% and 99.6% of the first and 53.0% and 57.3% of the second"*
    * Section 7: *"the models shown the predicate inputs held nearly every line with a failed predicate (100.0% and 99.6%) and about half of the clean ones (52.5% and 56.0%)"*
  * **The Issue:** In Section 7, `52.5%` ($491 / 936$) and `56.0%` ($524 / 936$) come from the secondary re-tabulation in Section 5.4 restricted to the $1,848$ lines that the human arm can classify (`results/e4/arms-classified-lines.json`), whereas the Abstract cites `53.0%` ($530 / 1,000$) and `57.3%` ($573 / 1,000$) from the full $2,000$-line sample (`results/e4/arms.json`). While using the $1,848$-line subset in Section 7 is logically consistent with the phrase *"on the same lines"*, switching from `53.0% / 57.3%` to `52.5% / 56.0%` without mentioning the $1,848$-line classified subset may look like a typo to a fast reader.
  * **Actionable Next Step:** Clarify in Section 7 whether you want to cite the primary sample numbers alongside the classified-subset numbers, or add a brief parenthetical—such as *"on the 1,848 classified lines"*—so the reader immediately sees why the clean-line percentages differ by $0.5$ and $1.3$ percentage points from the Abstract.

* **Growth Area 3: Pending External Reproduction Gate in Appendices B and C**
  * **Text Cited:**
    * Appendix B (Claim C13): *"supported for the internal double runs; external reproduction pending (FINAL-AUDIT item 11)"*
    * Appendix C: *"The internal double runs were byte-identical (16 files for E1 to E3); external reproduction from a clean clone is pending."*
  * **The Issue:** Leaving *"FINAL-AUDIT item 11"* and *"external reproduction from a clean clone is pending"* in a public `v1.0` release signals an incomplete pre-release checklist.
  * **Actionable Next Step:** Will you execute the clean-clone reproduction run and update the slot file before tagging `v1.0`, or if you intend to publish the preprint prior to external verification, would you consider removing the internal checklist label `(FINAL-AUDIT item 11)` so the text stands cleanly on its own?

* **Growth Area 4: Self-Reported Model Strings in the Acknowledgements**
  * **Text Cited:** *"for the second, the platform made two statements, in this order: a later session reported its own model as `Claude Opus 5.5` and stated that it produced the sweep, and the same session then identified the sweep's model as `DeepSeek V4 Pro`"*
  * **The Issue:** Wrapper platforms frequently hallucinate non-existent version numbers (such as `Claude Opus 5.5` or `DeepSeek V4 Pro`) when queried in-chat about their underlying model identity. Your current phrasing already distances yourself by writing *"the platform made two statements"*, which is good practice.
  * **Actionable Next Step:** Consider whether adding the word *"in-chat"* or *"unverified"* would make it even clearer to readers that these strings are raw conversational self-reports from the wrapper interface rather than API model identifiers.

---

## 4. Minimal Wording Examples (Preserving Your Voice and Slot Structure)

If you decide to address Growth Areas 1 and 2 in `paper/template.md`, the following minimal edits preserve your exact tone and slot architecture:

* **Section 1 (Paragraph 1):**
  > **Current:** `We found no record that identifies papers 1 to 3, and do not cite them. This paper is the number, on one real process.`
  >
  > **Option (if Papers 1–3 were unreleased/superseded):** `Papers 1 to 3 of the programme were not published separately and are not cited. This paper is the number, on one real process.`

* **Section 7 (Sentence 6):**
  > **Current:** `The only inference the three columns support is this: on the same lines the process released about two thirds of both sets within W (people held 33.0% and 34.0%); the models shown the predicate inputs held nearly every line with a failed predicate (100.0% and 99.6%) and about half of the clean ones (52.5% and 56.0%); the gate held exactly the lines with a failed predicate.`
  >
  > **Option (clarifying the denominator):** `The only inference the three columns support is this: on the 1,848 sample lines the log classifies, the process released about two thirds of both sets within W (people held 33.0% and 34.0%); the models shown the predicate inputs held nearly every line with a failed predicate (100.0% and 99.6%) and about half of the clean ones (52.5% and 56.0%; 53.0% and 57.3% on all 2,000 sample lines); the gate held exactly the lines with a failed predicate.`