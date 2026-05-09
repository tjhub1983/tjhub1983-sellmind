# -*- coding: utf-8 -*-
"""
CellMind LLM多Provider集成 v2.0
==============================
支持：MiniMax / OpenAI / DeepSeek 三路切换

v2.0变更：
- Provider抽象层：通过llm_providers.json配置，代码零改动扩展新Provider
- 响应格式统一：Anthropic风格和OpenAI风格自动适配
- 向后兼容：原有MiniMax-M2.7调用方式完全不变
- 切换方法：call_llm(..., provider="openai") 或 set_default_provider("deepseek")

售后改法：
1. 改 credentials/llm_providers.json 的 api_key_env 指向对应环境变量
2. 代码层直接 call_llm(..., provider="openai") 切换
"""
import json, os, time, random, requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# ============================================================
# 配置加载
# ============================================================
# Path(__file__) 在运行时被解析为当前文件路径
_CELLMIND_ROOT = Path(__file__).resolve().parent
_PROVIDER_CFG = _CELLMIND_ROOT / "credentials" / "llm_providers.json"

def _load_providers():
    with open(_PROVIDER_CFG, encoding="utf-8") as f:
        return json.load(f)

PROVIDERS = _load_providers()
DEFAULT_PROVIDER = PROVIDERS["default_provider"]
TIMEOUT_MS = PROVIDERS.get("timeout_ms", 30000)

def _get_api_key(env_var: str) -> str:
    """从环境变量读取API密钥"""
    return os.environ.get(env_var, "")

def _get_setting(setting_path: str) -> Optional[str]:
    """从Claude settings.json读取配置（兼容旧版）"""
    settings_file = Path.home() / ".claude" / "settings.json"
    if settings_file.exists():
        try:
            cfg = json.loads(settings_file.read_text("utf-8"))
            env = cfg.get("env", {})
            return env.get(setting_path)
        except:
            pass
    return None

# ============================================================
# Provider配置（运行时对象）
# ============================================================
class ProviderConfig:
    def __init__(self, name: str, cfg: dict):
        self.name = name
        self.api_base = cfg["api_base"]
        self.api_key_env = cfg["api_key_env"]
        self.models = cfg["models"]
        self.auth_type = cfg.get("auth_type", "bearer")
        self.anthropic_version = cfg.get("anthropic_version")
        self.response_format = cfg.get("response_format", "openai")

    def get_api_key(self) -> str:
        # 先查环境变量
        key = _get_api_key(self.api_key_env)
        if key:
            return key
        # 再查settings.json（兼容旧）
        if self.name == "minimax":
            key = _get_setting("ANTHROPIC_AUTH_TOKEN")
            if key:
                return key
        return ""

    def resolve_api_base(self) -> str:
        if self.name == "minimax":
            base = _get_setting("ANTHROPIC_BASE_URL")
            if base:
                return base
        return self.api_base

_PROVIDER_OBJECTS = {
    k: ProviderConfig(k, v) for k, v in PROVIDERS["providers"].items()
}

# ============================================================
# Cell & CellMemory（已弃用，请使用 CellMind-Core/cell_core/04_cmind.py）
# 本模块自成一派，未被 scripts/ 或 sell_core 调用
# 保留仅用于 llm_integration.py 内部 LLM 调用时的记忆功能演示
# 如无特殊需求，可移除此区块
# ============================================================
# DEPRECATED: 此 CellMemory 实现已被 E:/CellMind/CellMind-Core/cell_core/04_cmind.py 替代
# Cell & CellMemory（同原版）
DECAY_RATE = 0.95
INITIAL_STRENGTH = 1.0
HEBB_STRENGTH = 0.2
CONNECTION_DECAY = 0.95
ELIMINATION_THRESHOLD = 0.05
MATCH_WEIGHT = 0.5
BOX_DECAY_RATE = 0.99
BOX_SAVE_RATIO = 0.20
BOX_MAX = 5.0

@dataclass
class Cell:
    cell_id: str
    preference: str
    strength: float
    energy_box: float
    connections: Dict[str, float]
    response_count: int
    last_active: str
    born: str

    @staticmethod
    def create(preference: str) -> "Cell":
        now = datetime.now().isoformat()
        return Cell(
            cell_id=f"cell_{random.randint(10000, 99999)}",
            preference=preference,
            strength=INITIAL_STRENGTH,
            energy_box=0.0,
            connections={},
            response_count=0,
            last_active=now,
            born=now
        )

class CellMemory:
    def __init__(self, save_path: str = "./cells.json"):
        self.cells: Dict[str, Cell] = {}
        self.save_path = save_path
        self._load()

    def _load(self):
        if Path(self.save_path).exists():
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cells = {}
                    for k, v in data.items():
                        v.setdefault("energy_box", 0.0)
                        self.cells[k] = Cell(**v)
                print(f"[CellMemory] loaded {len(self.cells)} cells")
            except Exception as e:
                print(f"[CellMemory] load failed: {e}")

    def save(self):
        data = {k: asdict(v) for k, v in self.cells.items()}
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_or_create(self, preference: str) -> Cell:
        for cell in self.cells.values():
            if cell.preference == preference:
                return cell
        cell = Cell.create(preference)
        self.cells[cell.cell_id] = cell
        return cell

    def activate(self, preference: str) -> Optional[Cell]:
        candidates = []
        for cell in self.cells.values():
            if preference in cell.preference or cell.preference in preference:
                candidates.append(cell)
        if not candidates:
            cell = self.get_or_create(preference)
            return cell

        def score(c: Cell) -> float:
            match = len(set(c.preference) & set(preference)) / max(len(c.preference), 1)
            return MATCH_WEIGHT * match + (1 - MATCH_WEIGHT) * (c.strength / INITIAL_STRENGTH)

        candidates.sort(key=score, reverse=True)
        winner = candidates[0]
        boost = HEBB_STRENGTH
        to_box = boost * BOX_SAVE_RATIO
        winner.energy_box = min(BOX_MAX, winner.energy_box + to_box)
        winner.strength = min(2.0, winner.strength + boost - to_box)
        winner.response_count += 1
        winner.last_active = datetime.now().isoformat()
        return winner

    def hebb_connect(self, cell_a: Cell, cell_b: Cell):
        if cell_a.cell_id == cell_b.cell_id:
            return
        current_ab = cell_a.connections.get(cell_b.cell_id, 0.0)
        cell_a.connections[cell_b.cell_id] = min(1.0, current_ab + HEBB_STRENGTH)
        current_ba = cell_b.connections.get(cell_a.cell_id, 0.0)
        cell_b.connections[cell_a.cell_id] = min(1.0, current_ba + HEBB_STRENGTH)

    def decay_all(self, days: float = 1.0):
        box_decay = BOX_DECAY_RATE ** days
        strength_decay = DECAY_RATE ** days
        conn_decay = CONNECTION_DECAY ** days
        for cell in self.cells.values():
            strength_loss = cell.strength * (1 - strength_decay)
            if cell.energy_box > 0:
                compensated = min(cell.energy_box, strength_loss)
                cell.energy_box -= compensated
                strength_loss -= compensated
            cell.strength -= strength_loss
            cell.strength = max(0.0, cell.strength)
            cell.energy_box *= box_decay
            for cid in cell.connections:
                cell.connections[cid] *= conn_decay

    def eliminate_weak(self):
        to_remove = [cid for cid, c in self.cells.items() if c.strength < ELIMINATION_THRESHOLD]
        for cid in to_remove:
            del self.cells[cid]

    def get_top_cells(self, n: int = 5) -> List[Cell]:
        return sorted(self.cells.values(), key=lambda c: c.strength, reverse=True)[:n]

    def activate_sequence(self, preferences: List[str]):
        prev: Optional[Cell] = None
        for pref in preferences:
            cell = self.activate(pref)
            if prev:
                self.hebb_connect(prev, cell)
            prev = cell

    def build_context_prompt(self, query: str, top_n: int = 10) -> str:
        top = self.get_top_cells(top_n)
        if not top:
            return ""
        lines = ["[Internal Context - Not visible to user]", f"# Active cells: {len(top)}"]
        for c in top:
            lines.append(f"- {c.preference} (strength={c.strength:.3f}, responds={c.response_count})")
        lines.append("[End Internal Context]")
        return "\n".join(lines)

# ============================================================
# LLM调用（多Provider）
# ============================================================

def _parse_response(raw: dict, fmt: str) -> str:
    """统一解析不同Provider的响应格式"""
    if fmt == "anthropic":
        for item in raw.get("content", []):
            if item.get("type") == "text":
                return item.get("text", "")
        return ""
    elif fmt == "openai":
        choices = raw.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            return msg.get("content", "")
        return ""
    return ""


def call_llm(messages: List[dict],
             model: Optional[str] = None,
             provider: Optional[str] = None,
             temperature: float = 0.7,
             max_tokens: int = 512) -> Tuple[str, dict]:
    """
    多Provider LLM调用
    - provider: "minimax" / "openai" / "deepseek"，默认走DEFAULT_PROVIDER
    - model: 具体模型名，默认用provider的第一个模型
    - 兼容旧调用：call_llm(messages) 等同于旧API，完全不变
    """
    provider_key = provider or DEFAULT_PROVIDER
    pcfg = _PROVIDER_OBJECTS.get(provider_key)

    if pcfg is None:
        return f"[ERROR: unknown provider '{provider_key}']", {}

    api_key = pcfg.get_api_key()
    if not api_key:
        return f"[ERROR: no API key for provider '{provider_key}' (env: {pcfg.api_key_env})]", {}

    api_base = pcfg.resolve_api_base()

    # 确定模型
    if model is None:
        model = pcfg.models[0] if pcfg.models else provider_key

    # 构建payload
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if pcfg.anthropic_version:
        headers["anthropic-version"] = pcfg.anthropic_version

    if pcfg.response_format == "anthropic":
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    else:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    url = f"{api_base}/v1/messages" if pcfg.response_format == "anthropic" else f"{api_base}/chat/completions"

    try:
        resp = requests.post(url, headers=headers, json=payload,
                             timeout=TIMEOUT_MS / 1000)
        resp.raise_for_status()
        raw = resp.json()
        text = _parse_response(raw, pcfg.response_format)
        return text, raw
    except Exception as e:
        return f"[ERROR: {e}]", {}


def set_default_provider(provider: str):
    """运行时切换默认Provider"""
    global DEFAULT_PROVIDER
    if provider in _PROVIDER_OBJECTS:
        DEFAULT_PROVIDER = provider
        print(f"[LLM] Default provider switched to: {provider}")
    else:
        print(f"[LLM] Unknown provider: {provider}, available: {list(_PROVIDER_OBJECTS.keys())}")


def get_providers() -> Dict[str, dict]:
    """返回当前Provider列表（不含密钥）"""
    return {
        k: {
            "name": v.name,
            "models": v.models,
            "api_base": v.api_base,
            "has_key": bool(v.get_api_key()),
        }
        for k, v in _PROVIDER_OBJECTS.items()
    }

# ============================================================
# 测试套件
# ============================================================

def test_provider_connection(provider: str = "minimax") -> bool:
    """测试指定Provider连通性"""
    pcfg = _PROVIDER_OBJECTS.get(provider)
    if not pcfg:
        print(f"[FAIL] Unknown provider: {provider}")
        return False

    key = pcfg.get_api_key()
    if not key:
        print(f"[FAIL] No API key for {provider} (env: {pcfg.api_key_env})")
        return False

    messages = [{"role": "user", "content": "Reply with exactly one word: OK"}]
    text, raw = call_llm(messages, provider=provider, max_tokens=200)

    if "[ERROR" in text:
        print(f"[FAIL] {provider} call failed: {text}")
        return False

    print(f"[PASS] {provider} connected | response: {text[:50]}")
    return True


if __name__ == "__main__":
    print("CellMind LLM Integration v2.0 (Multi-Provider)")
    print(f"Default provider: {DEFAULT_PROVIDER}")
    print(f"Available: {list(_PROVIDER_OBJECTS.keys())}")
    print("=" * 50)

    # 测试当前默认Provider
    test_provider_connection(DEFAULT_PROVIDER)

    print("\n[Provider Status]")
    for k, v in get_providers().items():
        key_status = "✅ key" if v["has_key"] else "❌ no key"
        print(f"  {k}: {v['name']} | models={v['models']} | {key_status}")