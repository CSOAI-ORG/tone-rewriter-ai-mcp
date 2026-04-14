#!/usr/bin/env python3
"""Tone Rewriter AI MCP — MEOK AI Labs. Text tone analysis, transformation, and style matching."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, re
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("tone-rewriter-ai", instructions="Text tone analysis and rewriting. Analyze, transform, and match text tone for professional, casual, formal, and other styles. By MEOK AI Labs.")

# Tone transformation templates and patterns
TONE_PATTERNS = {
    "professional": {
        "greeting": "Dear {recipient},",
        "closing": "Kind regards,",
        "replacements": [("hi", "Hello"), ("hey", "Hello"), ("thanks", "Thank you"), ("gonna", "going to"), ("wanna", "want to"), ("gotta", "need to"), ("yeah", "yes"), ("nope", "no"), ("ok", "understood"), ("asap", "at your earliest convenience")],
        "remove_patterns": [r'\b(lol|haha|omg|bruh)\b'],
    },
    "casual": {
        "greeting": "Hey!",
        "closing": "Cheers!",
        "replacements": [("Dear Sir/Madam", "Hey there"), ("Thank you", "Thanks"), ("at your earliest convenience", "ASAP"), ("I would like to", "I'd like to"), ("Please find attached", "Here's"), ("Kind regards", "Cheers"), ("Furthermore", "Also"), ("However", "But")],
        "remove_patterns": [],
    },
    "formal": {
        "greeting": "Dear Sir/Madam,",
        "closing": "Yours faithfully,",
        "replacements": [("hi", "Good day"), ("hey", "Good day"), ("thanks", "I am grateful"), ("want to", "wish to"), ("need to", "am required to"), ("get", "obtain"), ("use", "utilise"), ("help", "assist"), ("buy", "purchase"), ("ask", "enquire")],
        "remove_patterns": [r'\b(lol|haha|omg|bruh|tbh|ngl|imo)\b', r'!{2,}'],
    },
    "urgent": {
        "greeting": "URGENT:",
        "closing": "Immediate response required.",
        "replacements": [("please", "PLEASE"), ("important", "CRITICAL"), ("soon", "IMMEDIATELY"), ("when you can", "NOW")],
        "remove_patterns": [],
    },
    "empathetic": {
        "greeting": "I understand this is important to you.",
        "closing": "Please don't hesitate to reach out if you need anything else.",
        "replacements": [("you must", "you might consider"), ("you should", "it might help to"), ("you need to", "it would be beneficial to"), ("wrong", "could be improved"), ("failed", "didn't go as planned"), ("problem", "challenge")],
        "remove_patterns": [],
    },
}

SENTIMENT_WORDS = {
    "positive": ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "happy", "pleased", "delighted", "perfect", "brilliant"],
    "negative": ["bad", "terrible", "awful", "horrible", "hate", "angry", "disappointed", "frustrated", "annoyed", "poor", "wrong", "failed"],
    "neutral": ["okay", "fine", "acceptable", "adequate", "standard", "normal", "average", "typical"],
    "urgent": ["urgent", "immediately", "asap", "critical", "emergency", "deadline", "now", "hurry"],
    "formal": ["therefore", "furthermore", "consequently", "regarding", "hereby", "pursuant", "accordingly"],
    "casual": ["hey", "lol", "gonna", "wanna", "gotta", "yeah", "nope", "cool", "awesome", "btw"],
}


@mcp.tool()
def analyze_tone(text: str, api_key: str = "") -> str:
    """Analyze the tone and sentiment of text. Returns detected tones, formality level, and word-level analysis."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    sentence_count = max(1, len(re.split(r'[.!?]+', text.strip())))
    avg_sentence_len = word_count / sentence_count

    tone_scores = {}
    for tone, keywords in SENTIMENT_WORDS.items():
        matches = [w for w in words if w in keywords]
        tone_scores[tone] = {"score": round(len(matches) / max(1, word_count) * 100, 1), "words_found": matches}

    # Formality score (0-100)
    formality = 50
    if tone_scores["formal"]["score"] > 0: formality += 20
    if tone_scores["casual"]["score"] > 0: formality -= 20
    if avg_sentence_len > 15: formality += 10
    if avg_sentence_len < 8: formality -= 10
    if text.count("!") > 2: formality -= 10
    if "Dear" in text or "Regards" in text: formality += 15
    formality = max(0, min(100, formality))

    # Detect primary tone
    primary = max(tone_scores, key=lambda t: tone_scores[t]["score"]) if any(tone_scores[t]["score"] > 0 for t in tone_scores) else "neutral"

    return {
        "primary_tone": primary,
        "tone_scores": {k: v["score"] for k, v in tone_scores.items()},
        "formality_score": formality,
        "formality_label": "very formal" if formality > 80 else "formal" if formality > 60 else "neutral" if formality > 40 else "casual" if formality > 20 else "very casual",
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sentence_len, 1),
        "exclamation_count": text.count("!"),
        "question_count": text.count("?"),
    }


@mcp.tool()
def rewrite_tone(text: str, target_tone: str, api_key: str = "") -> str:
    """Rewrite text in a target tone (professional, casual, formal, urgent, empathetic)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    tone_key = target_tone.lower().strip()
    if tone_key not in TONE_PATTERNS:
        return {"error": f"Unknown tone '{target_tone}'. Available: {', '.join(TONE_PATTERNS.keys())}"}

    pattern = TONE_PATTERNS[tone_key]
    result = text

    # Apply replacements (case-insensitive)
    for old, new in pattern["replacements"]:
        result = re.sub(re.escape(old), new, result, flags=re.IGNORECASE)

    # Remove unwanted patterns
    for pat in pattern["remove_patterns"]:
        result = re.sub(pat, "", result, flags=re.IGNORECASE)

    # Clean up whitespace
    result = re.sub(r'\s+', ' ', result).strip()

    return {
        "original": text,
        "rewritten": result,
        "target_tone": tone_key,
        "changes_made": sum(1 for old, new in pattern["replacements"] if old.lower() in text.lower()),
    }


@mcp.tool()
def compare_tones(text_a: str, text_b: str, api_key: str = "") -> str:
    """Compare the tone of two text samples."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    def quick_analysis(text):
        words = re.findall(r'\b\w+\b', text.lower())
        scores = {}
        for tone, keywords in SENTIMENT_WORDS.items():
            matches = len([w for w in words if w in keywords])
            scores[tone] = round(matches / max(1, len(words)) * 100, 1)
        return scores

    scores_a = quick_analysis(text_a)
    scores_b = quick_analysis(text_b)

    differences = {}
    for tone in scores_a:
        diff = scores_b[tone] - scores_a[tone]
        if abs(diff) > 0.5:
            differences[tone] = round(diff, 1)

    return {
        "text_a_tones": scores_a,
        "text_b_tones": scores_b,
        "differences": differences,
        "more_formal": "text_a" if scores_a.get("formal", 0) > scores_b.get("formal", 0) else "text_b",
        "more_positive": "text_a" if scores_a.get("positive", 0) > scores_b.get("positive", 0) else "text_b",
    }


@mcp.tool()
def suggest_tone(context: str, audience: str = "general", api_key: str = "") -> str:
    """Suggest the best tone for a given context and audience."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    context_lower = context.lower()
    audience_lower = audience.lower()

    recommendations = []
    if any(w in context_lower for w in ["complaint", "issue", "problem", "angry", "upset"]):
        recommendations.append({"tone": "empathetic", "reason": "Customer service/complaint handling benefits from empathetic tone"})
    if any(w in context_lower for w in ["proposal", "board", "investor", "report", "meeting"]):
        recommendations.append({"tone": "formal", "reason": "Business communications should use formal tone"})
    if any(w in context_lower for w in ["deadline", "urgent", "emergency", "critical"]):
        recommendations.append({"tone": "urgent", "reason": "Time-sensitive situations need urgent, clear tone"})
    if any(w in context_lower for w in ["blog", "social", "newsletter", "update"]):
        recommendations.append({"tone": "casual", "reason": "Content marketing works best with approachable, casual tone"})
    if any(w in audience_lower for w in ["executive", "client", "stakeholder", "partner"]):
        recommendations.append({"tone": "professional", "reason": "External stakeholder communication requires professional tone"})

    if not recommendations:
        recommendations.append({"tone": "professional", "reason": "Default professional tone suits most contexts"})

    return {"context": context, "audience": audience, "recommendations": recommendations}


if __name__ == "__main__":
    mcp.run()
