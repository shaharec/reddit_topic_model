"""Step 7 -- Memory and checkpointing.

By default an agent forgets everything when a run ends. Two mechanisms
carry information forward, and they solve different problems:

* memory=True     -- persistent memory ACROSS runs. After each task CrewAI
                     uses an LLM to extract useful facts from the output,
                     stores them, and injects relevant memories into future
                     task prompts. All agents in a crew share it unless an
                     agent is given its own.
* checkpoint=True -- a snapshot of progress WITHIN a workflow (config, task
                     state, memory, intermediate results, inputs, history),
                     taken whenever a task finishes, so an interrupted run
                     can resume from that point. Stored via JsonProvider
                     (one JSON file per checkpoint, easy to inspect) or
                     SqliteProvider (one DB, better under heavy load).
                     Crew, Flow, and Agent all accept `checkpoint`;
                     children inherit the parent's value unless they set
                     their own.

Run:  ANTHROPIC_API_KEY=... python 07_memory_checkpointing.py
"""

from crewai import Agent, Crew, LLM, Task
from crewai_tools import DirectoryReadTool, FileReadTool

from config import CREWAI_MODEL, WORKSPACE_DIR

llm = LLM(model=CREWAI_MODEL)

reviewer = Agent(
    role="Code Reviewer",
    goal="Review the codebase and record project conventions worth remembering.",
    backstory="You build up knowledge about a project across sessions.",
    tools=[FileReadTool(), DirectoryReadTool(directory=WORKSPACE_DIR)],
    llm=llm,
)

task = Task(
    description=(
        f"Review the code in {WORKSPACE_DIR}. Note the project's conventions "
        "and any standing rules (e.g. 'fix the implementation, never the tests') "
        "so future runs can rely on them. Then {objective}."
    ),
    expected_output="A review summary plus the facts worth remembering for next time.",
    agent=reviewer,
)

crew = Crew(
    agents=[reviewer],
    tasks=[task],
    memory=True,      # facts persist across separate kickoffs
    checkpoint=True,  # snapshots let an interrupted run resume
)

if __name__ == "__main__":
    # First run: learns the project. Run it again tomorrow and the stored
    # memories are retrieved and added to the task prompt automatically.
    result = crew.kickoff(inputs={"objective": "summarize what account.py does"})
    print(result)
