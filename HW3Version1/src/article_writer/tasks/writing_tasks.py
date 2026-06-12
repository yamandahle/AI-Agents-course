"""Writing task factories — defines the 5-task writing pipeline."""
from __future__ import annotations

from crewai import Agent, Task


def make_context_load_task(writer: Agent, artifact_task: Task) -> Task:
    return Task(
        description=(
            "Load all context files:\n"
            "1. data/guideline.md — WHAT to write\n"
            "2. data/research.md — WHAT facts to use\n"
            "3. profiles/Structure.md, Terminology.md, Characters.md — HOW to write\n"
            "4. All files in few_shot_examples/ — example output\n"
            "Combine into a single unified writer context string."
        ),
        expected_output="Unified writer context string with 4 labeled sections.",
        agent=writer,
        context=[artifact_task],
    )


def make_draft_generation_task(writer: Agent, context_task: Task) -> Task:
    return Task(
        description=(
            "Generate a complete LaTeX article draft of at least 15 pages.\n"
            "Required elements:\n"
            "- Cover page (topic, author, date, course, lecturer)\n"
            "- Linked table of contents\n"
            "- ≥5 numbered sections\n"
            "- ≥1 image with caption\n"
            "- ≥1 Python-generated graph (PDF inclusion)\n"
            "- ≥1 table using booktabs\n"
            "- ≥1 equation in \\begin{equation} environment\n"
            "- ≥1 Hebrew-English BiDi chapter (polyglossia)\n"
            "- Bibliography with all research.md sources\n"
            "Save output to results/draft_v1.tex."
        ),
        expected_output="results/draft_v1.tex — complete LaTeX source, compilable with lualatex.",
        agent=writer,
        context=[context_task],
    )


def make_evaluation_task(evaluator: Agent, draft_task: Task) -> Task:
    return Task(
        description=(
            "Evaluate the draft on 5 dimensions (1-10 each):\n"
            "- Coverage (25%): all guideline key points addressed?\n"
            "- Accuracy (25%): all claims cited from research.md?\n"
            "- Style (20%): matches profiles/Characters.md?\n"
            "- Structure (20%): follows profiles/Structure.md?\n"
            "- Citation Quality (10%): IEEE format, no dead links?\n"
            "Write critique to results/critique_v1.md with specific improvement points."
        ),
        expected_output="JSON scores + results/critique_v1.md with actionable improvement list.",
        agent=evaluator,
        context=[draft_task],
    )


def make_optimization_task(writer: Agent, eval_task: Task) -> Task:
    return Task(
        description=(
            "Apply ALL critique points from the critique file to the current draft.\n"
            "- Do not remove sections that were not critiqued.\n"
            "- Do not shrink below 15 pages.\n"
            "- Save revised draft to results/draft_v{N+1}.tex."
        ),
        expected_output="Revised LaTeX draft saved with incremented version number.",
        agent=writer,
        context=[eval_task],
    )


def make_compilation_task(writer: Agent, opt_task: Task) -> Task:
    return Task(
        description=(
            "Compile the final LaTeX draft to PDF using lualatex (4 passes).\n"
            "Run biber between pass 1 and 2 for bibliography.\n"
            "Verify compiled PDF has ≥15 pages.\n"
            "Save as results/article_final.pdf."
        ),
        expected_output="results/article_final.pdf — verified ≥15 pages.",
        agent=writer,
        context=[opt_task],
    )
