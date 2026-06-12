"""Generates data/guideline.md from a raw topic string using an LLM."""
from __future__ import annotations

from pathlib import Path

from article_writer.shared.constants import DEFAULT_ENCODING, GUIDELINE_PATH
from article_writer.shared.llm_client import LLMClient
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)

_SYSTEM = (
    "You are an academic article planning expert. "
    "Your job is to take a raw topic and produce a complete, detailed article guideline "
    "in structured Markdown format."
)

_USER_TEMPLATE = """\
Generate a complete article guideline for a 15-page academic article on the following topic.

TOPIC: {topic}

The guideline MUST follow this exact Markdown structure:

# Article Guideline — {topic}

## Topic
[2-3 sentences describing the specific subject of the article, its scope, and why it matters.]

## Angle
[1-2 sentences describing the specific argument or perspective this article takes — not just\
 a summary but an analytical stance.]

## Key Points
[Exactly 8 bullet points. Each must be a concrete, researchable claim or sub-topic the\
 article will address. Use this format:]
- Key Point 1: ...
- Key Point 2: ...
- Key Point 3: ...
- Key Point 4: ...
- Key Point 5: ...
- Key Point 6: ...
- Key Point 7: ...
- Key Point 8: ...

## Narrative Arc
[3-4 sentences describing how the article flows — what the introduction establishes, how\
 the body builds the argument, what the conclusion delivers.]

## Target Length
~15 pages (minimum)

## Language Requirements
- Primary language: Hebrew (RTL)
- At least one chapter demonstrating Hebrew-English BiDi switching
- Technical terms remain in English throughout

## Required Visual Elements
- Graph: [Describe a specific data comparison chart relevant to this topic]\
 (Python matplotlib → PDF)
- Table: [Describe a specific comparison or summary table relevant to this topic]
- Formula: [Describe a specific mathematical formula relevant to this topic]
- Image: [Describe a specific architecture diagram or figure relevant to this topic]

## Cover Page Information
- Author: Nagham Mansour
- Course: AI Agents — Advanced Topics
- Lecturer: Dr. Yoram Segal
- Date: June 2026

Return ONLY the Markdown content — no preamble, no explanation.
"""


class GuidelineGenerator:
    """Generates a structured article guideline from a plain-text topic."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    def generate(self, topic: str, output_path: str | Path = GUIDELINE_PATH) -> Path:
        """Call LLM to expand topic → guideline.md. Returns the written path."""
        logger.info("Generating guideline for topic: %s", topic)
        resp = self._llm.complete(
            system=_SYSTEM,
            user=_USER_TEMPLATE.format(topic=topic),
            step="guideline_generation",
            temperature=0.4,
            max_tokens=2048,
        )
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(resp.text.strip(), encoding=DEFAULT_ENCODING)
        logger.info("Guideline written to %s (%d chars)", out, len(resp.text))
        return out
