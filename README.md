# verified-research

A Claude Code skill (also usable from Codex and other agents that read `SKILL.md`) for web research you can audit. Every claim in the answer carries a footnote with a sentence copied verbatim from the source, and a script fetches each page and checks that the sentence is really there. Answers that rest on a judgment or on conflicting sources get a second, cold read by a fresh subagent.

It leaves *how* to search to the model. It only governs what reaches you: checkable sources, primary sources over repetition, and an explicit **Unverified** section for whatever could not be checked.

```
[^1]: https://developers.google.com/custom-search/v1/overview "Existing Custom Search JSON API customers have until January 1, 2027 to transition to an alternative solution."
```

## Why

In a 30-question test ([eval](eval/)), models asked for verbatim quotes almost never invented one. The real gaps were elsewhere: 6–16% of citations pointed to pages nothing could open, and quotes that were real but did not carry the claim attached to them. The script closes the first; the cold read caught the second and rewrote 6 of the 8 answers it reviewed. The trade is speed: about 3× the time.

## Install

Copy this folder to `~/.claude/skills/verified-research/`, or install the plugin from the repository root. Needs Python 3. Optional, installed when the script asks:

- `pip install pdfminer.six` for PDF sources
- `pip install playwright && playwright install chromium` for pages rendered by JavaScript

Sites that refuse automated readers are respected, not bypassed: the agent is told to cite a machine-readable copy (official API, DOI page, archive) or list the claim as unverified.
