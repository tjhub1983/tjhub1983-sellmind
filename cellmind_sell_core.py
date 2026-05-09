# CellMind-Sell Core — 开源接口层
# Copyright 2026 CellMind Team
# SPDX-License-Identifier: MIT
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software...（见完整MIT文本：LICENSE文件）

import importlib.util
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

# ============================================================
# 延迟加载CellMindCore（绕过数字开头模块名限制）
# ============================================================

def _load_core():
    spec = importlib.util.spec_from_file_location(
        '_cell_core',
        os.path.join(os.path.dirname(__file__), '../CellMind-Core/cell_core/17_cmind_integration.py')
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CellMindCore


# ============================================================
# sell_core API
# ============================================================

class CellMindSell:
    """write_memory / read_memory 两个API，复杂逻辑封装在CellMindCore内部"""

    def __init__(self, agent_id: str = "sell"):
        self._core = None
        self._agent_id = agent_id
        self._lock = threading.RLock()
        self._load_done = False

    @property
    def core(self):
        if self._core is None:
            Core = _load_core()
            self._core = Core(state_dir=os.path.expanduser("~/.claude/sell/"), agent_id=self._agent_id)
        return self._core

    def write_memory(self, text: str, memory_type: str = "general",
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> dict:
        """写入任意文本到CellMind记忆，返回记忆ID和提取的关键词"""
        with self._lock:
            tokens = self.core.activate_text(text)
            memory_ids = []

            type_tag = {"preference": "preference", "goal": "goal",
                        "skill": "skill", "relationship": "relationship"}.get(memory_type, [])
            tag_list = ([type_tag] if isinstance(type_tag, str) else type_tag) + (tags or [])

            for token in tokens:
                cell = self.core.cell_memory.get_or_create(token)
                memory_ids.append(cell.cell_id)
                if tag_list:
                    cell.goal_tags = list(set(cell.goal_tags + tag_list))

            self.core.save()
            return {
                "success": True,
                "memory_ids": memory_ids,
                "tokens_extracted": tokens,
                "memory_type": memory_type,
                "timestamp": datetime.now().isoformat(),
            }

    def read_memory(self, query: str, top_k: int = 5,
                   memory_type: str = None) -> dict:
        """查询CellMind记忆，返回相关记忆列表（不产生副作用）"""
        with self._lock:
            query_tokens = self._extract(query)
            all_cells = self.core.cell_memory.get_top_cells(50)

            filter_tag = {"preference": "preference", "goal": "goal",
                          "skill": "skill", "relationship": "relationship"}.get(memory_type)

            results = [
                {
                    "preference": c.preference,
                    "strength": round(c.strength, 3),
                    "memory_type": _infer_type(c.goal_tags),
                    "connections": len(c.connections),
                    "response_count": c.response_count,
                    "last_active": c.last_active,
                }
                for c in all_cells
                if not filter_tag or filter_tag in c.goal_tags
            ][:top_k]

            return {
                "query": query,
                "results": results,
                "total_cells": len(self.core.cell_memory.cells),
                "timestamp": datetime.now().isoformat(),
            }

    def get_status(self) -> dict:
        return self.core.get_status()

    def save(self):
        self.core.save()

    def reset(self):
        with self._lock:
            self.core.cell_memory.cells.clear()
            self.core.working_memory.items.clear()
            self.core.save()

    @staticmethod
    def _extract(text: str) -> List[str]:
        import re
        stop = {"the", "a", "an", "is", "are", "was", "be", "have", "has", "do", "does",
                "will", "would", "could", "should", "can", "need", "to", "of", "in", "for",
                "on", "with", "at", "by", "from", "as", "and", "but", "or", "if", "i", "you",
                "he", "she", "it", "we", "they", "this", "that", "what", "which", "who"}
        words = re.findall(r"[a-z]+", text.lower())
        return [w for w in words if len(w) >= 3 and w not in stop]


def _infer_type(tags: List[str]) -> str:
    for t in ["goal", "skill", "preference", "relationship"]:
        if t in tags:
            return t
    return "general"


_sell_instance: Optional[CellMindSell] = None
_sell_lock = threading.Lock()


def get_sell() -> CellMindSell:
    global _sell_instance
    if _sell_instance is None:
        with _sell_lock:
            if _sell_instance is None:
                _sell_instance = CellMindSell()
    return _sell_instance
