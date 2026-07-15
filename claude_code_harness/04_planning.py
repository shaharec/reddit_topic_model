"""Step 4 -- Planning long-running tasks.

As tasks get longer, the objective gets crowded out of context by tool
output ("context rot"). Planning fixes this: build a step-by-step plan
before doing any work and keep it in context throughout -- the same job
Claude Code's to-do list does.

CrewAI gives you two distinct knobs:

* planning=True on the Crew -- a high-level roadmap for the overall task,
  generated before execution and kept available as the task progresses.
* reasoning=True on an Agent -- the agent reflects on its own approach,
  drafts an execution plan, refines it (up to max_reasoning_attempts),
  and injects the final plan into the task before acting.

Run:  ANTHROPIC_API_KEY=... python 04_planning.py
"""

from crewai import LLM, Agent, Crew, Task
from crewai_tools import DirectoryReadTool, FileReadTool

from config import CREWAI_MODEL, WORKSPACE_DIR

llm = LLM(model=CREWAI_MODEL)

bug_fixer = Agent(
    role="Bug Fixer",
    goal="Find and describe the fix for the reported bug in the codebase.",
    backstory="You read directories and files to build an accurate picture of the code.",
    tools=[FileReadTool(), DirectoryReadTool(directory=WORKSPACE_DIR)],
    llm=llm,
    reasoning=True,
    max_reasoning_attempts=3,  # optional: cap the plan-refinement loop
)

task = Task(
    description=(
        f"In the working directory {WORKSPACE_DIR}, find the fix for {{objective}}. "
        "Read the code and the tests before concluding."
    ),
    expected_output="A short description of each bug and the exact fix, per file.",
    agent=bug_fixer,
)

crew = Crew(
    agents=[bug_fixer],
    tasks=[task],
    planning=True,
    # CrewAI defaults to gpt-4o-mini for the planning step; pin it to Claude.
    planning_llm=llm,
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"objective": "the failing tests in account.py"})
    print(result)
