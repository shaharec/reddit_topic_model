"""Step 5 -- Delegating with subagents.

Planning keeps the agent focused, but it doesn't shrink how much the model
must hold. Subagents do: the main agent hands a scoped task to a helper
that works in its OWN context and returns a short summary -- the manager
sees the conclusion, not the intermediate file dumps.

CrewAI supports this with hierarchical workflows: a manager agent
(allow_delegation=True -- disabled by default!) delegates to specialists
and combines their results.

Run:  ANTHROPIC_API_KEY=... python 05_subagents.py
"""

import subprocess

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool

from config import CREWAI_MODEL, WORKSPACE_DIR

llm = LLM(model=CREWAI_MODEL)

read_file = FileReadTool()
write_file = FileWriterTool()
list_dir = DirectoryReadTool(directory=WORKSPACE_DIR)


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


explorer = Agent(
    role="Codebase Explorer",
    goal="Map the repository and surface the files relevant to the task.",
    backstory="You read directories and files to build a picture of the code.",
    tools=[read_file, list_dir],
    llm=llm,
)

coder = Agent(
    role="Software Engineer",
    goal="Implement the requested change. Never modify the tests.",
    backstory="You make small, correct edits informed by the explorer's findings.",
    tools=[read_file, write_file, list_dir],
    llm=llm,
)

tester = Agent(
    role="Test Runner",
    goal="Run the tests and report pass or fail.",
    backstory="You verify every change against the test suite and report the raw result.",
    tools=[read_file, run_tests],
    llm=llm,
)

manager = Agent(
    role="Engineering Lead",
    goal="Break the request into steps and delegate each to the right specialist.",
    backstory="You decide who does what, review tests, finish once the change is done.",
    llm=llm,
    allow_delegation=True,  # off by default -- must be explicit on the manager
)

task = Task(
    description=(
        f"In the working directory {WORKSPACE_DIR}, {{objective}}. "
        "Explore the code first, make the change, then run the tests and report."
    ),
    expected_output="A summary of the files changed and the final test output.",
)

crew = Crew(
    agents=[explorer, coder, tester],
    tasks=[task],
    manager_agent=manager,
    process=Process.hierarchical,
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"objective": "fix the failing tests in account.py"})
    print(result)
