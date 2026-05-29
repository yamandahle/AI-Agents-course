---
name: relevance_check
description: Validates the logical link between an example and a main argument. Use when a debater looks for gaps in an opponent's argument or when the judge determines a winner.
---

# Relevance Check Skill

This skill assesses whether a provided example or evidence actually supports the main argument through a valid chain of reasoning. It is critical for identifying logical fallacies or weak points in a debate.

## How It Works

1.  **Argument Identification**: Identifies the main argument using the Argument Extraction skill.
2.  **Example Mapping**: Isolates the specific examples or data points provided in the response.
3.  **Reasoning Path Analysis**: Checks for "bridge words" and explanatory phrases that connect the example to the point (e.g., "therefore", "consequently", "this demonstrates", "leads to", "illustrates that").
4.  **Validity Check**: If the reasoning path clearly leads from the example to the main argument, the example is marked as **Valid**.
5.  **Gap Detection**: If the reasoning is missing or non-sequitur, it flags a "Logical Gap" for the agent to exploit.

## Core Process

- **Reasoning Keywords**: Always look for words like *because*, *as a result*, *this implies*, *the rationale being*, *foundationally*, *which effectively means*.
- **Validation**: An example is only as good as the reasoning that gets it to the point.
