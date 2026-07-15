"""Step 2 -- The first CrewAI agent.

CrewAI provides the step-1 execution loop automatically the moment you
create an agent: you define WHO does the work (Agent), WHAT the assignment
is (Task), and a Crew ties them together. kickoff() runs the same
loop we hand-wrote in 01_core_loop.py.

Run:  ANTHROPIC_API_KEY=... python 02_first_agent.py
"""

from crewai import Agent, Crew, Task

from config import CREWAI_MODEL

bug_fixer = Agent(
    role="Bug Fixer",
    goal="Find and describe the fix for the reported bug in the codebase.",
    backstory="You read directories and files to build an accurate picture of the code.",
    llm=CREWAI_MODEL,
)

task = Task(
    description="Find the fix for {objective}.",
    expected_output="A short description of the fix and which file it belongs in.",
    agent=bug_fixer,
)

if __name__ == "__main__":
    result = Crew(agents=[bug_fixer], tasks=[task]).kickoff(
        inputs={"objective": "the overdraft bug in account.py"}
    )
    print(result)
