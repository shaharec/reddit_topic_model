"""Step 3 -- Giving the agent tools.

Tools are what let a text-only model actually work on a codebase. CrewAI
ships filesystem tools out of the box (FileReadTool, FileWriterTool,
DirectoryReadTool); anything more specific is a plain Python function
exposed with the @tool decorator -- the docstring is the instruction
manual the model reads.

The filesystem also doubles as external memory: the agent can park a big
intermediate result in a file and keep only the filename in context
(what Anthropic calls context engineering).

Run:  ANTHROPIC_API_KEY=... python 03_tools.py
"""

import subprocess

from crewai import Agent, Crew, Task
from crewai.tools import tool
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool

from config import CREWAI_MODEL, WORKSPACE_DIR

# --- Built-in filesystem tools --------------------------------------------

read_file = FileReadTool()
write_file = FileWriterTool()
list_dir = DirectoryReadTool(directory=WORKSPACE_DIR)

filesystem_tools = [read_file, write_file, list_dir]


# --- A custom tool: run the test suite ------------------------------------

@tool("run_tests")
def run_tests(path: str = "tests/") -> str:
    """Run the pytest suite at the given path (relative to the workspace)
    and return the result."""
    result = subprocess.run(
        ["pytest", path, "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=WORKSPACE_DIR,
    )
    output = result.stdout + result.stderr
    return output[-4000:] if len(output) > 4000 else output


bug_fixer = Agent(
    role="Bug Fixer",
    goal="Fix the reported bug so the test suite passes. Never modify the tests.",
    backstory="You read code, make the smallest correct change, and verify it with tests.",
    tools=filesystem_tools + [run_tests],
    llm=CREWAI_MODEL,
)

task = Task(
    description=(
        f"In the working directory {WORKSPACE_DIR}, {{objective}}. "
        "Explore the code first, make the change, then run the tests and report."
    ),
    expected_output="A summary of the files changed and the final test output.",
    agent=bug_fixer,
)

if __name__ == "__main__":
    result = Crew(agents=[bug_fixer], tasks=[task]).kickoff(
        inputs={"objective": "fix the overdraft bug in account.py"}
    )
    print(result)
