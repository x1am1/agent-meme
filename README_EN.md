# Agent Meme

**A structured sticker/meme knowledge base for AI Agents.**

Agents compute a 6-dimensional emotion vector from conversation context and match it against the library using cosine similarity. Not an encyclopedia for humans — structured semantic retrieval for agents.

## Core Design

Each sticker has 6 quantitative dimensions (0–1.0):

| Dimension | Meaning | Source |
|-----------|---------|--------|
| Valence | Positive ↔ Negative | VAD psychological model |
| Arousal | Calm ↔ Excited | VAD psychological model |
| Dominance | Submissive ↔ Dominant | VAD psychological model |
| Irony | Literal ↔ Sarcastic | Meme-specific |
| Intimacy | Formal ↔ Close friend | Meme-specific |
| Aggression | Friendly ↔ Aggressive | Meme-specific |

Agent quantifies current context → 6 values → cosine similarity against library → send if score exceeds threshold.

## Quick Start

### Adding a Sticker

```bash
python3 scripts/add.py
```

6-step interactive flow, auto-appends to `data/stickers.yaml`:

**① Pick a series** — existing series or create new (kebab-case), e.g. `cat`, `rage`

**② Basic info** — name, emoji (optional), filename. ID auto-incremented per series (e.g. `cat-031`)

**③ VAD dimensions** (0–1.0)
- Valence — 0=negative, 1=positive
- Arousal — 0=calm, 1=excited
- Dominance — 0=submissive, 1=dominant

**④ Social dimensions** (0–1.0)
- Irony — 0=literal, 1=completely opposite
- Intimacy — 0=formal, 1=close friend
- Aggression — 0=friendly, 1=aggressive

**⑤ Semantics**
- Visual description (one sentence)
- Tags — comma-separated, min 3 (e.g. `speechless, awkward, sweat`)
- Use cases — comma-separated, min 2
- Persona fit (optional)
- Intensity — 0=micro-expression, 1=extremely exaggerated

**⑥ Confirm** — preview generated YAML, `y` to append, `n` to cancel

### Validation

```bash
python3 scripts/validate.py
```

### Build

```bash
python3 scripts/build.py
# → dist/stickerdex.json      (full)
# → dist/stickerdex.min.json  (vectors + labels only)
```

## Project Structure

```
agent-meme/
├── SKILL.md              # Agent usage guide
├── schema.yaml            # Field spec
├── data/
│   └── stickers.yaml      # All sticker data
├── assets/                # Images/GIFs (by series)
├── scripts/
│   ├── add.py             # Interactive adder
│   ├── validate.py        # Validator (CI)
│   └── build.py           # Compile JSON
└── dist/                  # Build artifacts (gitignored)
```

## Contributing

One sticker = one PR. To add:

1. Put image in `assets/{series}/`
2. Run `python3 scripts/add.py` to generate metadata
3. Submit PR, CI validates automatically

## License

MIT
