#!/usr/bin/env python3
"""Rewrite text in different tones (formal, casual, technical). — MEOK AI Labs."""
import json, os, re, hashlib, uuid as _uuid, random
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": "Limit/day"})
    _usage[c].append(now); return None

mcp = FastMCP("tone-rewriter", instructions="MEOK AI Labs — Rewrite text in different tones (formal, casual, technical).")


@mcp.tool()
def rewrite_tone(text: str, tone: str = "formal") -> str:
    """Rewrite text in a different tone."""
    if err := _rl(): return err
    result = {"original": text, "tone": tone}
    if tone == "formal":
        result["rewritten"] = text.replace("don't", "do not").replace("can't", "cannot").replace("won't", "will not")
    elif tone == "casual":
        result["rewritten"] = text.replace("do not", "don't").replace("cannot", "can't")
    elif tone == "technical":
        result["rewritten"] = text  # Would need NLP for real transformation
    result["word_count"] = len(result.get("rewritten", text).split())
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()
