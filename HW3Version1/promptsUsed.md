# Prompts Used — HW3 Article-Writing Multi-Agent Network

## Session Date
2026-06-11

---

## Prompt 1 — Architecture Stage Kick-off

> we are going to build a full project I am the manager and you are a critical worker engineer, the project is to build a network that can write an article with length 15 pages with additional restrictions you can find them in file "\\wsl.localhost\Ubuntu\home\nagham1023\AI-Agents-course\HW3Version1\main-L06-summary-and-ex03-defination.pdf" and the project should build with instructions from this file "\\wsl.localhost\Ubuntu\home\nagham1023\AI-Agents-course\HW3Version1\software_submission_guidelines-V3.pdf" we are going to divide the work into 3 stages.
>
> The first stage is we are going to define the architecture we are going to use. So we need in addition to you 2 agents:
>
> **Researcher Agent** — who is exploratory (find information through various sources) and directed by human feedback: "search, read, pivot, search again."
>
> **Writer Agent** — who is deterministic, follows tone, structure, final edits with human feedback (human review in the end only): "draft, critique, edit, format"
>
> The two agents in the same project to share context.
>
> The first agent should behave as:
> 1. Read human-written article guideline to understand the topic to research
> 2. Iteratively do web searches to learn more about the topic and gather material, following user feedback after each batch of web searches
> 3. Revise all the gathered content — do not skip any content, do not keep any untrustworthy content, keep only the most relevant.
> 4. Write all gathered content into a final artefact which will be used by the writer agent.
>
> For web searches solution use Gemini or Perplexity — get precise answers to search queries with citations. We're going to use MCP server and use MCP tools to do the API calls. This is why you need to add tools such as deep research, researcher handler — and each tool should add prompt as the query.
>
> The writing flow will have 3 phases:
> - **Phase 1:** Load the context with 2 markdown files (guidelines, research) and another 2 files (profiles/ and few-shot examples).
> - **Phase 2:** Generate the initial draft.
> - **Phase 3:** Improve the post with evaluator-optimizer loop.
>
> The guideline is "what to write" — contains things like the Topic, angle, key points, and narrative arc — these in the .md file with the research.md file with LLM prompt will give us the draft.
>
> The writing profiles are the "how to write it" — will be static and configured and contains 3 Markdown files: Structure, Terminology, Characters — and these 3 will be injected into every prompt. So profiles with few-shot examples will go into the writer prompt that produces the draft.
>
> Prepare the PRD file and the PLAN file for what I explained and make a TODO file with 800 todos in the list and add this prompt to markdown file with name promptsUsed.

---

## Source Documents Referenced

| Document | Purpose |
|---|---|
| `main-L06-summary-and-ex03-defination.pdf` | Assignment definition, article content requirements, LaTeX workflow |
| `software_submission_guidelines-V3.pdf` | Code quality, project structure, SDK architecture, testing standards |

---

## Key Decisions Extracted from Prompt

| Decision | Detail |
|---|---|
| Framework | CrewAI (agent orchestration) |
| Search API | Gemini or Perplexity via MCP server |
| Context sharing | Both agents in the same CrewAI Crew, context passed via Task context chain |
| Researcher feedback | Human-in-the-loop after each search batch |
| Writer feedback | Human review at the end only |
| Writing phases | 3: Context Load → Draft Generation → Evaluator-Optimizer Loop |
| Writing profiles | Static MD files: Structure.md, Terminology.md, Characters.md |
| Few-shot examples | Injected into every writer prompt alongside profiles |
| Output format | LaTeX → PDF (LuaLaTeX / MiKTeX) |
| Article length | ~15 pages |

---

## Prompt 2 — Stage 3 Extension

> I updated the few-shot-examples with real pdf examples as they should so modify the project to adapt to this change. add the ability to change the model we use from configuration we work me and my partner she will use sonnet and ill use gemini model so make sure the .env example is adapting to this and the guideline you write it according to the few-shot-examples and add a README file for this project contains how to run it the directories and a full summary of how it works. now for the evaluation phase I need a 3-4 loops between the writer and reviewer and make sure they keep each version in a file with the version name in the results file and final will have final version and also in the results file and make sure the 2 agents has separate context the review only can read the draft not the writer context!, how the review works, the input will be the current post and context: guideline+research+profiles(to check against) the output is review pydantic object the review model contains(profile(which constraint), location(where in the article), comment(what is wrong ~1-2 lines), and then the next step is applying the correctness which is how the edit works, the input: current post+ structured reviews, the context: guidlines+ research+ profiles+ few-shot- examples(same as the initial writer) the priority: guideline>research> profile violations, make a file and store all the traces every LLM/tool call with full I/O +metadata, make a file and save the latency and cost per-step timing, tokens,dollars. now let us build an eval dataset from scratch, extract 20 real articles with ~13-20 pages from MDPI do a reverse-Engineer(guidlines + research are the input) and generate this will be the output label the outputs with binary pass/fail + 3 sentence critique) then split it into train/dev/test then build the evaluator and then evaluate the evaluator! so repeat until converge (measure F1= precision * recall) Run the LLM judge on dev split compute F1 score adjust LLM judge prompt/examples and for final validation run on test split for final validation. make prd and plan files and then a todo list with 650 todos on the list, add this prompt to the used prompts file and execute the todo list

---

### Key Decisions Extracted from Prompt 2

| Decision | Detail |
|---|---|
| Few-shot format | Changed from `.md` to real MDPI PDFs (PyMuPDF/fitz extraction) |
| LLM provider switching | `LLM_PROVIDER` env var — `anthropic` (partner) or `google` (Nagham) |
| Reviewer context isolation | Reviewer sees ONLY draft + guideline + research + profiles — never few-shots |
| Review output type | `ArticleReview` Pydantic model with list of `ReviewComment(profile, location, comment)` |
| Editor priority | guideline violations > research violations > profile violations |
| Version tracking | `draft_v1.tex`, `review_v1.json`, ..., `draft_final.tex` in `results/` |
| Tracing | `traces.jsonl` — full I/O + metadata per LLM/tool call |
| Metrics | `metrics.jsonl` — latency_ms, tokens, cost_usd per step |
| Eval dataset | 20 MDPI articles (13–20 pages), labelled PASS/FAIL + 3-sentence critique |
| Eval splits | train/dev/test split saved as JSONL |
| Judge convergence | F1 on dev split (standard 2PR/(P+R)); refine prompt until F1 ≥ 0.80 |
| Final eval | Run winning judge on test split (held-out throughout refinement) |
