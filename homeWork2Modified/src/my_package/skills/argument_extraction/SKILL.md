---
name: argument_extraction
description: Extracts the core argument from a response by analyzing structural markers. Use when an agent receives an opponent's response or when the judge builds a debate summary.
---

# Argument Extraction Skill

This skill allows agents and judges to isolate the primary claim from a multi-paragraph response. It ensures that the debate remains focused on the actual points being made rather than conversational fluff.

## How It Works

1.  **Paragraph Segmentation**: The input text is split into distinct paragraphs.
2.  **Sentence Analysis**: For each paragraph, the skill examines the **first sentence** (typically the topic sentence) and the **last sentence** (typically the concluding or transitioning sentence).
3.  **Core Identification**: It filters these sentences for argumentative keywords and stance-bearing language.
4.  **Consistency Check**: It compares the extracted sentences against the agent's known stance to ensure the main argument has not shifted.
5.  **Output**: Returns a concise summary of the main argument.

## Workflow

- **Trigger**: "Extract the main argument", "What is the opponent's core point?", "Summarize the debate arguments".
- **Action**: Analyze the structural positions of sentences to determine the thesis of the response.
