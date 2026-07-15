"""Step 8 -- Putting it all together.

The full harness on one task: the execution loop, filesystem + test tools,
planning, hierarchical subagents, sandboxing, human approval, memory, and
checkpointing working together.

The evaluation mirrors how Anthropic tests coding agents: a concrete,
automatically-checkable objective. The workspace ships a BankAccount class
with two real bugs and five tests, three of which fail. The rule is to fix
only the implementation, never the tests -- success is taking the suite
from 3 failing / 2 passing to all 5 passing.

By default tests run locally inside the workspace; set E2B_API_KEY (and
pip install 'crewai-tools[e2b]') to run them in an isolated E2B VM instead,
as in the article.

Run:  ANTHROPIC_API_KEY=... python 08_full_harness.py
"""

import os
import shlex
import subprocess

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool

from config import CREWAI_MODEL, WORKSPACE_DIR

llm = LLM(model=CREWAI_MODEL)

# --- Tools -----------------------------------------------------------------

read_file = FileReadTool()
write_file = FileWriterTool()
list_dir = DirectoryReadTool(directory=WORKSPACE_DIR)
filesystem_tools = [read_file, write_file, list_dir]

USE_E2B = bool(os.getenv("E2B_API_KEY"))

if USE_E2B:
    from crewai_tools import E2BExecTool, E2BPythonTool

    exec_tool = E2BExecTool()
    sandbox_tools = [exec_tool, E2BPythonTool()]

    def sync_and_test_command(path: str) -> str:
        """Sync ./workspace into the sandbox, then run pytest there."""
        steps = ["mkdir -p /workspace"]
        for root, _dirs, files in os.walk(WORKSPACE_DIR):
            rel_root = os.path.relpath(root, WORKSPACE_DIR)
            for name in files:
                if name.endswith(".pyc"):
                    continue
                rel = os.path.normpath(os.path.join(rel_root, name))
                content = open(os.path.join(root, name)).read()
                steps.append(f"mkdir -p /workspace/{shlex.quote(os.path.dirname(rel) or '.')}")
                steps.append(f"cat > /workspace/{shlex.quote(rel)} <<'HARNESS_EOF'\n{content}\nHARNESS_EOF")
        steps.append("pip install -q pytest")
        steps.append(f"cd /workspace && pytest {shlex.quote(path)} -q")
        return " && ".join(steps)

    @tool("run_tests")
    def run_tests(path: str = "tests/") -> str:
        """Sync ./workspace into the sandbox, then run pytest there."""
        return exec_tool.run(command=sync_and_test_command(path))

else:
    sandbox_tools = []

    @tool("run_tests")
    def run_tests(path: str = "tests/") -> str:
        """Run the pytest suite at the given path (relative to the workspace)
        and return the result."""
        result = subprocess.run(
            ["pytest", path, "-q"],
            capture_output=True, text=True, timeout=120, cwd=WORKSPACE_DIR,
        )
        output = result.stdout + result.stderr
        return output[-4000:] if len(output) > 4000 else output


# --- Agents ------------------------------------------------------------------

explorer = Agent(
    role="Codebase Explorer",
    goal="Map the repo and surface the files relevant to the task.",
    backstory="You read directories and files to build a picture of the code.",
    tools=[read_file, list_dir],
    llm=llm,
)

coder = Agent(
    role="Software Engineer",
    goal="Implement the requested change. Fix the implementation only -- never the tests.",
    backstory="You make small, correct edits and reason before acting.",
    tools=filesystem_tools,
    reasoning=True,
    llm=llm,
)

tester = Agent(
    role="Test Runner",
    goal="Run the tests and report pass or fail.",
    backstory="You verify every change against the test suite.",
    tools=sandbox_tools + [read_file, run_tests],
    llm=llm,
)

manager = Agent(
    role="Engineering Lead",
    goal="Delegate steps to the right specialist; finish once all tests pass.",
    backstory="You coordinate the explorer, engineer, and test runner.",
    allow_delegation=True,
    llm=llm,
)

# --- Task + Crew --------------------------------------------------------------

task = Task(
    description=(
        f"In the working directory {WORKSPACE_DIR}, {{objective}}. "
        "Explore the code first, make the change, then run the tests and report. "
        "Rule: fix only the implementation, never edit or remove the tests."
    ),
    expected_output="Summary of the files changed and the final test output.",
    human_input=True,  # pause for approval before accepting the result
)

crew = Crew(
    agents=[explorer, coder, tester],
    tasks=[task],
    manager_agent=manager,
    process=Process.hierarchical,  # subagent orchestration
    planning=True,                 # roadmap kept in context throughout
    planning_llm=llm,
    memory=True,                   # facts persist across runs
    checkpoint=True,               # resume-able snapshots per finished task
)

if __name__ == "__main__":
    result = crew.kickoff(
        inputs={"objective": "fix the failing tests in account.py"}
    )
    print(result)
