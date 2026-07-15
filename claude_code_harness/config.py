"""Shared configuration for the harness steps.

Every step reads the model from here so you can swap it in one place
(or via the CLAUDE_MODEL environment variable). The article used
Claude Sonnet 4.6; we default to Claude Opus 4.8, the current
most capable Opus-tier model.

CrewAI routes LLM calls through LiteLLM, which expects the
"anthropic/<model-id>" prefix. The raw core loop (step 01) talks to the
Anthropic SDK directly and uses the bare model id.
"""

import os
from pathlib import Path

# Bare Anthropic model id (used by 01_core_loop.py via the anthropic SDK).
ANTHROPIC_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")

# LiteLLM-style model string (used by every CrewAI step).
CREWAI_MODEL = f"anthropic/{ANTHROPIC_MODEL}"

# The demo codebase the harness operates on.
WORKSPACE_DIR = str(Path(__file__).parent / "workspace")
