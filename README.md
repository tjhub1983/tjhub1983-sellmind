# SellMind - Temporal Memory for AI

**Version 2.1.0** | Cross-session memory persistence with emotional coherence. Built for Claude Code agents.

---

## What It Does

SellMind gives AI agents a **72-hour strong memory window** — seamless continuity across sessions, stable identity anchoring, and persistent emotional state. Part of the [CellMind](https://github.com/tjhub1983/cellmind) ecosystem.

> SellMind 时效记忆闭环 — CellMind的记忆系统核心，赋予AI跨会话记忆能力。

---

## Features

- :clock1: **72-Hour Strong Memory Window** — 3-day active retention with seamless session bridging
- :anchor: **Identity Anchoring** — Stable self-model preserved across sessions
- :heart: **Emotion Lock** — Affective state persistence with valence tracking
- :brain: **CellMind Integration** — Feeds into Hebbian cell pool for long-term consolidation
- :zap: **HTTP API** — Flask server on port 18766 for frontend/backend integration
- :snake: **Python SDK** — Two-API design (`write_memory` / `read_memory`) for drop-in adoption

---

## Quick Start

### API Server

```bash
pip install flask
python sellmind/temporal_api.py
```

### Python SDK

```python
from sellmind.cellmind_sell_core import CellMindSell

sell = CellMindSell()

# Write a memory
sell.write_memory(
    text="User prefers minimal design, dislikes heavy decoration",
    memory_type="preference",
    tags=["design", "ux"]
)

# Query memories
context = sell.read_memory(query="design preferences", top_k=3)
for item in context["results"]:
    print(item["preference"], item["strength"])
```

### Temporal Memory Core

```python
from sellmind.temporal_memory import TemporalMemory

tm = TemporalMemory()
tm.add_record("Hello, how are you?", "user", "neutral", "greeting")
prompt = tm.build_context_prompt()
```

---

## Architecture

```
┌─────────────────────┐
│   AI Application    │
│  (Claude Code etc.) │
└────────┬────────────┘
         │ write_memory / read_memory  (SDK)
         ▼
┌─────────────────────┐
│   HTTP API Server   │  Flask :18766
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  TemporalMemory     │  72h window + Hebbian decay
│  (sellmind/)        │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│   CellMind Core     │  Cell pool + free-energy principle
│   (long-term)       │
└─────────────────────┘
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/new-window/init` | GET | Initialize new session window |
| `/temporal/context` | GET | Retrieve recent context |
| `/temporal/context/prompt` | GET | Get context as prompt string |
| `/discuss` | POST | Record dialog + commit to memory |
| `/emotion/update` | POST | Update affective state |
| `/identity` | GET | Get identity anchor info |
| `/status` | GET | System status |
| `/save` | POST | Trigger persistence save |

---

## Project Structure

```
sellmind/
├── sellmind/                  # Temporal memory core
│   ├── temporal_memory.py      # Core 72h memory engine
│   ├── temporal_api.py         # Flask API server (port 18766)
│   ├── frontend_api.js         # Frontend integration module
│   └── test_temporal.py        # Test suite
├── cellmind_sell_core.py       # SDK: write_memory / read_memory
├── llm_integration.py          # LLM integration helpers
├── install.py                  # Dependency installer
├── pyproject.toml
├── API.md                      # Detailed API reference
├── ARCHITECTURE.md             # System architecture doc
├── examples/
│   ├── basic_usage.py
│   └── advanced_usage.py
└── tests/
    └── test_cellmind.py
```

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `STRONG_MEMORY_WINDOW_MS` | 259200000 (72h) | Strong memory bridging window |
| `FORGET_THRESHOLD_DAYS` | 3 | When forgetting begins |
| `PERMANENT_IMPORTANCE_THRESHOLD` | 0.85 | Permanent retention threshold |

**Storage path:** `~/.claude/cmind/`

---

## SellMind vs Other Solutions

| Feature | SellMind | Naive RAG | Vector DB Only |
|---------|----------|-----------|----------------|
| Cross-session continuity | :white_check_mark: | :x: | :x: |
| Emotional state tracking | :white_check_mark: | :x: | :x: |
| Identity anchoring | :white_check_mark: | :x: | :x: |
| 72h temporal window | :white_check_mark: | :x: | :x: |
| Hebbian learning | :white_check_mark: | :x: | :x: |
| CellMind integration | :white_check_mark: | :x: | :x: |
| Setup complexity | Low | Medium | High |

---

## Dependencies

- Python 3.8+
- Flask (for API server)
- CellMind Core (auto-loaded: `cell_memory.py` + `core.py`)

---

## License

MIT License — CellMind Team, 2026

---

## Contributing

Contributions welcome! Please open an issue or submit a PR. For major changes, open a discussion first.

*CellMind v2.1 | 时效记忆 & Temporal Memory | 2026-05-09*
