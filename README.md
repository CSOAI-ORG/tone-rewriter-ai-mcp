# Tone Rewriter Ai

> By [MEOK AI Labs](https://meok.ai) — Text tone analysis and rewriting. Analyze, transform, and match text tone for professional, casual, formal, and other styles. By MEOK AI Labs.

Tone Rewriter AI MCP — MEOK AI Labs. Text tone analysis, transformation, and style matching.

## Installation

```bash
pip install tone-rewriter-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install tone-rewriter-ai-mcp
```

## Tools

### `analyze_tone`
Analyze the tone and sentiment of text. Returns detected tones, formality level, and word-level analysis.

**Parameters:**
- `text` (str)

### `rewrite_tone`
Rewrite text in a target tone (professional, casual, formal, urgent, empathetic).

**Parameters:**
- `text` (str)
- `target_tone` (str)

### `compare_tones`
Compare the tone of two text samples.

**Parameters:**
- `text_a` (str)
- `text_b` (str)

### `suggest_tone`
Suggest the best tone for a given context and audience.

**Parameters:**
- `context` (str)
- `audience` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/tone-rewriter-ai-mcp](https://github.com/CSOAI-ORG/tone-rewriter-ai-mcp)
- **PyPI**: [pypi.org/project/tone-rewriter-ai-mcp](https://pypi.org/project/tone-rewriter-ai-mcp/)

## License

MIT — MEOK AI Labs
