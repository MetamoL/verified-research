# verified-research

An agent skill for Claude Code, Codex, and other agents that read `SKILL.md`, for web research you can audit. Every claim in the answer carries a footnote with a sentence copied verbatim from the source, and a script fetches each page and checks that the sentence is really there. Answers that rest on a judgment or on conflicting sources get a second, cold read by a fresh subagent.

It leaves *how* to search to the model. It only governs what reaches you: checkable sources, primary sources over repetition, and an explicit **Unverified** section for whatever could not be checked.

```
[^1]: https://developers.google.com/custom-search/v1/overview "Existing Custom Search JSON API customers have until January 1, 2027 to transition to an alternative solution."
```

## Example

From the [evaluation](eval/), asked in Japanese: *What do large Japanese cohort studies show about sleep duration and mortality?* (translated, trimmed)

| Without the skill | With the skill |
|---|---|
| The JACC study found a **U-shaped** relationship: mortality was lowest at 7 hours, and both short (≤4 h) and long (≥10 h) sleep raised it. | Mortality is lowest around 7 hours, and **long sleep is consistently linked to higher risk**. **Short sleep is not**: JACC found a U-shape, but in the JPHC cohort short sleep showed no higher risk after adjustment. A pooled Asian analysis found a J-shape, weighted to long sleep. |
| Sources: a health foundation's summary page, a Spanish news summary | Sources: the JACC and JPHC papers and the pooled analysis, each quote checked against the page; an Unverified section lists what was not checked |

The cold read found the cohort that disagreed and rewrote the conclusion.

## Why

In a 100-question test with Claude Code and Codex ([eval](eval/)), models asked for verbatim quotes rarely invented one. The bigger gap: without the skill, 11–16% of citations pointed to pages nothing could open, so no one could check them; with it, almost none. For Codex, the skill also cut quotes that do not support their claim by about a third (judged blind by two models); Claude Code was already good at that. Judgment questions get a cold read that rewrote several conclusions. The trade is speed: about 2–2.5× the time.

## Install

**Claude Code**

```
/plugin marketplace add MetamoL/skills
/plugin install verified-research@metamol
```

**Codex and other agents**

```
npx skills add MetamoL/verified-research
```

It asks which agents to install for. Add `-g` to make it available in every project.

**By hand:** clone this repository into your agent's skills folder (`~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex).

```
git clone https://github.com/MetamoL/verified-research ~/.claude/skills/verified-research
```

Needs Python 3. Optional, installed when the script asks:

- `pip install pdfminer.six` for PDF sources
- `pip install playwright && playwright install chromium` for pages rendered by JavaScript

Sites that refuse automated readers are respected, not bypassed: the agent is told to cite a machine-readable copy (official API, DOI page, archive) or list the claim as unverified.

## 日本語

Web 調査の答えのすべての主張に、原文どおりの引用つきの出典を付けさせる AI エージェント用のスキルです。Claude Code・Codex など、`SKILL.md` を読むエージェントで使えます。引用がページに本当に載っているかをスクリプトで照合し、判断が絡むときは別のエージェントに読み直させます。検索の仕方はモデルに任せます。Claude Code と Codex で行った100問の評価結果は [eval](eval/)。導入は上の Install のとおりです。ほかのスキルは [MetamoL/skills](https://github.com/MetamoL/skills) にまとめています。

## License

[LICENSE](LICENSE)（日本語・英語）。自分の環境で使うこと・改変することは自由です。再配布と転載はできません。 Free to use and modify in your own setup, personal or business; redistribution is not permitted.
