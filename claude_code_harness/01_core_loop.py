"""Step 1 -- The core agent loop.

At the center of Claude Code is a plain agent loop: send a message, the
model either answers or requests tools; run the tools, feed the results
back, repeat until the model answers with no further tool calls.

This step implements that loop by hand with the Anthropic SDK, so you can
see exactly what CrewAI automates in every later step. The article's
pseudocode:

    while True:
        reply = model(messages, tools)
        calls = [b for b in reply if b.type == "tool_use"]
        if not calls:            # plain text, no tool call: the job is done
            return reply.text
        messages += [reply, run_all(calls)]

Run:  ANTHROPIC_API_KEY=... python 01_core_loop.py
"""

import json
import os
from pathlib import Path

import anthropic

from config import ANTHROPIC_MODEL, WORKSPACE_DIR

# --- Tools: the "hands" the loop gives the model -------------------------

TOOLS = [
    {
        "name": "list_dir",
        "description": "List the files in a directory inside the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path relative to the workspace root."}
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file inside the workspace and return its contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to the workspace root."}
            },
            "required": ["path"],
        },
    },
]


def _resolve(path: str) -> Path:
    """Confine every file operation to the workspace root."""
    root = Path(WORKSPACE_DIR).resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Path escapes the workspace: {path}")
    return target


def execute_tool(name: str, tool_input: dict) -> str:
    try:
        if name == "list_dir":
            target = _resolve(tool_input["path"])
            return "\n".join(sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir()))
        if name == "read_file":
            return _resolve(tool_input["path"]).read_text()
        return f"Unknown tool: {name}"
    except Exception as exc:  # surface tool failures to the model, don't crash the loop
        return f"Error: {exc}"


# --- The loop itself ------------------------------------------------------

def agent_loop(user_message: str) -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]

    while True:
        reply = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=16000,
            tools=TOOLS,
            messages=messages,
        )

        calls = [b for b in reply.content if b.type == "tool_use"]
        if not calls:  # plain text, no tool call: the job is done
            return next((b.text for b in reply.content if b.type == "text"), "")

        # Append the assistant turn, run every requested tool, and return
        # ALL results in a single user message (parallel tool calls).
        messages.append({"role": "assistant", "content": reply.content})
        results = []
        for call in calls:
            print(f"[tool] {call.name}({json.dumps(call.input)})")
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": execute_tool(call.name, call.input),
                }
            )
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    answer = agent_loop(
        "Explore the workspace ('.' is the root), read account.py and its tests, "
        "and describe the bugs and the fix. Do not modify anything."
    )
    print("\n=== Final answer ===\n")
    print(answer)
