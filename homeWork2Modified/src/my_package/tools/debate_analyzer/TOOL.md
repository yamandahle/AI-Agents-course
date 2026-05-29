---
name: debate_analyzer
description: Analyzes debate turns, provides judicial commentary, and generates a structured results.md file. Use exclusively by the JudgeAgent after receiving a response.
---

# Debate Analyzer Tool

The Debate Analyzer is a specialized tool for the JudgeAgent to process debate flow, evaluate arguments against a framework, and document the session's analytical trajectory.

## How It Works

1.  **Response Capture**: Receives the raw content from a debater (Speaker).
2.  **Circular Point Extraction**: Identifies the main points and supporting data using the `argument_extraction` and `relevance_check` skills.
3.  **Judicial Evaluation**: The Judge generates an "Analytic" piece for the response, assessing strengths, weaknesses, and potential openings for the opponent.
4.  **Flow Documentation**: Appends the analysis to the chronological session flow.
5.  **Final Resolution**: After the debate ends, it weighs the competing clashes (e.g., Mental Health vs. Autonomy) to determine the winner.
6.  **Report Generation**: Writes or updates the `results.md` file using the mandatory structured template.

## Results.md Structure

The tool enforces the following structure:
- **Debate Session Analytics**: Topic, Framework, and Verdict.
- **Chronological Session Flow**: Speaker points followed by Judge Analytics for every turn.
- **Final Round Resolution**: Impact weighing matrix and the final ballot reasoning.

## Usage

- **Trigger**: Called by the JudgeAgent after every debater turn and at the end of the session.
- **Input**: Debater name, content, current turn number, and session history.
- **Output**: Updated internal state and a formatted entry in `results/results.md`.
