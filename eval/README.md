# Evaluation (2026-11-02)

100 questions in [questions.txt](questions.txt): 50 English, 50 Japanese. The first 30 are mostly facts (software releases, law, statistics, prices, games); the other 70 lean on judgment and contested evidence (diet, health, hardware, policy, "is it true that…"). Four conditions: Claude Code and Codex (GPT), each with and without the skill. Without the skill, the agent was still asked to footnote every claim with a verbatim quote, so the baseline is a careful one.

## Checkable sources

Every footnote quote was fetched and checked with `verify_quotes.py`.

| Condition | Quotes | Verified | Not on page | Unfetchable |
|---|---:|---:|---:|---:|
| Claude Code, no skill | 466 | 412 (88%) | 4 | 50 (11%) |
| Claude Code, skill | 777 | 776 (99.9%) | 1 | 0 |
| Codex, no skill | 322 | 257 (80%) | 13 (4%) | 52 (16%) |
| Codex, skill | 338 | 337 (99.7%) | 0 | 1 |

Without the skill, 11–16% of citations pointed to pages no script could open (bot-blocked journals and agencies, rate-limited sites); with it, almost none. "Not on page" is an upper bound for paraphrased quotes: some of the 13 are pages the checker reads imperfectly (math markup, PDF layout).

## Do the quotes support the claims?

All 1,903 claim–quote pairs were shuffled, stripped of their condition, and judged twice, by Codex and by Claude, on one question: does the quote alone support the sentence that cites it? The two judges agreed on 84% of items.

| Condition | Fully supported (Codex judge / Claude judge) | Not supported (Codex / Claude) | Not supported by both |
|---|---:|---:|---:|
| Claude Code, no skill | 40% / 52% | 3.4% / 2.6% | 2.4% |
| Claude Code, skill | 42% / 56% | 2.2% / 2.2% | 1.8% |
| Codex, no skill | 23% / 30% | 8.1% / 11.2% | 7.1% |
| Codex, skill | 31% / 41% | 5.3% / 7.4% | 4.4% |

- For **Codex**, the skill cut unsupported quotes by about a third and raised fully supported ones by 8–11 points.
- For **Claude Code**, the difference is small: asked for verbatim quotes, it already fetched pages and quoted them well. Most of its gain is in checkable sources, not in quote fit.
- An earlier 30-question round showed a larger drop for Claude (7% → 2%, one judge); the 100-question run did not reproduce it.
- Both judges were strict, so most of the rest is "partly supported" in every condition, largely for names or years the quote leaves implicit.

## Conclusions changed by the cold read

The cold read ran on the judgment questions and rewrote several conclusions, for example: sleep and mortality in Japanese cohorts ("U-shaped" → short sleep showed no risk after adjustment in one large cohort), and whether AI-written code has more vulnerabilities ("mostly yes" → "not established, studies disagree"). These are not scored above.

## Cost

| | Time per question | Tokens |
|---|---:|---:|
| Claude Code | about 2.5× the no-skill run | about 1.6× (not counting cold-read subagents) |
| Codex | 286 s vs 132 s (2.2×) | not measured |

## Limits

- One run per condition; agents in the same run shared a web-search quota that ran out partway, which pushed some answers onto known URLs and official APIs.
- The judges see only the claim and the quote, not the page, so "partly supported" includes context the page gives but the quote does not.
- Overall answer correctness against a key was not scored.
