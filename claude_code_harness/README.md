# Building Claude Code's Harness (step-by-step)

An implementation of Akshay Pachaar's article **"Let's build Claude Code's
harness (step-by-step)"** — rebuilding the machinery around a coding agent
(the *harness*) layer by layer in [CrewAI](https://docs.crewai.com).

> The gap between your agent and Claude Code isn't the model, it's the
> machinery around the model. The model is the brain that picks each action;
> the harness is the hands that carry it out and keep the run on track.

## The layers

Each script adds one layer on top of the previous, mapping it to the CrewAI
feature that handles it:

| Step | File | Layer | CrewAI feature |
|------|------|-------|----------------|
| 1 | `01_core_loop.py` | The core agent loop (hand-written with the Anthropic SDK, so you can see what CrewAI automates) | — |
| 2 | `02_first_agent.py` | First agent: who / what / kickoff | `Agent`, `Task`, `Crew.kickoff()` |
| 3 | `03_tools.py` | Filesystem tools + a custom `run_tests` tool | `FileReadTool`, `FileWriterTool`, `DirectoryReadTool`, `@tool` |
| 4 | `04_planning.py` | Planning (crew roadmap) and reasoning (agent-level plan) | `planning=True`, `reasoning=True` |
| 5 | `05_subagents.py` | Delegation: manager + explorer / engineer / test-runner specialists | `Process.hierarchical`, `allow_delegation=True` |
| 6 | `06_sandbox_hitl.py` | Sandboxed execution + human approval | `E2BExecTool`, `E2BPythonTool`, `human_input=True` |
| 7 | `07_memory_checkpointing.py` | Persistent memory across runs; resumable checkpoints | `memory=True`, `checkpoint=True` |
| 8 | `08_full_harness.py` | **Everything together** on the evaluation task | all of the above |

## The evaluation

`workspace/` contains a small codebase the harness operates on — a
`BankAccount` class with **two real bugs** and **five tests, three of which
fail**:

- Bug 1: `withdraw()` allows overdrafts instead of raising `ValueError`.
- Bug 2: `transfer()` only credits half the amount to the destination.

The rule: **fix only the implementation, never the tests.** Success means
taking the suite from 3 failing / 2 passing to all 5 passing — mirroring how
Anthropic evaluates coding agents against suites of failing tests.

```sh
cd workspace && pytest tests/ -q   # 3 failed, 2 passed  (before the harness runs)
```

## Setup

```sh
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# optional — E2B sandboxing for steps 6 and 8:
pip install 'crewai-tools[e2b]'
export E2B_API_KEY=e2b_...
```

The model defaults to `claude-opus-4-8` (the article used Claude
Sonnet 4.6); override with `export CLAUDE_MODEL=claude-sonnet-4-6`
(see `config.py`).

## Run

```sh
python 01_core_loop.py     # then 02, 03, ... in order
python 08_full_harness.py  # the full harness on the bug-fixing task
```

`08_full_harness.py` runs tests locally unless `E2B_API_KEY` is set, in which
case the `run_tests` tool syncs `workspace/` into a fresh E2B VM and runs
pytest there. Because it uses `human_input=True`, the run pauses in the
terminal for your approval before accepting the result. Memory and
checkpoints are written to CrewAI's local storage; run it twice and the
second run starts with what the first one learned.

If a run edits `workspace/account.py`, restore the buggy version with
`git checkout -- workspace/account.py` to try again.

## What's still your job

The parts no framework builds for you: the prompts (role / goal / backstory),
the execution environment (E2B or a self-managed VM), and tool selection —
which agent gets which tools. And the harness has a cost: planning,
subagents, and looping all add API calls, so measure before you stack layers
a single model call could have solved.
