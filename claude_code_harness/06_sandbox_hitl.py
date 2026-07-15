"""Step 6 -- Sandboxing and human-in-the-loop approval.

An agent with shell access can run a destructive command, and telling the
model not to isn't a safeguard. Real protection is two layers:

1. A sandbox that isolates execution -- here E2B, which spins up a fresh
   VM per session and destroys it afterward. Shell commands and Python
   run entirely inside that isolated environment, never on the host.
2. A permission system -- human_input=True on a Task pauses the crew after
   it produces an answer so you can approve it or send it back.

Requires an E2B account:  pip install 'crewai-tools[e2b]'  and E2B_API_KEY.

Run:  ANTHROPIC_API_KEY=... E2B_API_KEY=... python 06_sandbox_hitl.py
"""

from crewai import Agent, Crew, LLM, Task
from crewai_tools import E2BExecTool, E2BPythonTool, FileReadTool

from config import CREWAI_MODEL, WORKSPACE_DIR

llm = LLM(model=CREWAI_MODEL)

# Code runs inside E2B's VM, not on this machine.
sandbox_tools = [E2BExecTool(), E2BPythonTool()]

tester = Agent(
    role="Test Runner",
    goal="Run the tests in the sandbox and report pass or fail.",
    backstory="You execute code only inside the isolated sandbox, never on the host.",
    tools=sandbox_tools + [FileReadTool()],
    llm=llm,
)

task = Task(
    description=(
        f"In the working directory {WORKSPACE_DIR}, {{objective}}. "
        "Explore the code first, run the tests in the sandbox, and report."
    ),
    expected_output="A summary of the test run and the final test output.",
    agent=tester,
    # Pause for review: approve the output or send it back for another pass.
    # (Behind a web app or chat UI, CrewAI's webhook-based HITL system
    # handles the same review step instead of stdin.)
    human_input=True,
)

if __name__ == "__main__":
    result = Crew(agents=[tester], tasks=[task]).kickoff(
        inputs={"objective": "run the test suite for account.py and summarize the failures"}
    )
    print(result)
