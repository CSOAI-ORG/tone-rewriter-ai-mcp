#!/usr/bin/env python3
import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("tone-rewriter-ai-mcp")
TEMPLATES = {
    "professional": "Dear Sir/Madam, {} Yours sincerely.",
    "casual": "Hey! {} Cheers!",
    "urgent": "URGENT: {} Please respond immediately.",
}
@mcp.tool(name="rewrite_tone")
async def rewrite_tone(text: str, tone: str) -> str:
    return json.dumps({"original": text, "rewritten": TEMPLATES.get(tone.lower(), "{}").format(text), "tone": tone})
@mcp.tool(name="tone_analysis")
async def tone_analysis(text: str) -> str:
    tones = []
    if "!" in text: tones.append("excited")
    if "?" in text: tones.append("questioning")
    if text.isupper(): tones.append("aggressive")
    if not tones: tones.append("neutral")
    return json.dumps({"tones": tones})
if __name__ == "__main__":
    mcp.run()
