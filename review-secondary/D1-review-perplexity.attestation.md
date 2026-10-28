# Attestation: D1 round-1 review, machine (Perplexity Computer)

Machine review, AI support, not the external review.

| field | value |
|---|---|
| platform | Perplexity Computer, web access on |
| model, as the model states it | "Claude Opus 5.5 (Anthropic), as the host platform (Perplexity Computer) names it; it exposes no finer version string"; closing line "Model: Claude Opus 5.5" |
| model, as the author's app shows it | the author had selected DeepSeek on the platform; the model's own statement is recorded above and governs this attestation |
| conflict stated by the model | "the Haiku arm and the paper's builder sessions are both Claude-family models, and this session produced the A1 fence review on 2026-10-14" (the 2026-10-14 output is the second A1 machine sweep, `A1-fence-sweep-deepseek.md`, whose attestation names the model the author selected; see `DECISIONS.md` D-D-2 for the correction) |
| run by | the author, 2026-10-26 to 2026-10-28, on the packet at commit `76264dd` |
| prompt | the round-1 machine review prompt (as for the ChatGPT review) |
| join | the first reply was cut off on copy inside the first bullet of the Abstract check; a follow-up in the same session asked for the rest from that bullet onward, unchanged. The file is the first reply up to the line before that bullet, then the second reply from that bullet (complete) to its end. Nothing else was changed |
| file | `review-secondary/D1-review-perplexity.md` |
| SHA-256 | `8824527fa2b23c5d1214fc69711ef71b61cea83da9acc58fb01e705c2319c75f` |

Committed unedited apart from the join described above, by the builder on 2026-10-28. This review is AI support, to be disclosed in the acknowledgements; it is adjudicated in `DECISIONS.md` D-D-2 together with the external review.
