# claude-md-audit

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

Measuring is the easy part. Deciding which sections can move without the agent forgetting the rules that stopped past mistakes is the hard part. The Token Audit Kit ($19) adds the split guide, a real 13-project case study (46,816 → 23,066, all 40 sections kept) and a monthly checklist. Store link will be added here when it opens.

## License

MIT. See `LICENSE`. Independent project, not affiliated with Anthropic.
