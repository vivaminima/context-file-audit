# context-file-audit

*Part of the [Vivaminima tools](https://github.com/vivaminima) for Claude Code users.*

<img src="https://raw.githubusercontent.com/vivaminima/vivaminima/main/img/run/context-file-audit.png" width="760" alt="context-file-audit: real output of the free version on a made-up sample">

**Install in Claude Code:** `/plugin install context-file-audit --marketplace vivaminima/vivaminima`

Audits the `CLAUDE.md` files that Claude Code reads at session start.

Find out how much context your `CLAUDE.md` takes up at session start, including everything it pulls in with `@import`.

```
python claude_md_audit.py ~/code
```

```
project      at start  CLAUDE.md  imported  verdict
-------------------------------------------------------
content-a      48,062      1,246    46,816  LEAKING
design         19,413         24    19,389  heavy
hq             12,040          6    12,034  normal
-------------------------------------------------------
ALL           139,325
```

A line like `@house-rules.md` is not a link. It is an inline import: the whole file is loaded when the session starts. In the project above, one import came to 46,816 estimated tokens.

## Usage

```
python claude_md_audit.py [folder]              # every project under folder
python claude_md_audit.py --sections <project>  # one project, largest sections first
python claude_md_audit.py --help
```

- Python 3.8+, standard library only
- No network calls, writes nothing
- Verdicts: light <= 5,000 · normal <= 15,000 · heavy <= 25,000 · LEAKING above

## Notes

- Token counts are estimates (a conservative mixed-script approximation, not a model tokenizer). Good enough to tell 3,000 from 47,000.
- Context loads at session start and prompt caching applies, so this measures working room, not a per-turn bill. Confirm real spend with your client's own cost/context commands.

## The full kit

Measuring is the easy part. Deciding which sections can move without the agent forgetting the rules that stopped past mistakes is the hard part. The Token Audit Kit ($19) adds the split guide, a real 13-project case study (46,816 → 23,066, all 40 sections kept) and a monthly checklist. Get it here: https://vivastory4.gumroad.com

## More from Vivaminima

- Free tools: [skill-audit-kit](https://github.com/vivaminima/skill-audit-kit) · [secret-map](https://github.com/vivaminima/secret-map) · [inbox-ledger](https://github.com/vivaminima/inbox-ledger) · [release-gate](https://github.com/vivaminima/release-gate) · [skill-install-gate](https://github.com/vivaminima/skill-install-gate) · [console-safe](https://github.com/vivaminima/console-safe) · [checklist-stop](https://github.com/vivaminima/checklist-stop) · [handoff-check](https://github.com/vivaminima/handoff-check) · [llm-budget-router-lite](https://github.com/vivaminima/llm-budget-router-lite) · [go-no-go-verdict-skill](https://github.com/vivaminima/go-no-go-verdict-skill) · [ai-company-starter-kit](https://github.com/vivaminima/ai-company-starter-kit) · [beginner-readme-section](https://github.com/vivaminima/beginner-readme-section)

## License

MIT. See `LICENSE`. Independent project, not affiliated with Anthropic.
