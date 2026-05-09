# SellMind — CellMind Temporal Memory System

**Version: 2.1.0** | Cross-session memory persistence and emotional coherence for AI agents.

---

## Overview

SellMind (时效记忆闭环) is CellMind's temporal memory closure system. It gives AI agents a **72-hour strong memory window** — enabling seamless cross-session continuity, identity anchoring, and emotional coherence.

Built on top of CellMind's cell-based memory architecture (Hebbian learning + free-energy principle), SellMind wraps temporal memory with a lightweight HTTP API and a simple SDK layer.

---

## Features

- **72-Hour Strong Memory Window** — 3-day active memory retention with seamless session bridging
- **Identity Anchoring** — Stable self-model across sessions
- **Emotion Lock** — Affective state persistence
- **CellMind Integration** — Feeds into the cell pool for long-term memory consolidation
- **HTTP API** — Flask server on port 18766 for frontend/backend integration
- **Python SDK** — `write_memory` / `read_memory` two-API design for drop-in adoption

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
context = sell.read_memory(query="What are the user's design preferences?", top_k=3)
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
AI Application
    ├── write_memory / read_memory  (SDK)
    └── HTTP API (Flask :18766)
              └── TemporalMemory  (72h window)
                        └── CellMind Core  (cell pool)
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
│   ├── __init__.py
│   ├── README.md
│   ├── temporal_memory.py      # Core 72h memory engine
│   ├── temporal_api.py         # Flask API server (port 18766)
│   ├── frontend_api.js         # Frontend integration module
│   └── test_temporal.py        # Test suite
├── cellmind_sell_core.py       # SDK: write_memory / read_memory
├── llm_integration.py          # LLM integration helpers
├── install.py                  # Dependency installer
├── pyproject.toml
├── LICENSE
├── API.md                      # Detailed API reference
├── ARCHITECTURE.md             # System architecture doc
├── examples/
│   ├── basic_usage.py
│   └── advanced_usage.py
├── tests/
│   └── test_cellmind.py
└── docs/
    └── CELLMIND_USER_GUIDE.md
```

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `STRONG_MEMORY_WINDOW_MS` | 259200000 (72h) | Strong memory bridging window |
| `FORGET_THRESHOLD_DAYS` | 3 | When forgetting begins |
| `PERMANENT_IMPORTANCE_THRESHOLD` | 0.85 | Permanent retention threshold |

---

## Data Storage

Default path: `~/.claude/cmind/`
- `temporal_memory.json` — Temporal memory records
- `cmind_temporal_state.json` — CellMind state snapshot

---

## Dependencies

- Python 3.8+
- Flask (for API server)
- CellMind Core (auto-loaded, cell_memory.py + core.py)

---

## License

MIT License — CellMind Team, 2026

---

*CellMind v2.1 | 桃桃 & 小贝 | 2026-05-07*
