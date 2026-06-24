# Prompts I've Used — HW5 AirLLM Evaluation Pipeline

This file logs every prompt submitted to an AI agent during the development of HW5.
Each entry records the date, the target agent, and the verbatim prompt text.

---

## Session 1 — 2026-06-22 — Initial Architecture & Documentation Sprint

### Prompt 1 — Project Kickoff & Full Pipeline Design

**Agent:** Claude Sonnet 4.6 (Claude Code)
**Date:** 2026-06-22
**Purpose:** Define the full evaluation pipeline architecture, generate PRD, PLAN, and TODO

**Verbatim Prompt:**
```
today we are working on assignment 5, the assignment is "Assignment 5 (HW5) focuses on
running exceptionally large language models (LLMs) in a local environment using AirLLM.
The assignment is based on the concepts covered in Lecture 08.
To successfully complete the assignment, you must perform the following tasks:
Model and Hardware Setup: You must choose and download a large LLM tailored to your
computer and document your specific hardware specifications.
Comparative Execution: You need to attempt to run the model directly on your regular
processor (CPU or GPU) and document the outcome. Following this, you must run the model
again using AirLLM and perform an in-depth analysis comparing the two executions.
Quantization: You are specifically required to apply a quantizer and demonstrate its
impact on the model.
AI Agent Orchestration: An essential part of the assignment is demonstrating your
ability to write the appropriate prompts for your AI agents to generate the necessary
code, specifically focusing on planning a modular architecture.
Detailed Report: You must write an in-depth report that extracts and explains the core
concepts from the lecture. Your report must include comparative metrics, graphs, and
original ideas for comparative experiments.
The guidelines emphasize that the provided instructions are only a baseline; to achieve
a grade of "excellence," you are expected to bring your own original thoughts, unique
interpretations, and creativity to the experiments and analysis"
I want you to follow the guidelines of this file
"AI-Agents-course\Course recources\software_submission_guidelines-V3.pdf"
and now let us start, you are a researcher and we are conducting a structured scientific
experiment comparing a baseline against different framework, I want you to build an
evaluation loop that switch configuration dynamically a 2 big model LLM from hugging
face with different sizes(leave it as something I can hook to the pipeline) and for the
2 we are going to try 2 frameworks standard ollama and AirLLM and for each one will try
different quantization first Q4 then Q8 and then Q2. make an OS page monitoring hooks
to hook into system diagnostics and to log CPU, RAM swapping and of course we want to
record Vram allocation spikes. in the end of the pipeline we want to plot the trade offs
data with colors and 3-4 sentences summary. I want this prompt to be added to file
named prompt Ive used. write a prd file then a plan file focusing on the pipelines and
write a todo list with 800 todo and make sure it is relevant to the plan
```

**What this prompt produced:**
- `docs/PRD.md` — Full product requirements document
- `docs/PLAN.md` — Modular pipeline architecture plan
- `docs/TODO.md` — 800-item task list mapped to the plan
- `prompts_ive_used.md` — This file

---

## Session 2 — TBD — Code Generation Phase

*(Prompts will be appended here as implementation proceeds)*

---

## Prompt Design Notes

The above prompt follows the "Vibe Coding" orchestration pattern described in the
submission guidelines (v3.00, §1.4): the human architect defines requirements clearly
and delegates code generation to AI agents. Key design decisions in the prompt:

1. **Hook-based model registry** — models are left as injectable so the pipeline can
   run on any hardware without code changes.
2. **2×2×3 evaluation matrix** — two models × two frameworks × three quantization
   levels = 12 experimental cells, enabling rigorous comparative analysis.
3. **OS-level monitoring** — the prompt explicitly requests system-call-level hooks
   (CPU, RAM swap, VRAM spikes) rather than application-level metrics alone.
4. **Scientific framing** — framing as "baseline vs. framework" ensures the code
   produces reproducible, publication-quality results with statistical validity.
5. **Plot + summary** — requiring both a visualization and a textual 3-4 sentence
   summary forces the pipeline to synthesize findings, not just dump numbers.
