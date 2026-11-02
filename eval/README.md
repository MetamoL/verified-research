# Evaluation (2026-11-02)

30 questions in [questions.txt](questions.txt): 15 English, 15 Japanese, covering software releases, law, health, science, government statistics, prices, and games. Every footnote quote was checked with `verify_quotes.py` after the run.

| Condition | Quotes | Verified | Not on page | Unfetchable |
|---|---:|---:|---:|---:|
| Claude Code, no skill, asked for verbatim quotes | 87 | 82 (94%) | 0 | 5 (6%) |
| Codex (GPT), no skill, asked for verbatim quotes | 64 | 53 (83%) | 1 | 10 (16%) |
| Claude Code with verified-research | 136 | 134 (99%) | 1 | 1 |

What this shows:

- **Fabricated quotes are rare** once a model is asked for verbatim quotes. The one mismatch per condition was a dropped footnote marker and a stray ruby character on the page, not an invented sentence.
- **Unverifiable citations are not rare.** Without the skill, 6% (Claude) and 16% (Codex) of citations point to pages no script can open (bot-blocked PubMed and JAMA pages, rate-limited news sites). The skill drives this to near zero by making the agent find a checkable copy or move the claim to Unverified.
- **The cold read changes conclusions.** It ran on 8 of 30 questions (judgments and conflicting sources) and led to edits on 6: on sleep and mortality in Japanese cohorts, the no-skill answer said "U-shaped"; the cold read found that short sleep showed no risk after adjustment in one large cohort, and the answer was rewritten. Others removed a claim its quote did not support or softened a date the source did not state.
- **Quotes that do not carry their claim drop.** All 287 claim–quote pairs were shuffled, stripped of their condition, and judged by Codex (GPT) on one question: does the quote alone support the sentence that cites it? A quote that does not support its claim at all fell from 7% (Claude, no skill) and 16% (Codex, no skill) to 2% with the skill. Sampled verdicts held up: the failures were real, such as a quote about long sleep cited for a claim that short sleep also raises mortality. The judge was strict, so most of the rest landed in "partly supported" in every condition (69%, 53%, 65%), mostly for context the quote leaves implicit; fully supported rose from 24% to 32%.

  | Condition | Supported | Partly | Not supported |
  |---|---:|---:|---:|
  | Claude Code, no skill | 21 (24%) | 60 (69%) | 6 (7%) |
  | Codex, no skill | 20 (31%) | 34 (53%) | 10 (16%) |
  | Claude Code with verified-research | 44 (32%) | 89 (65%) | 3 (2%) |

- **Cost:** about 1.6× the tokens (not counting the cold-read subagents) and 3× the wall time of the no-skill run.

Not measured: overall answer correctness against a key. The first round (5 questions with a key, earlier the same day) found every condition correct, so a harder keyed set is the next step.
