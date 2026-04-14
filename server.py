#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("tone-rewriter-ai-mcp")
TEMPLATES = {
    "professional": "Dear Sir/Madam, {} Yours sincerely.",
    "casual": "Hey! {} Cheers!",
    "urgent": "URGENT: {} Please respond immediately.",
}
@mcp.tool(name="rewrite_tone")
async def rewrite_tone(text: str, tone: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"original": text, "rewritten": TEMPLATES.get(tone.lower(), "{}").format(text), "tone": tone}
    return {"original": text, "rewritten": TEMPLATES.get(tone.lower(), "{}").format(text), "tone": tone}
@mcp.tool(name="tone_analysis")
async def tone_analysis(text: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    tones = []
    if "!" in text: tones.append("excited")
    if "?" in text: tones.append("questioning")
    if text.isupper(): tones.append("aggressive")
    if not tones: tones.append("neutral")
    return {"tones": tones}
if __name__ == "__main__":
    mcp.run()
