<!-- paper/readme-headline.md: the source of the README's headline block. scripts/fill_paper.py fills it
from the slots, as the paper, and writes it into README.md between the headline markers. -->
## Headline

Every number below comes from a slot file under `results/`, filled by `scripts/fill_paper.py` as the paper is.

**Exposure (E1).** Of the {{e1/exposure.json>analysed_clearings|int}} analysed invoice clearings of the BPI Challenge
2019 log, the share made on evidence that failed each registered predicate, in count and in cleared value (anonymised EUR),
with 95% intervals (Wilson; purchase-document-clustered bootstrap); source `results/e1/exposure.json`:

{{#exposure}}

**Gate column (E3).** The gate would have held {{e3/gate-held.json>held>clearings|int}} analysed clearings:
{{e3/gate-held.json>held>share_of_clearings|pct}} of clearings ({{e3/gate-held.json>held>bootstrap95|ivpct}}) and
{{e3/gate-held.json>held>share_of_value|pct}} of cleared value ({{e3/gate-held.json>held>value_bootstrap95|ivpct}});
source `results/e3/gate-held.json`.

**Hold rates on the same registered sample (E4).** Source `results/e4/arms.json`:

| arm | hold rate, lines with a failed predicate | hold rate, clean lines |
|---|---:|---:|
| people (from the log) | {{e4/arms.json>arms>people>hold_rate_defective|pct1}} | {{e4/arms.json>arms>people>hold_rate_clean|pct1}} |
| Jev (ERP view) | {{e4/arms.json>arms>jev>hold_rate_defective|pct1}} | {{e4/arms.json>arms>jev>hold_rate_clean|pct1}} |
| Haiku (ERP view) | {{e4/arms.json>arms>haiku>hold_rate_defective|pct1}} | {{e4/arms.json>arms>haiku>hold_rate_clean|pct1}} |
| gate | {{e4/arms.json>arms>gate>hold_rate_defective|pct1}} | {{e4/arms.json>arms>gate>hold_rate_clean|pct1}} |

For people, on the sample lines the log lets us classify, a hold is a recorded payment block or, in nearly every case, an
inferred non-release within 60 days, not a recorded decision. No causal claim is made; see the non-claims in `CLAIMS.md`.
