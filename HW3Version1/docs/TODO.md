# TODO — AI Article-Writing Multi-Agent Network (Revised)
**800-Item Critical Task List**

| Field | Value |
|---|---|
| Version | 1.01 |
| Date | 2026-06-11 |
| Total Tasks | 800 |

---

## STAGE 1 — Architecture & Documentation

### S1.A Planning Documents
- [x] 001. Write docs/PRD.md — Product Requirements Document
- [x] 002. Write docs/PLAN.md — Architecture & Planning Document
- [x] 003. Write docs/TODO.md — 800-item task list (this file)
- [x] 004. Write promptsUsed.md — User prompt log
- [ ] 005. Write docs/PRD_researcher_agent.md — per-mechanism PRD
- [ ] 006. Write docs/PRD_writer_agent.md — per-mechanism PRD
- [ ] 007. Write docs/PRD_mcp_tools.md — per-mechanism PRD
- [ ] 008. Write docs/PRD_latex_pipeline.md — per-mechanism PRD
- [ ] 009. Write docs/PRD_evaluator_optimizer.md — per-mechanism PRD
- [ ] 010. Manager review of all Stage 1 documents

### S1.B Skills — Structure & Documentation
- [ ] 011. Create skills/research/SKILL.md with YAML metadata + instructions + example + constraints
- [ ] 012. Create skills/writing/SKILL.md with YAML metadata + instructions + example + constraints
- [ ] 013. Create skills/catch-me-up/SKILL.md — triggered by "catch me up"
- [ ] 014. catch-me-up SKILL.md: explain project purpose in ≤5 sentences
- [ ] 015. catch-me-up SKILL.md: list current directory tree with one-line purpose per folder
- [ ] 016. catch-me-up SKILL.md: list all agents and their roles
- [ ] 017. catch-me-up SKILL.md: list all tools and their purposes
- [ ] 018. catch-me-up SKILL.md: state current stage and what is next
- [ ] 019. catch-me-up SKILL.md: constraint — output must fit on one terminal screen
- [ ] 020. catch-me-up SKILL.md: constraint — trigger phrase is exactly "catch me up"

### S1.C Tools — Documentation with Prompts
- [ ] 021. Document deep_research tool in tools.md: name, description, input schema, example prompt
- [ ] 022. Document researcher_handler tool in tools.md: name, description, input schema, example prompt
- [ ] 023. Document citation_extractor tool in tools.md: name, description, input schema, example prompt
- [ ] 024. Document content_filter tool in tools.md: name, description, input schema, example prompt
- [ ] 025. tools.md: add prompt template for each tool showing exact query structure
- [ ] 026. tools.md: add expected output format per tool
- [ ] 027. tools.md: add error handling notes per tool

### S1.D Summary Files
- [ ] 028. Create skills.md at project root — summarize all 3 skills with name + purpose
- [ ] 029. skills.md: table format with columns: Name, Trigger, Purpose, Example Phrase
- [ ] 030. skills.md: note which agent each skill is wired into
- [ ] 031. Create tools.md at project root — summarize all 4 tools with name + purpose
- [ ] 032. tools.md: table format with columns: Name, Agent, API Backend, Query Param
- [ ] 033. tools.md: add sample prompt for each tool

---

## STAGE 2 — Implementation

### S2.A Project Bootstrap & Config
- [ ] 034. Create pyproject.toml with uv project settings
- [ ] 035. pyproject.toml: add crewai>=0.80.0 dependency
- [ ] 036. pyproject.toml: add crewai-tools>=0.14.0 dependency
- [ ] 037. pyproject.toml: add anthropic>=0.40.0 dependency
- [ ] 038. pyproject.toml: add google-generativeai>=0.8.0 dependency
- [ ] 039. pyproject.toml: add openai>=1.50.0 dependency (Perplexity uses OpenAI-compatible API)
- [ ] 040. pyproject.toml: add python-dotenv>=1.0.0 dependency
- [ ] 041. pyproject.toml: add mcp>=1.0.0 dependency
- [ ] 042. pyproject.toml: add ruff as dev dependency
- [ ] 043. pyproject.toml: add pytest, pytest-cov, pytest-asyncio as dev dependencies
- [ ] 044. pyproject.toml: configure ruff — target-version py310, line-length 88
- [ ] 045. pyproject.toml: configure pytest — testpaths=["tests"], asyncio_mode=auto
- [ ] 046. pyproject.toml: configure coverage — source=src/, threshold=85
- [ ] 047. Create .env-example with ANTHROPIC_API_KEY placeholder
- [ ] 048. Create .env-example with GEMINI_API_KEY placeholder
- [ ] 049. Create .env-example with PERPLEXITY_API_KEY placeholder
- [ ] 050. Create .gitignore — include .env, __pycache__, .venv, *.pyc, .ruff_cache
- [ ] 051. Create README.md — project overview
- [ ] 052. README.md: installation section (uv commands only)
- [ ] 053. README.md: usage section with example commands
- [ ] 054. README.md: architecture summary with agent descriptions
- [ ] 055. README.md: add ISO/IEC 25010 compliance note
- [ ] 056. Create config/setup.json version 1.00
- [ ] 057. config/setup.json: llm provider, model, temperature settings
- [ ] 058. config/setup.json: research backend, batch_size, max_batches, min_confidence
- [ ] 059. config/setup.json: writing max_evaluator_iterations, score_threshold, target_pages
- [ ] 060. config/setup.json: latex compiler and compile_passes
- [ ] 061. Create config/rate_limits.json version 1.00
- [ ] 062. config/rate_limits.json: gemini — 30 rpm, 500 rph, concurrent 3, retry 30s, max 3
- [ ] 063. config/rate_limits.json: perplexity — 20 rpm, 300 rph, concurrent 2, retry 30s, max 3
- [ ] 064. config/rate_limits.json: anthropic — 50 rpm, 1000 rph, concurrent 5, retry 10s, max 3
- [ ] 065. config/rate_limits.json: default — 30 rpm, 500 rph, concurrent 3, retry 30s, max 3

### S2.B Shared Infrastructure — Constants & Version
- [ ] 066. Create src/article_writer/__init__.py (empty, marks package)
- [ ] 067. Create src/article_writer/shared/__init__.py
- [ ] 068. Create src/article_writer/shared/constants.py
- [ ] 069. constants.py: CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW
- [ ] 070. constants.py: DEFAULT_ENCODING = "utf-8"
- [ ] 071. constants.py: RESEARCH_ARTIFACT_PATH = "data/research.md"
- [ ] 072. constants.py: GUIDELINE_PATH = "data/guideline.md"
- [ ] 073. constants.py: PROFILES_DIR = "profiles"
- [ ] 074. constants.py: FEW_SHOT_DIR = "few_shot_examples"
- [ ] 075. constants.py: RESULTS_DIR = "results"
- [ ] 076. constants.py: MAX_FILE_LINES = 150
- [ ] 077. constants.py: MIN_ARTICLE_PAGES = 15
- [ ] 078. Create src/article_writer/shared/version.py
- [ ] 079. version.py: get_version() reads from config/setup.json
- [ ] 080. version.py: fallback to "1.00" if config not found
- [ ] 081. Write test: constants.py — all symbols defined and non-empty
- [ ] 082. Write test: version.get_version() returns string in X.YY format

### S2.C Shared Infrastructure — Config Loader
- [ ] 083. Create src/article_writer/shared/config.py
- [ ] 084. config.py: LLMConfig dataclass (provider, model, temperature)
- [ ] 085. config.py: ResearchConfig dataclass (search_backend, fallback, batch_size, etc.)
- [ ] 086. config.py: WritingConfig dataclass (max_iter, score_threshold, target_pages)
- [ ] 087. config.py: LaTeXConfig dataclass (compiler, compile_passes)
- [ ] 088. config.py: AppConfig dataclass wrapping all sub-configs
- [ ] 089. config.py: load_config() with @lru_cache — singleton pattern
- [ ] 090. config.py: load_rate_limits() with @lru_cache
- [ ] 091. config.py: clear validation — raise KeyError with clear message on missing key
- [ ] 092. Write test: load_config() returns AppConfig with correct types
- [ ] 093. Write test: load_config() raises on missing required key
- [ ] 094. Write test: load_config() is cached (same object returned twice)
- [ ] 095. Write test: load_rate_limits() returns dict with service keys

### S2.D Shared Infrastructure — Logger
- [ ] 096. Create src/article_writer/shared/logger.py
- [ ] 097. logger.py: ArticleLogger class extending logging.Logger
- [ ] 098. logger.py: log_api_call(service, query, response_preview) method
- [ ] 099. logger.py: log_token_usage(service, input_tok, output_tok, cost_usd) method
- [ ] 100. logger.py: log_eval_score(iteration, scores) — appends to eval_log.json
- [ ] 101. logger.py: get_logger(name) factory — registers ArticleLogger class
- [ ] 102. logger.py: write to results/run_log.txt and stdout simultaneously
- [ ] 103. logger.py: create results/ directory if not exists
- [ ] 104. Write test: get_logger returns ArticleLogger instance
- [ ] 105. Write test: log_eval_score appends JSON entry to eval_log.json
- [ ] 106. Write test: log_api_call records service name in output

### S2.E Shared Infrastructure — API Gatekeeper
- [ ] 107. Create src/article_writer/shared/gatekeeper.py
- [ ] 108. gatekeeper.py: QueueStatus dataclass (queue_depth, active_calls)
- [ ] 109. gatekeeper.py: _ServiceState dataclass (rpm_calls deque, rph_calls deque, active int)
- [ ] 110. gatekeeper.py: ApiGatekeeper class
- [ ] 111. ApiGatekeeper.__init__: load rate limits from config
- [ ] 112. ApiGatekeeper._get_limits: look up service, fall back to "default"
- [ ] 113. ApiGatekeeper._get_state: lazy-init _ServiceState per service
- [ ] 114. ApiGatekeeper._check_rate_limit: purge expired window entries, return wait seconds
- [ ] 115. ApiGatekeeper.execute(service, api_call, *args, **kwargs): full flow
- [ ] 116. execute: check rate limit → sleep if needed
- [ ] 117. execute: increment active counter, record timestamps
- [ ] 118. execute: retry loop up to max_retries
- [ ] 119. execute: log each call via ArticleLogger
- [ ] 120. execute: decrement active counter in finally block
- [ ] 121. execute: raise RuntimeError after all retries exhausted
- [ ] 122. ApiGatekeeper.get_queue_status: return QueueStatus
- [ ] 123. Write test: execute enforces requests_per_minute sliding window
- [ ] 124. Write test: execute retries on exception up to max_retries
- [ ] 125. Write test: execute raises after max_retries
- [ ] 126. Write test: execute reads limits from config (not hardcoded)
- [ ] 127. Write test: get_queue_status returns correct active count
- [ ] 128. Write test: concurrent_max is respected (mock sleep)

### S2.F MCP Layer — Gemini Client
- [ ] 129. Create src/article_writer/mcp/__init__.py
- [ ] 130. Create src/article_writer/mcp/gemini_client.py
- [ ] 131. GeminiClient.__init__: load GEMINI_API_KEY from .env
- [ ] 132. GeminiClient.__init__: configure genai with api_key
- [ ] 133. GeminiClient.__init__: set model to gemini-1.5-pro (deep research)
- [ ] 134. GeminiClient.__init__: set flash model to gemini-1.5-flash (citation)
- [ ] 135. GeminiClient.search(prompt): call API via gatekeeper.execute("gemini", ...)
- [ ] 136. GeminiClient.search: enable google_search_retrieval grounding tool
- [ ] 137. GeminiClient.search: extract answer text from response
- [ ] 138. GeminiClient.search: extract citations from grounding_metadata
- [ ] 139. GeminiClient.search: derive confidence from support_chunks
- [ ] 140. GeminiClient.search: return dict(answer, citations, confidence)
- [ ] 141. GeminiClient: raise clear ValueError when GEMINI_API_KEY is not set
- [ ] 142. GeminiClient: log token usage per call
- [ ] 143. Write test: GeminiClient.search calls gatekeeper not API directly
- [ ] 144. Write test: GeminiClient raises ValueError on missing API key
- [ ] 145. Write test: GeminiClient parses citations from mock response

### S2.G MCP Layer — Perplexity Client
- [ ] 146. Create src/article_writer/mcp/perplexity_client.py
- [ ] 147. PerplexityClient.__init__: load PERPLEXITY_API_KEY from .env
- [ ] 148. PerplexityClient.__init__: configure openai.OpenAI with base_url + api_key
- [ ] 149. PerplexityClient.__init__: set model to sonar-pro
- [ ] 150. PerplexityClient.search(prompt): call chat.completions.create via gatekeeper
- [ ] 151. PerplexityClient.search: extract content from response.choices[0].message.content
- [ ] 152. PerplexityClient.search: extract citations from response.citations if present
- [ ] 153. PerplexityClient.search: return dict(answer, citations, confidence="MEDIUM")
- [ ] 154. PerplexityClient: raise ValueError when PERPLEXITY_API_KEY is not set
- [ ] 155. PerplexityClient: log token usage per call
- [ ] 156. Write test: PerplexityClient.search calls gatekeeper
- [ ] 157. Write test: PerplexityClient extracts citations from mock response
- [ ] 158. Write test: PerplexityClient raises ValueError on missing key

### S2.H MCP Layer — MCP Server
- [ ] 159. Create src/article_writer/mcp/mcp_server.py
- [ ] 160. mcp_server.py: import mcp.server, mcp.types
- [ ] 161. mcp_server.py: create Server("article-writer-research-server")
- [ ] 162. mcp_server.py: register list_tools handler — return all 4 tool schemas
- [ ] 163. deep_research schema: inputSchema requires "prompt" (string)
- [ ] 164. researcher_handler schema: inputSchema requires "prompt" (string)
- [ ] 165. citation_extractor schema: inputSchema requires "prompt" (string — URL or text)
- [ ] 166. content_filter schema: inputSchema requires "prompt" (string — content + topic)
- [ ] 167. mcp_server.py: register call_tool handler — dispatch to correct client
- [ ] 168. mcp_server.py: main() async — run with stdio_server transport
- [ ] 169. mcp_server.py: entrypoint if __name__ == "__main__"
- [ ] 170. Write test: all 4 tools are registered with correct names
- [ ] 171. Write test: each tool schema has "prompt" in required fields

### S2.I Tools Layer — Base Tool
- [ ] 172. Create src/article_writer/tools/__init__.py
- [ ] 173. Create src/article_writer/tools/base_tool.py
- [ ] 174. ArticleBaseTool(BaseTool) mixin with shared behavior
- [ ] 175. ArticleBaseTool._sanitize_input: strip HTML tags, truncate to 4000 chars
- [ ] 176. ArticleBaseTool._log_call: log tool name + sanitized input via logger
- [ ] 177. ArticleBaseTool._format_markdown_output: ensure output starts with ## header
- [ ] 178. All concrete tools must call _sanitize_input before processing
- [ ] 179. All concrete tools must call _log_call at entry
- [ ] 180. Write test: _sanitize_input strips <script> tags
- [ ] 181. Write test: _sanitize_input truncates to 4000 chars
- [ ] 182. Write test: _log_call records tool name

### S2.J Tools Layer — deep_research
- [ ] 183. Create src/article_writer/tools/deep_research_tool.py
- [ ] 184. DeepResearchTool(ArticleBaseTool)
- [ ] 185. name = "deep_research"
- [ ] 186. description = "Search the web for factual information on a topic. Input: a research query as plain text. Returns: answer with citations and confidence level."
- [ ] 187. _run(prompt: str) — sanitize input
- [ ] 188. _run: call GeminiClient.search(prompt) via gatekeeper
- [ ] 189. _run: on Gemini failure, fall back to PerplexityClient.search(prompt)
- [ ] 190. _run: format output as: "## Answer\n...\n## Citations\n- [title](url)"
- [ ] 191. _run: include confidence tag: "**Confidence:** HIGH|MEDIUM"
- [ ] 192. _run: discard result if confidence is LOW (return empty string)
- [ ] 193. Prompt template (stored in class): "Search for: {prompt}. Provide factual answer with citations."
- [ ] 194. Write test: _run returns markdown with ## Answer and ## Citations sections
- [ ] 195. Write test: _run falls back to Perplexity when Gemini raises
- [ ] 196. Write test: _run returns empty string on LOW confidence
- [ ] 197. Write test: _run sanitizes HTML in search results

### S2.K Tools Layer — researcher_handler
- [ ] 198. Create src/article_writer/tools/researcher_handler.py
- [ ] 199. ResearchSession dataclass: visited_urls (set), previous_queries (list), batch_count (int)
- [ ] 200. ResearcherHandlerTool(ArticleBaseTool)
- [ ] 201. name = "researcher_handler"
- [ ] 202. description = "Manages a multi-turn research session. Tracks visited URLs and previous queries to avoid repetition. Input: current research intent as plain text. Returns: suggested new queries and session summary."
- [ ] 203. _run(prompt: str) — sanitize input
- [ ] 204. _run: initialize session if first call
- [ ] 205. _run: extract URLs from prompt, add to visited_urls set
- [ ] 206. _run: generate next 3 query suggestions (call LLM via gatekeeper, avoid repeats)
- [ ] 207. _run: increment batch_count
- [ ] 208. _run: return JSON: {"batch": N, "new_queries": [...], "summary": "..."}
- [ ] 209. reset_session(): clear ResearchSession state
- [ ] 210. Prompt template: "Given research intent: {prompt}. Previously searched: {previous_queries}. Suggest 3 new angles not yet covered."
- [ ] 211. Write test: _run increments batch_count
- [ ] 212. Write test: _run avoids suggesting previous_queries
- [ ] 213. Write test: reset_session clears all state
- [ ] 214. Write test: _run output is valid JSON

### S2.L Tools Layer — citation_extractor
- [ ] 215. Create src/article_writer/tools/citation_extractor.py
- [ ] 216. CitationExtractorTool(ArticleBaseTool)
- [ ] 217. name = "citation_extractor"
- [ ] 218. description = "Extracts and formats a citation from a URL or raw text. Input: a URL or raw text passage containing source information. Returns: formatted markdown citation [Title](url) with author and date."
- [ ] 219. _run(prompt: str) — sanitize input
- [ ] 220. _run: detect if input is URL (startswith http)
- [ ] 221. _run if URL: call LLM to extract title, author, date from URL metadata
- [ ] 222. _run if text: parse author, title, publication from text via LLM
- [ ] 223. _run: return "[{title}]({url}) — {author}, {date}"
- [ ] 224. _run: handle malformed URLs with fallback plain-text citation
- [ ] 225. Prompt template (URL): "Extract citation metadata from this URL: {prompt}. Return JSON: {title, author, date, url}"
- [ ] 226. Prompt template (text): "Extract citation from this passage: {prompt}. Return JSON: {title, author, date, publication}"
- [ ] 227. Write test: _run detects URL vs plain text
- [ ] 228. Write test: _run formats markdown citation correctly
- [ ] 229. Write test: _run handles malformed URL without crashing

### S2.M Tools Layer — content_filter
- [ ] 230. Create src/article_writer/tools/content_filter.py
- [ ] 231. ContentFilterResult dataclass: keep (bool), confidence (str), reason (str)
- [ ] 232. ContentFilterTool(ArticleBaseTool)
- [ ] 233. name = "content_filter"
- [ ] 234. description = "Evaluates a content chunk for relevance and trustworthiness. Input: content chunk concatenated with ' | Topic: <topic>'. Returns: keep decision with confidence (HIGH/MEDIUM/LOW) and reason."
- [ ] 235. _run(prompt: str) — sanitize input
- [ ] 236. _run: split on " | Topic: " to get content and topic
- [ ] 237. _run: call Claude Haiku via gatekeeper with evaluation prompt
- [ ] 238. _run: parse LLM JSON response into ContentFilterResult
- [ ] 239. _run: return "KEEP:{confidence}:{reason}" or "DISCARD:{reason}"
- [ ] 240. Prompt template: "You are a fact-checker. Rate this content chunk for relevance to '{topic}' and trustworthiness. Content: {content}. Reply JSON: {keep: bool, confidence: HIGH|MEDIUM|LOW, reason: str}"
- [ ] 241. Write test: _run returns KEEP for authoritative academic source
- [ ] 242. Write test: _run returns DISCARD for social media speculation
- [ ] 243. Write test: _run handles LLM returning malformed JSON

### S2.N Agents Layer — Base Agent Mixin
- [ ] 244. Create src/article_writer/agents/__init__.py
- [ ] 245. Create src/article_writer/agents/base_agent.py
- [ ] 246. BaseAgentMixin class (not a CrewAI Agent — a Python mixin)
- [ ] 247. BaseAgentMixin._load_skills(skills_dir: str) -> str: read all SKILL.md files in dir
- [ ] 248. BaseAgentMixin._load_skills: concatenate skill contents as system context
- [ ] 249. BaseAgentMixin._log_task_start(task_name: str): log to ArticleLogger
- [ ] 250. BaseAgentMixin._log_task_end(task_name: str, result_preview: str): log to ArticleLogger
- [ ] 251. BaseAgentMixin.build_backstory(base: str, skills_dir: str) -> str: append skills to backstory
- [ ] 252. Write test: _load_skills reads SKILL.md files from directory
- [ ] 253. Write test: _load_skills returns empty string if directory missing
- [ ] 254. Write test: build_backstory appends skill content

### S2.O Agents Layer — Researcher Agent
- [ ] 255. Create src/article_writer/agents/researcher_agent.py
- [ ] 256. build_researcher_agent() factory function returning crewai.Agent
- [ ] 257. role = "Expert Research Analyst"
- [ ] 258. goal = "Gather comprehensive, verified, cited material on the article topic. Never skip content. Discard only untrustworthy items."
- [ ] 259. backstory: append skills/research/SKILL.md content via BaseAgentMixin
- [ ] 260. tools: [DeepResearchTool(), ResearcherHandlerTool(), CitationExtractorTool(), ContentFilterTool()]
- [ ] 261. allow_delegation=False
- [ ] 262. verbose=True
- [ ] 263. max_iter: read from config research.max_batches
- [ ] 264. Write test: build_researcher_agent() returns Agent instance
- [ ] 265. Write test: researcher agent has exactly 4 tools
- [ ] 266. Write test: researcher agent allow_delegation is False

### S2.P Agents Layer — Writer Agent & Evaluator
- [ ] 267. Create src/article_writer/agents/writer_agent.py
- [ ] 268. build_writer_agent() factory function returning crewai.Agent
- [ ] 269. role = "Senior Technical Article Writer"
- [ ] 270. goal = "Produce a polished 15-page LaTeX article from research material following all writing profiles exactly."
- [ ] 271. backstory: append skills/writing/SKILL.md content via BaseAgentMixin
- [ ] 272. tools = [] (writer uses only context, no external tools)
- [ ] 273. allow_delegation=True
- [ ] 274. verbose=True
- [ ] 275. build_evaluator_agent() factory function — evaluator sub-agent
- [ ] 276. evaluator role = "Article Quality Evaluator"
- [ ] 277. evaluator goal = "Score the draft on 5 dimensions (1–10) and produce actionable critique in structured format."
- [ ] 278. evaluator backstory: structured critic, returns JSON scores
- [ ] 279. evaluator tools = []
- [ ] 280. Write test: build_writer_agent() returns Agent with empty tools
- [ ] 281. Write test: build_evaluator_agent() returns Agent
- [ ] 282. Write test: writer agent allow_delegation is True

### S2.Q Tasks Layer — Research Tasks
- [ ] 283. Create src/article_writer/tasks/__init__.py
- [ ] 284. Create src/article_writer/tasks/research_tasks.py
- [ ] 285. make_research_batch_task(researcher, topic): Task
- [ ] 286. research_batch_task.description: "Search for material on '{topic}'. Use researcher_handler to plan 5 queries. For each query use deep_research. Extract citations with citation_extractor. Filter with content_filter."
- [ ] 287. research_batch_task.expected_output: "Markdown list of facts with inline [source](url) citations and confidence level."
- [ ] 288. research_batch_task: human_input=True (pause for feedback)
- [ ] 289. make_research_filter_task(researcher, batch_task): Task
- [ ] 290. research_filter_task.description: "Review all gathered content. Remove duplicates and LOW confidence items. Keep only HIGH and MEDIUM confidence facts."
- [ ] 291. research_filter_task.context = [batch_task]
- [ ] 292. make_research_artifact_task(researcher, filter_task): Task
- [ ] 293. research_artifact_task.description: "Write all curated facts to data/research.md. Include a section per research dimension. Each fact on its own bullet with citation."
- [ ] 294. research_artifact_task.expected_output: "Completed data/research.md file path."
- [ ] 295. research_artifact_task.context = [filter_task]
- [ ] 296. Write test: research_batch_task.human_input is True
- [ ] 297. Write test: research_artifact_task has correct context chain

### S2.R Tasks Layer — Writing Tasks
- [ ] 298. Create src/article_writer/tasks/writing_tasks.py
- [ ] 299. make_context_load_task(writer, artifact_task): Task
- [ ] 300. context_load_task.description: "Load guideline.md, research.md, profiles/Structure.md, profiles/Terminology.md, profiles/Characters.md, and all few_shot_examples/. Combine into unified writer context."
- [ ] 301. context_load_task.expected_output: "Unified context string ready for draft generation."
- [ ] 302. context_load_task.context = [artifact_task]
- [ ] 303. make_draft_generation_task(writer, context_task): Task
- [ ] 304. draft_generation_task.description: "Using the unified context, generate a complete LaTeX article draft of at least 15 pages. Include cover page, TOC, all required elements (image, graph, table, formula, BiDi chapter), and bibliography."
- [ ] 305. draft_generation_task.expected_output: "LaTeX source saved to results/draft_v1.tex, fully compilable with lualatex."
- [ ] 306. draft_generation_task.context = [context_task]
- [ ] 307. make_evaluation_task(evaluator, draft_task): Task
- [ ] 308. evaluation_task.description: "Evaluate the draft on 5 dimensions (coverage 25%, accuracy 25%, style 20%, structure 20%, citation quality 10%). Score each 1–10. Write structured critique to results/critique_v1.md."
- [ ] 309. evaluation_task.expected_output: "JSON scores + critique_v1.md file with specific improvement actions."
- [ ] 310. evaluation_task.context = [draft_task]
- [ ] 311. make_optimization_task(writer, eval_task): Task
- [ ] 312. optimization_task.description: "Apply all critique points from critique.md to the current draft. Revise LaTeX source. Increment version number."
- [ ] 313. optimization_task.context = [eval_task]
- [ ] 314. make_compilation_task(writer, opt_task): Task
- [ ] 315. compilation_task.description: "Compile the final LaTeX source to PDF using lualatex (4 passes). Verify page count >= 15."
- [ ] 316. compilation_task.expected_output: "results/article_final.pdf — verified ≥15 pages."
- [ ] 317. Write test: all tasks have non-empty description and expected_output
- [ ] 318. Write test: context chain is correct for each task

### S2.S Writing Pipeline — Context Loader
- [ ] 319. Create src/article_writer/writing/__init__.py
- [ ] 320. Create src/article_writer/writing/context_loader.py
- [ ] 321. ContextLoader class
- [ ] 322. load_guideline(path): read file, raise FileNotFoundError if missing
- [ ] 323. load_research(path): read file, raise FileNotFoundError if missing
- [ ] 324. load_profiles(profiles_dir): read Structure.md, Terminology.md, Characters.md
- [ ] 325. load_few_shots(few_shot_dir): read all .md files in directory
- [ ] 326. build_writer_context(): combine all loaded content
- [ ] 327. build_writer_context: prepend profiles as "## WRITING PROFILES (HOW TO WRITE)"
- [ ] 328. build_writer_context: append few-shots as "## FEW-SHOT EXAMPLES"
- [ ] 329. build_writer_context: append guideline as "## ARTICLE GUIDELINE (WHAT TO WRITE)"
- [ ] 330. build_writer_context: append research as "## RESEARCH MATERIAL"
- [ ] 331. log file names and sizes as each is loaded
- [ ] 332. Verify context_loader.py <= 150 lines
- [ ] 333. Write test: loads all 3 profile files
- [ ] 334. Write test: raises FileNotFoundError on missing guideline.md
- [ ] 335. Write test: output contains all 4 section headers
- [ ] 336. Write test: profiles appear before guideline in output

### S2.T Writing Pipeline — Draft Generator
- [ ] 337. Create src/article_writer/writing/draft_generator.py
- [ ] 338. DraftGenerator class
- [ ] 339. __init__(context: str, config: AppConfig): store context and config
- [ ] 340. generate() -> Path: call Anthropic API via gatekeeper
- [ ] 341. generate: build system prompt = profiles + LaTeX requirements
- [ ] 342. generate: user prompt = "Write a LaTeX article based on this research: {context}"
- [ ] 343. generate: request complete LaTeX with preamble, cover, TOC, body, bibliography
- [ ] 344. generate: validate output contains \begin{document} and \end{document}
- [ ] 345. generate: validate output contains \maketitle and \tableofcontents
- [ ] 346. generate: save to results/draft_v1.tex
- [ ] 347. generate: log token usage
- [ ] 348. Verify draft_generator.py <= 150 lines
- [ ] 349. Write test: generate() saves file to results/draft_v1.tex
- [ ] 350. Write test: output fails validation if \begin{document} missing
- [ ] 351. Write test: token usage is logged

### S2.U Writing Pipeline — Evaluator
- [ ] 352. Create src/article_writer/writing/evaluator.py
- [ ] 353. EvaluationScore dataclass: coverage, accuracy, style, structure, citation_quality, weighted_score
- [ ] 354. Evaluator class
- [ ] 355. __init__(guideline_path, research_path): load reference documents
- [ ] 356. evaluate(draft_path, iteration): read draft .tex
- [ ] 357. evaluate: build prompt with 5-dimension rubric (weights specified)
- [ ] 358. evaluate: call LLM via gatekeeper
- [ ] 359. evaluate: parse JSON response into EvaluationScore
- [ ] 360. evaluate: compute weighted_score = sum(score * weight for each dimension)
- [ ] 361. evaluate: write critique to results/critique_v{iteration}.md
- [ ] 362. evaluate: call logger.log_eval_score(iteration, scores)
- [ ] 363. Evaluation prompt template: "Score this LaTeX article draft on 5 dimensions 1-10. Coverage=25%, Accuracy=25%, Style=20%, Structure=20%, Citations=10%. Return JSON: {coverage, accuracy, style, structure, citation_quality, critique_points: [...]}"
- [ ] 364. Verify evaluator.py <= 150 lines
- [ ] 365. Write test: weighted_score computation is correct
- [ ] 366. Write test: critique is written to correctly named file
- [ ] 367. Write test: eval_log.json is updated

### S2.V Writing Pipeline — Optimizer
- [ ] 368. Create src/article_writer/writing/optimizer.py
- [ ] 369. Optimizer class
- [ ] 370. __init__(iteration: int): track current version
- [ ] 371. optimize(draft_path, critique_path) -> Path: read both files
- [ ] 372. optimize: build revision prompt: "Revise this LaTeX draft applying all critique points: {critique}"
- [ ] 373. optimize: call LLM via gatekeeper
- [ ] 374. optimize: validate output still contains required LaTeX structure
- [ ] 375. optimize: save to results/draft_v{iteration+1}.tex
- [ ] 376. optimize: log lines added/removed (diff count)
- [ ] 377. Revision prompt template: "You are editing a LaTeX article. Apply ALL of these critique points: {critique_points}. Original draft: {draft}. Return the complete revised LaTeX source."
- [ ] 378. Verify optimizer.py <= 150 lines
- [ ] 379. Write test: optimize() saves to correctly versioned path
- [ ] 380. Write test: optimize() validates LaTeX structure in output
- [ ] 381. Write test: diff size is logged

### S2.W Writing Pipeline — Loop Controller
- [ ] 382. Create src/article_writer/writing/loop_controller.py
- [ ] 383. EvalOptimizerLoop class
- [ ] 384. __init__(max_iterations, score_threshold, guideline_path, research_path)
- [ ] 385. run(initial_draft_path) -> Path: main loop
- [ ] 386. run: enforce minimum 2 iterations always
- [ ] 387. run: evaluate current draft
- [ ] 388. run: if iteration >= 2 AND score >= threshold: break
- [ ] 389. run: if iteration >= max_iterations: break
- [ ] 390. run: otherwise optimize and increment
- [ ] 391. run: log each iteration with score and threshold
- [ ] 392. run: return path to final draft .tex
- [ ] 393. Verify loop_controller.py <= 150 lines
- [ ] 394. Write test: loop enforces minimum 2 iterations
- [ ] 395. Write test: loop stops when score >= threshold (after min 2)
- [ ] 396. Write test: loop stops at max_iterations even below threshold
- [ ] 397. Write test: correct final path is returned

### S2.X LaTeX Layer — Templates
- [ ] 398. Create src/article_writer/latex/__init__.py
- [ ] 399. Create src/article_writer/latex/latex_templates.py
- [ ] 400. LUALATEX_PREAMBLE constant: full LaTeX preamble string
- [ ] 401. preamble: \documentclass{article} with geometry options
- [ ] 402. preamble: \usepackage{polyglossia} — Hebrew + English BiDi
- [ ] 403. preamble: \usepackage{fontspec} — Unicode font support
- [ ] 404. preamble: \usepackage{geometry} — margins
- [ ] 405. preamble: \usepackage[colorlinks]{hyperref} — linked TOC
- [ ] 406. preamble: \usepackage[backend=biber]{biblatex} — bibliography
- [ ] 407. preamble: \usepackage{tikz} — diagrams
- [ ] 408. preamble: \usepackage{graphicx} — images
- [ ] 409. preamble: \usepackage{booktabs} — tables
- [ ] 410. preamble: \usepackage{amsmath} — formulas
- [ ] 411. preamble: \usepackage{fancyhdr} — headers/footers
- [ ] 412. preamble: \usepackage{listings} — code listings
- [ ] 413. COVER_PAGE template with {title}, {author}, {date}, {course}, {lecturer} placeholders
- [ ] 414. HEADER_FOOTER_SETUP constant
- [ ] 415. BIBLIOGRAPHY_SECTION constant
- [ ] 416. Create src/article_writer/latex/latex_templates_bib.py (if preamble > 150 lines)
- [ ] 417. Write test: LUALATEX_PREAMBLE contains all 12 required packages
- [ ] 418. Write test: COVER_PAGE has all 5 placeholder fields

### S2.Y LaTeX Layer — BiDi Handler
- [ ] 419. Create src/article_writer/latex/bidi_handler.py
- [ ] 420. BiDiHandler class
- [ ] 421. HEBREW_RANGE = (0x0590, 0x05FF)
- [ ] 422. contains_hebrew(text: str) -> bool: check Unicode range
- [ ] 423. wrap_rtl(text: str) -> str: wrap with \begin{RTL}...\end{RTL}
- [ ] 424. wrap_ltr(text: str) -> str: wrap with \begin{LTR}...\end{LTR}
- [ ] 425. inject_bidi_chapter(chapter_content: str) -> str: auto-detect and wrap blocks
- [ ] 426. inject_bidi_chapter: split on sentence boundaries, detect per-block direction
- [ ] 427. inject_bidi_chapter: wrap Hebrew blocks in RTL, English in LTR
- [ ] 428. polyglossia_setup() -> str: return polyglossia language configuration
- [ ] 429. Write test: contains_hebrew detects Hebrew Unicode range
- [ ] 430. Write test: contains_hebrew returns False for ASCII text
- [ ] 431. Write test: inject_bidi_chapter produces valid LaTeX BiDi markers
- [ ] 432. Write test: polyglossia_setup contains \setdefaultlanguage

### S2.Z LaTeX Layer — Compiler
- [ ] 433. Create src/article_writer/latex/latex_compiler.py
- [ ] 434. CompilationError(Exception) custom exception
- [ ] 435. LaTeXCompiler class
- [ ] 436. __init__: load compiler and compile_passes from config
- [ ] 437. compile(tex_path: Path, output_dir: Path) -> Path
- [ ] 438. compile: run lualatex pass 1 (generates .aux)
- [ ] 439. compile: run biber (processes .bib)
- [ ] 440. compile: run lualatex pass 2 (resolves citations)
- [ ] 441. compile: run lualatex pass 3-4 (resolves cross-refs)
- [ ] 442. compile: capture stdout/stderr; raise CompilationError if exit != 0
- [ ] 443. compile: extract page count from .log file
- [ ] 444. compile: raise CompilationError if page_count < MIN_ARTICLE_PAGES
- [ ] 445. compile: return path to resulting .pdf
- [ ] 446. _run_pass(cmd: list, cwd: Path): subprocess.run wrapper
- [ ] 447. _extract_page_count(log_path: Path) -> int: parse "Output written on ... (N pages)"
- [ ] 448. Verify latex_compiler.py <= 150 lines
- [ ] 449. Write test: compile runs correct number of subprocess calls (mock)
- [ ] 450. Write test: compile raises CompilationError on non-zero exit
- [ ] 451. Write test: _extract_page_count parses correct integer
- [ ] 452. Write test: compile raises if pages < 15

### S2.AA SDK Layer
- [ ] 453. Create src/article_writer/sdk/__init__.py
- [ ] 454. Create src/article_writer/sdk/sdk.py
- [ ] 455. ArticleWriterSDK class — single public entry point
- [ ] 456. __init__: load AppConfig
- [ ] 457. __init__: instantiate ApiGatekeeper (shared singleton)
- [ ] 458. start_research_session(guideline_path: str) -> Path
- [ ] 459. start_research_session: instantiate researcher agent via build_researcher_agent()
- [ ] 460. start_research_session: create research tasks
- [ ] 461. start_research_session: create and kickoff ArticleResearchCrew
- [ ] 462. start_research_session: return Path to data/research.md
- [ ] 463. start_writing_session(guideline_path: str, research_path: str) -> Path
- [ ] 464. start_writing_session: load context via ContextLoader
- [ ] 465. start_writing_session: generate draft via DraftGenerator
- [ ] 466. start_writing_session: return Path to results/draft_v1.tex
- [ ] 467. run_evaluator_loop(draft_path: str, max_iter: int = 3) -> Path
- [ ] 468. run_evaluator_loop: instantiate EvalOptimizerLoop
- [ ] 469. run_evaluator_loop: run loop
- [ ] 470. run_evaluator_loop: return Path to final draft .tex
- [ ] 471. compile_to_pdf(tex_path: str) -> Path
- [ ] 472. compile_to_pdf: instantiate LaTeXCompiler
- [ ] 473. compile_to_pdf: compile to PDF
- [ ] 474. compile_to_pdf: return Path to results/article_final.pdf
- [ ] 475. Verify sdk.py <= 150 lines
- [ ] 476. Write test: SDK initializes without errors (mock config)
- [ ] 477. Write test: start_research_session returns a Path object
- [ ] 478. Write test: compile_to_pdf returns a Path object

### S2.AB Crew Wiring
- [ ] 479. Create src/article_writer/crew.py
- [ ] 480. ArticleResearchCrew class
- [ ] 481. __init__(researcher_agent, tasks: list): store agents and tasks
- [ ] 482. kickoff(inputs: dict) -> str: create Crew and call .kickoff()
- [ ] 483. crew: process = Process.sequential
- [ ] 484. crew: verbose=True
- [ ] 485. ArticleWritingCrew class
- [ ] 486. __init__(writer_agent, evaluator_agent, tasks: list)
- [ ] 487. kickoff(inputs: dict) -> str: create Crew and call .kickoff()
- [ ] 488. Verify crew.py <= 150 lines
- [ ] 489. Write test: ArticleResearchCrew.kickoff creates Crew (mock)
- [ ] 490. Write test: ArticleWritingCrew.kickoff creates Crew (mock)

### S2.AC Main Entry Point
- [ ] 491. Create src/main.py
- [ ] 492. main(): parse CLI args — --guideline, --research (optional), --mode (research|write|full)
- [ ] 493. mode "research": run start_research_session only
- [ ] 494. mode "write": run start_writing_session + run_evaluator_loop + compile_to_pdf
- [ ] 495. mode "full": run entire pipeline end-to-end
- [ ] 496. print output path on success
- [ ] 497. handle exceptions with user-friendly messages (no tracebacks to user)
- [ ] 498. exit(0) on success, exit(1) on failure
- [ ] 499. Verify main.py <= 150 lines
- [ ] 500. Write test: main exits 0 with mock SDK

### S2.AD Writing Profiles
- [ ] 501. Create profiles/Structure.md — document skeleton rules
- [ ] 502. Structure.md: cover page must have topic, author, date, course, lecturer
- [ ] 503. Structure.md: TOC immediately after cover page, linked to all chapters
- [ ] 504. Structure.md: chapters numbered \section{}, subsections \subsection{}
- [ ] 505. Structure.md: headers/footers on all pages (not cover)
- [ ] 506. Structure.md: bibliography last chapter, \printbibliography
- [ ] 507. Structure.md: BiDi chapter must use polyglossia RTL/LTR markers
- [ ] 508. Structure.md: images in \figure environment with \caption
- [ ] 509. Structure.md: tables with \toprule, \midrule, \bottomrule (booktabs)
- [ ] 510. Structure.md: formulas in \begin{equation} environment with label
- [ ] 511. Create profiles/Terminology.md — vocabulary rules
- [ ] 512. Terminology.md: technical terms in English even in Hebrew text
- [ ] 513. Terminology.md: no colloquial contractions in academic text
- [ ] 514. Terminology.md: IEEE citation style — [1], [2], ... inline
- [ ] 515. Terminology.md: numbers > 999 use comma separator (e.g., 10,000)
- [ ] 516. Terminology.md: dates in ISO 8601 (YYYY-MM-DD)
- [ ] 517. Terminology.md: Hebrew transliteration follows Academy of the Hebrew Language
- [ ] 518. Create profiles/Characters.md — voice and tone rules
- [ ] 519. Characters.md: formal academic voice, no first person ("the paper argues...")
- [ ] 520. Characters.md: sentences max 25 words
- [ ] 521. Characters.md: paragraphs 4–7 sentences
- [ ] 522. Characters.md: no exclamation marks
- [ ] 523. Characters.md: passive voice allowed for methodology sections

### S2.AE Few-Shot Examples
- [ ] 524. Create few_shot_examples/example_intro.md
- [ ] 525. example_intro: 3-paragraph LaTeX introduction with \section{Introduction}
- [ ] 526. example_intro: demonstrates cite commands (\cite{key})
- [ ] 527. example_intro: demonstrates formal tone per Characters.md
- [ ] 528. Create few_shot_examples/example_section.md
- [ ] 529. example_section: LaTeX body section with heading, table, and formula
- [ ] 530. example_section: table uses booktabs \toprule/\midrule/\bottomrule
- [ ] 531. example_section: formula in \begin{equation} with label and \ref
- [ ] 532. Create few_shot_examples/example_conclusion.md
- [ ] 533. example_conclusion: LaTeX conclusion section
- [ ] 534. example_conclusion: synthesis of 3 main research points
- [ ] 535. example_conclusion: future work paragraph

### S2.AF Data Input Template
- [ ] 536. Create data/guideline.md.example — template for article guideline
- [ ] 537. guideline.md.example: ## Topic section with placeholder
- [ ] 538. guideline.md.example: ## Angle section with placeholder
- [ ] 539. guideline.md.example: ## Key Points section with 5 bullet placeholders
- [ ] 540. guideline.md.example: ## Narrative Arc section with placeholder
- [ ] 541. guideline.md.example: ## Target Length: ~15 pages
- [ ] 542. Add data/guideline.md.example to git (not data/guideline.md itself)

### S2.AG Graph Generation Script
- [ ] 543. Create assets/graphs/generate_graph.py
- [ ] 544. generate_graph.py: import matplotlib.pyplot as plt
- [ ] 545. generate_graph.py: accept --title, --xlabel, --ylabel, --output CLI args
- [ ] 546. generate_graph.py: generate sample line graph with random data
- [ ] 547. generate_graph.py: save as PDF for LaTeX inclusion (plt.savefig)
- [ ] 548. generate_graph.py: use pgf backend for LaTeX-compatible output
- [ ] 549. Write test: generate_graph.py produces a valid PDF file

---

## STAGE 3 — Quality, Testing & Submission

### S3.A Test Infrastructure
- [ ] 550. Create tests/conftest.py with all shared fixtures
- [ ] 551. fixture: mock_gemini_client — returns preset search results
- [ ] 552. fixture: mock_perplexity_client — returns preset search results
- [ ] 553. fixture: temp_data_dir (tmp_path) with guideline.md and research.md
- [ ] 554. fixture: sample_guideline_content — valid markdown guideline
- [ ] 555. fixture: sample_research_content — valid markdown research artifact
- [ ] 556. fixture: sample_draft_tex — minimal compilable LaTeX source
- [ ] 557. fixture: gatekeeper_with_test_config — ApiGatekeeper from test config
- [ ] 558. fixture: all_profiles (Structure, Terminology, Characters) in temp dir
- [ ] 559. fixture: few_shot_files in temp dir

### S3.B Unit Tests — Shared
- [ ] 560. tests/unit/test_shared/test_constants.py — all 10 constants defined
- [ ] 561. tests/unit/test_shared/test_config.py — load_config success + failure cases
- [ ] 562. tests/unit/test_shared/test_logger.py — ArticleLogger methods
- [ ] 563. tests/unit/test_shared/test_gatekeeper.py — rate limiting + retry logic
- [ ] 564. tests/unit/test_shared/test_version.py — get_version format

### S3.C Unit Tests — Tools
- [ ] 565. tests/unit/test_tools/test_base_tool.py — sanitize and log methods
- [ ] 566. tests/unit/test_tools/test_deep_research.py — search + fallback + confidence filter
- [ ] 567. tests/unit/test_tools/test_researcher_handler.py — session management
- [ ] 568. tests/unit/test_tools/test_citation_extractor.py — URL vs text detection
- [ ] 569. tests/unit/test_tools/test_content_filter.py — HIGH/MEDIUM/LOW classification

### S3.D Unit Tests — Agents
- [ ] 570. tests/unit/test_agents/test_base_agent.py — _load_skills, build_backstory
- [ ] 571. tests/unit/test_agents/test_researcher_agent.py — initialization, tool count
- [ ] 572. tests/unit/test_agents/test_writer_agent.py — initialization, delegation flag

### S3.E Unit Tests — Writing Pipeline
- [ ] 573. tests/unit/test_writing/test_context_loader.py — load + build + missing file
- [ ] 574. tests/unit/test_writing/test_draft_generator.py — generate + validate + save
- [ ] 575. tests/unit/test_writing/test_evaluator.py — scoring + critique + log
- [ ] 576. tests/unit/test_writing/test_optimizer.py — versioned save + diff log
- [ ] 577. tests/unit/test_writing/test_loop_controller.py — min 2 iter + threshold + max

### S3.F Unit Tests — LaTeX
- [ ] 578. tests/unit/test_latex/test_templates.py — package presence in preamble
- [ ] 579. tests/unit/test_latex/test_bidi_handler.py — Hebrew detection + wrapping
- [ ] 580. tests/unit/test_latex/test_compiler.py — subprocess calls + page extraction

### S3.G Integration Tests
- [ ] 581. tests/integration/test_context_pipeline.py — ContextLoader → DraftGenerator
- [ ] 582. tests/integration/test_eval_loop.py — loop runs ≥ 2 iterations minimum
- [ ] 583. tests/integration/test_research_to_artifact.py — filter → artifact file written

### S3.H Coverage & Linting
- [ ] 584. Run ruff check src/ — fix all violations
- [ ] 585. Run ruff check tests/ — fix all violations
- [ ] 586. Verify ruff reports 0 violations
- [ ] 587. Run pytest --cov=src --cov-report=term-missing
- [ ] 588. Verify coverage >= 85%
- [ ] 589. Fill any coverage gap with targeted tests
- [ ] 590. Generate HTML coverage report in results/coverage_html/

### S3.I File Size Enforcement
- [ ] 591. Create scripts/check_file_sizes.py
- [ ] 592. check_file_sizes.py: walk src/ and find files > 150 lines
- [ ] 593. check_file_sizes.py: exit 1 and list offending files
- [ ] 594. Run check_file_sizes.py and confirm 0 violations
- [ ] 595. Split any file > 150 lines into smaller modules

### S3.J Security Checks
- [ ] 596. git grep -r "API_KEY\s*=" src/ — must return nothing
- [ ] 597. git grep -r "api_key\s*=" src/ — must return nothing
- [ ] 598. Verify .env in .gitignore
- [ ] 599. Verify all 3 API keys in .env-example with placeholder values
- [ ] 600. Verify content_filter runs before web content injected into any prompt

### S3.K End-to-End Article Run
- [ ] 601. Write actual data/guideline.md for real article topic
- [ ] 602. Run SDK.start_research_session — approve research batches interactively
- [ ] 603. Inspect research.md — verify ≥ 10 cited facts
- [ ] 604. Run SDK.start_writing_session
- [ ] 605. Inspect draft_v1.tex for LaTeX validity
- [ ] 606. Run SDK.run_evaluator_loop — verify ≥ 2 iterations in eval_log.json
- [ ] 607. Run SDK.compile_to_pdf — verify exit code 0
- [ ] 608. Open article_final.pdf — verify cover page
- [ ] 609. Verify PDF TOC with working links
- [ ] 610. Verify PDF >= 15 pages
- [ ] 611. Verify PDF has >= 1 image with caption
- [ ] 612. Verify PDF has Python-generated graph
- [ ] 613. Verify PDF has >= 1 formatted table (booktabs)
- [ ] 614. Verify PDF has >= 1 mathematical formula in equation environment
- [ ] 615. Verify PDF has >= 1 BiDi chapter (Hebrew + English)
- [ ] 616. Verify bibliography with >= 10 citations
- [ ] 617. Verify headers and footers on all non-cover pages

### S3.L LaTeX Quality
- [ ] 618. Run lualatex with -interaction=nonstopmode
- [ ] 619. Verify 0 LaTeX errors in .log file
- [ ] 620. Verify 0 undefined references (\ref warnings)
- [ ] 621. Verify 0 missing citations
- [ ] 622. Verify biber runs without errors
- [ ] 623. Verify Hebrew fonts render in PDF
- [ ] 624. Verify RTL chapter direction correct

### S3.M Documentation
- [ ] 625. Verify README.md complete (description, install, usage, architecture)
- [ ] 626. Verify docs/PRD.md complete
- [ ] 627. Verify docs/PLAN.md complete
- [ ] 628. Verify docs/TODO.md has 800 items
- [ ] 629. Verify all 5 per-mechanism PRDs exist
- [ ] 630. Verify skills.md and tools.md exist at project root
- [ ] 631. Verify skills/research/SKILL.md, skills/writing/SKILL.md, skills/catch-me-up/SKILL.md exist

---

## ADDITIONAL QUALITY — OOP, Security, Observability

### AQ.A OOP Design Compliance
- [ ] 632. Verify ResearcherAgent inherits from BaseAgentMixin
- [ ] 633. Verify WriterAgent inherits from BaseAgentMixin
- [ ] 634. Verify all 4 tools inherit from ArticleBaseTool
- [ ] 635. Verify ArticleBaseTool inherits from crewai BaseTool
- [ ] 636. Verify no method duplicated across agent classes
- [ ] 637. Verify no method duplicated across tool classes
- [ ] 638. Run grep for copy-pasted code blocks (manual review)
- [ ] 639. Verify config loading uses lru_cache singleton (no duplicate reads)

### AQ.B Prompt Engineering Completeness
- [ ] 640. Verify deep_research tool has explicit prompt template documented
- [ ] 641. Verify researcher_handler tool has explicit prompt template documented
- [ ] 642. Verify citation_extractor has 2 prompt templates (URL + text)
- [ ] 643. Verify content_filter has explicit prompt template with JSON output spec
- [ ] 644. Verify DraftGenerator system prompt injects all 3 profile files
- [ ] 645. Verify Evaluator prompt specifies all 5 dimension weights
- [ ] 646. Verify Optimizer prompt instructs to apply ALL critique points
- [ ] 647. Verify all prompt templates stored as class-level constants (not inline strings)

### AQ.C Security Review
- [ ] 648. Review deep_research_tool._run: confirm sanitize_input is called first
- [ ] 649. Review content_filter: confirm LLM response is parsed as JSON not eval()
- [ ] 650. Review mcp_server: confirm no shell injection in tool dispatch
- [ ] 651. Review latex_compiler: confirm subprocess uses list args, not shell=True
- [ ] 652. Review citation_extractor: confirm URLs are validated before use
- [ ] 653. Review gatekeeper.execute: confirm api_call is callable, not string
- [ ] 654. Review main.py: confirm no raw user input passed to shell

### AQ.D Observability Completeness
- [ ] 655. Verify every MCP client logs token usage per call
- [ ] 656. Verify every tool logs via _log_call at entry
- [ ] 657. Verify gatekeeper logs every API call with timestamp
- [ ] 658. Verify eval_log.json has entry per loop iteration
- [ ] 659. Verify run_log.txt has all INFO and WARNING level events
- [ ] 660. Create notebooks/analysis.ipynb
- [ ] 661. notebook: load and plot eval_log.json scores per iteration
- [ ] 662. notebook: load run_log.txt and compute total token usage
- [ ] 663. notebook: plot API calls per service (bar chart)

### AQ.E ISO/IEC 25010 Compliance
- [ ] 664. Document Functional Suitability — all 12 AC in PRD met
- [ ] 665. Document Performance Efficiency — gatekeeper enforces rate limits
- [ ] 666. Document Reliability — retry logic, fallback Perplexity
- [ ] 667. Document Security — prompt injection mitigation, no hardcoded keys
- [ ] 668. Document Maintainability — OOP, ≤150 lines, Ruff, TDD
- [ ] 669. Document Portability — uv, .env, config files, no OS-specific paths
- [ ] 670. Add compliance table to README.md

### AQ.F Final Pre-Submission Checklist
- [ ] 671. All 12 acceptance criteria (PRD Section 6) verified
- [ ] 672. Ruff: 0 violations across src/ and tests/
- [ ] 673. pytest: coverage ≥ 85%
- [ ] 674. All Python files ≤ 150 lines
- [ ] 675. No secrets in git (git log -p | grep -i "api_key" returns nothing)
- [ ] 676. .env-example committed with all 3 API key placeholders
- [ ] 677. docs/ has PRD, PLAN, TODO, 5 per-mechanism PRDs
- [ ] 678. README.md exists and complete
- [ ] 679. promptsUsed.md exists with original prompt verbatim
- [ ] 680. config/ has setup.json and rate_limits.json version 1.00
- [ ] 681. article_final.pdf exists and >= 15 pages
- [ ] 682. eval_log.json shows >= 2 evaluator iterations
- [ ] 683. research.md exists with >= 10 cited facts
- [ ] 684. All figures in PDF have captions
- [ ] 685. All tables formatted with booktabs
- [ ] 686. Mathematical formula in proper equation environment
- [ ] 687. Bibliography uses biblatex + .bib file
- [ ] 688. BiDi chapter demonstrates Hebrew RTL correctly
- [ ] 689. SDK is single entry point — no bypassing
- [ ] 690. ApiGatekeeper wraps every external API call
- [ ] 691. uv is only package manager (no pip in scripts or README)
- [ ] 692. Version 1.00 in setup.json and pyproject.toml
- [ ] 693. skills.md and tools.md exist at project root
- [ ] 694. All 3 skill files exist with examples and constraints
- [ ] 695. All 4 tool files exist with prompt templates
- [ ] 696. catch-me-up skill responds correctly to trigger phrase
- [ ] 697. Graph in PDF generated by assets/graphs/generate_graph.py
- [ ] 698. Submission package complete and organized
- [ ] 699. Manager approves final article PDF
- [ ] 700. Assignment submitted before deadline

---

## EXTENDED TASKS — Robustness & Edge Cases

### EX.A Edge Case Handling
- [ ] 701. Handle Gemini returning empty response (retry once then fallback)
- [ ] 702. Handle Perplexity returning citations with no URL
- [ ] 703. Handle research.md having 0 facts (abort with clear error)
- [ ] 704. Handle LLM returning LaTeX with syntax errors (retry generation)
- [ ] 705. Handle LaTeX compilation taking > 5 minutes (timeout)
- [ ] 706. Handle biber not found in PATH (raise clear error with install hint)
- [ ] 707. Handle lualatex not found in PATH (raise clear error)
- [ ] 708. Handle results/ directory not writable (fail fast with clear message)
- [ ] 709. Handle evaluator returning score outside 0-10 (clamp and warn)
- [ ] 710. Handle optimizer producing longer output than context window (chunked revision)

### EX.B Additional Tests
- [ ] 711. Test: Gemini empty response → fallback to Perplexity
- [ ] 712. Test: Perplexity citation without URL → plain text citation
- [ ] 713. Test: research.md empty → SDK raises ValueError
- [ ] 714. Test: LLM LaTeX missing \begin{document} → DraftGenerator retries
- [ ] 715. Test: LaTeX compile timeout → CompilationError raised
- [ ] 716. Test: evaluator score clamped if outside 0-10
- [ ] 717. Test: main.py exit code 1 on CompilationError
- [ ] 718. Test: main.py exit code 1 on FileNotFoundError
- [ ] 719. Test: content_filter handles empty content string
- [ ] 720. Test: researcher_handler handles no new queries suggested

### EX.C Performance Tests
- [ ] 721. Test: gatekeeper processes 30 requests within 1 minute window correctly
- [ ] 722. Test: ContextLoader handles profile files of 10,000+ characters
- [ ] 723. Test: DraftGenerator handles context string > 50,000 characters
- [ ] 724. Test: EvalOptimizerLoop completes within reasonable time (mock LLM)
- [ ] 725. Test: LaTeXCompiler handles 200-page document without timeout

### EX.D Documentation Edge Cases
- [ ] 726. Verify catch-me-up skill works at any point in the project lifecycle
- [ ] 727. Verify catch-me-up output is ≤ 80 lines (terminal screen constraint)
- [ ] 728. Verify skills.md table is correct after adding any new skill
- [ ] 729. Verify tools.md table is correct after adding any new tool
- [ ] 730. Verify promptsUsed.md is updated with any new significant prompt

### EX.E Code Quality Deep Dive
- [ ] 731. Verify no bare except: clauses (always catch specific exceptions)
- [ ] 732. Verify all dataclasses use type annotations
- [ ] 733. Verify all public functions have return type annotations
- [ ] 734. Verify no mutable default arguments in function signatures
- [ ] 735. Verify no global mutable state outside of singletons
- [ ] 736. Verify all file paths use pathlib.Path not string concatenation
- [ ] 737. Verify all subprocess calls use list args (not shell=True)
- [ ] 738. Verify all json.loads calls have error handling
- [ ] 739. Verify all file reads specify encoding="utf-8"
- [ ] 740. Verify all lru_cache functions are pure (no side effects)

### EX.F MCP Server Quality
- [ ] 741. Verify MCP server handles unknown tool name gracefully
- [ ] 742. Verify MCP server handles missing "prompt" field in input
- [ ] 743. Verify MCP server returns proper error type on failure
- [ ] 744. Verify MCP server can be started independently of CrewAI
- [ ] 745. Verify MCP server health check endpoint responds

### EX.G LaTeX Deep Quality
- [ ] 746. Verify LaTeX uses \addbibresource{} for .bib file
- [ ] 747. Verify all \cite{} keys have matching entries in .bib
- [ ] 748. Verify \label{} for every \section, \subsection, figure, table, equation
- [ ] 749. Verify \ref{} and \pageref{} usage is consistent
- [ ] 750. Verify Hebrew font is set explicitly (e.g., David CLM or Frank Ruhl)

### EX.H Skill Quality
- [ ] 751. Verify skills/research/SKILL.md has ≥ 3 example research queries
- [ ] 752. Verify skills/research/SKILL.md has ≥ 5 constraints listed
- [ ] 753. Verify skills/writing/SKILL.md has ≥ 2 example LaTeX snippets
- [ ] 754. Verify skills/writing/SKILL.md has ≥ 5 writing constraints
- [ ] 755. Verify skills/catch-me-up/SKILL.md has example output format
- [ ] 756. Verify catch-me-up output format has: project name, stage, agents, tools, tree

### EX.I Tool Prompt Quality
- [ ] 757. Verify deep_research prompt specifies citation format in instructions
- [ ] 758. Verify researcher_handler prompt specifies to avoid duplicate angles
- [ ] 759. Verify citation_extractor prompt specifies JSON return format
- [ ] 760. Verify content_filter prompt specifies HIGH/MEDIUM/LOW definitions

### EX.J Version & Release
- [ ] 761. Tag git commit v1.00 — initial architecture
- [ ] 762. Tag git commit v1.01 — implementation complete
- [ ] 763. Tag git commit v1.02 — tests passing + article generated
- [ ] 764. Maintain version changelog in docs/CHANGELOG.md
- [ ] 765. docs/CHANGELOG.md: v1.00 — Architecture definition
- [ ] 766. docs/CHANGELOG.md: v1.01 — Full implementation
- [ ] 767. docs/CHANGELOG.md: v1.02 — Tests + article PDF

### EX.K Data Management
- [ ] 768. results/ directory: never commit generated .tex or .pdf to git
- [ ] 769. data/research.md: never commit (generated artifact)
- [ ] 770. data/guideline.md: never commit (human input)
- [ ] 771. Add results/, data/research.md, data/guideline.md to .gitignore
- [ ] 772. Committed: data/guideline.md.example (template only)
- [ ] 773. Committed: few_shot_examples/ all files
- [ ] 774. Committed: profiles/ all 3 files
- [ ] 775. Committed: skills/ all SKILL.md files
- [ ] 776. Committed: config/ both JSON files
- [ ] 777. Committed: assets/graphs/generate_graph.py

### EX.L Completeness — Per-Mechanism PRDs
- [ ] 778. PRD_researcher_agent.md: scope, inputs, behavior steps, tools used, HITL points
- [ ] 779. PRD_writer_agent.md: scope, inputs, 3 phases, evaluator loop, output
- [ ] 780. PRD_mcp_tools.md: all 4 tools described with prompt templates
- [ ] 781. PRD_latex_pipeline.md: packages, compilation steps, BiDi, page requirements
- [ ] 782. PRD_evaluator_optimizer.md: rubric weights, loop termination conditions, minimum iterations

### EX.M Notebook & Analysis
- [ ] 783. notebooks/analysis.ipynb cell 1: import and load eval_log.json
- [ ] 784. notebooks/analysis.ipynb cell 2: matplotlib bar chart — score per dimension per iteration
- [ ] 785. notebooks/analysis.ipynb cell 3: load run_log.txt, parse API call records
- [ ] 786. notebooks/analysis.ipynb cell 4: compute total cost estimate
- [ ] 787. notebooks/analysis.ipynb cell 5: pie chart — token usage by service
- [ ] 788. notebooks/analysis.ipynb cell 6: summary statistics table

### EX.N Final Validation Checklist (Manager)
- [ ] 789. Manager reads article_final.pdf cover to cover
- [ ] 790. Manager verifies topic matches original guideline.md
- [ ] 791. Manager verifies all research citations are real and accessible
- [ ] 792. Manager verifies writing quality matches academic standard
- [ ] 793. Manager verifies BiDi chapter is linguistically correct
- [ ] 794. Manager verifies graph is labeled and readable
- [ ] 795. Manager verifies formula is mathematically correct
- [ ] 796. Manager verifies table data is accurate per research.md
- [ ] 797. Manager approves submission
- [ ] 798. Final submission package assembled
- [ ] 799. Submission uploaded per course instructions
- [ ] 800. Post-submission: archive all results/ files for reproducibility

---

# Stage 3 Extension — 650 New Tasks

## S3-A: LLM Abstraction Layer

### S3-A.1 llm_client.py Core
- [x] S3-A-001. Create `src/article_writer/shared/llm_client.py`
- [x] S3-A-002. Define `LLMResponse` dataclass with `text, input_tokens, output_tokens, model, cost_usd`
- [x] S3-A-003. Define `_AnthropicResult` dataclass for internal SDK result
- [x] S3-A-004. Define `_COST_PER_1K` lookup dict with model pricing
- [x] S3-A-005. Implement `LLMClient.__init__` — resolve provider from env var then config
- [x] S3-A-006. Implement `LLMClient.__init__` — lazy import Anthropic SDK on `provider=anthropic`
- [x] S3-A-007. Implement `LLMClient.__init__` — lazy import Google Generative AI on `provider=google`
- [x] S3-A-008. Implement `LLMClient.complete(system, user, step, temperature, max_tokens) -> LLMResponse`
- [x] S3-A-009. Implement `LLMClient._call_anthropic` — call `messages.create` with system + user
- [x] S3-A-010. Implement `LLMClient._call_google` — call `generate_content` with combined prompt
- [x] S3-A-011. Implement `LLMClient._estimate_cost` — lookup model in `_COST_PER_1K`, fallback to default
- [x] S3-A-012. Wire `Tracer.log()` inside `LLMClient.complete` after every call
- [x] S3-A-013. Wire `MetricsTracker.log()` inside `LLMClient.complete` with latency_ms
- [x] S3-A-014. Add `_DEFAULT_PROMPT` for judge as module-level constant (used in judge.py not here)
- [ ] S3-A-015. Add unit test: mock Anthropic SDK, call `complete`, assert `LLMResponse.text` populated
- [ ] S3-A-016. Add unit test: mock Google SDK, call `complete` with `provider=google`
- [ ] S3-A-017. Add unit test: `_estimate_cost` for known model returns correct float
- [ ] S3-A-018. Add unit test: unknown model falls back to default cost
- [ ] S3-A-019. Add unit test: `LLM_PROVIDER` env var overrides `provider` parameter
- [ ] S3-A-020. Add unit test: `complete` raises `ValueError` for unknown provider
- [ ] S3-A-021. Add unit test: Tracer.log called exactly once per `complete()` call
- [ ] S3-A-022. Add unit test: MetricsTracker.log called exactly once per `complete()` call
- [ ] S3-A-023. Verify ruff passes on `llm_client.py`
- [ ] S3-A-024. Verify `llm_client.py` is ≤150 lines

### S3-A.2 Config Extension
- [x] S3-A-025. Add `anthropic_model` field to `config/setup.json["llm"]`
- [x] S3-A-026. Add `gemini_model` field to `config/setup.json["llm"]`
- [x] S3-A-027. Add `review_iterations` field to `config/setup.json["writing"]`
- [x] S3-A-028. Add `tracing` section to `config/setup.json` with `enabled`, `traces_file`, `metrics_file`
- [ ] S3-A-029. Update `AppConfig` / `LLMConfig` dataclass in `shared/config.py` to include `anthropic_model` and `gemini_model`
- [ ] S3-A-030. Update `WritingConfig` dataclass to include `review_iterations`
- [ ] S3-A-031. Add `TracingConfig` dataclass with `enabled`, `traces_file`, `metrics_file`
- [ ] S3-A-032. Update `load_config()` to populate new config fields
- [ ] S3-A-033. Add unit test for new config fields loaded correctly

### S3-A.3 Environment Variables
- [x] S3-A-034. Update `.env-example` with `LLM_PROVIDER` variable and explanatory comment
- [x] S3-A-035. Update `.env-example` header comment explaining provider switching
- [ ] S3-A-036. Verify `.env-example` is in `.gitignore` scope (only `.env` ignored, not `.env-example`)
- [ ] S3-A-037. Test: set `LLM_PROVIDER=google` in test env, verify `LLMClient` selects Google

## S3-B: PDF Few-Shot Loading

### S3-B.1 few_shot_loader.py
- [x] S3-B-001. Create `src/article_writer/writing/few_shot_loader.py`
- [x] S3-B-002. Define `_MAX_CHARS_PER_EXAMPLE = 8000` constant
- [x] S3-B-003. Define `_HEADER_FMT` constant for labelled few-shot headers
- [x] S3-B-004. Implement `FewShotLoader.__init__(directory)` with `Path` conversion
- [x] S3-B-005. Implement `FewShotLoader.load_all() -> list[dict]` — iterates directory, dispatch by suffix
- [x] S3-B-006. Implement `.pdf` branch in `load_all` via `_read_pdf()`
- [x] S3-B-007. Implement `.md` / `.txt` branch in `load_all` via `Path.read_text`
- [x] S3-B-008. Implement `FewShotLoader._read_pdf(path) -> str` using `fitz.open()`
- [x] S3-B-009. Add try/except in `_read_pdf` — return error placeholder on failure
- [x] S3-B-010. Implement `FewShotLoader.build_context_block() -> str` — formatted header + text
- [x] S3-B-011. Return empty string from `build_context_block` when no examples found
- [ ] S3-B-012. Add unit test: `load_all()` with a real PDF returns non-empty text
- [ ] S3-B-013. Add unit test: `load_all()` with `.md` file returns file content
- [ ] S3-B-014. Add unit test: empty directory returns `[]`
- [ ] S3-B-015. Add unit test: unreadable PDF returns placeholder string (not exception)
- [ ] S3-B-016. Add unit test: text truncated to `_MAX_CHARS_PER_EXAMPLE`
- [ ] S3-B-017. Add unit test: `build_context_block` empty dir returns empty string
- [ ] S3-B-018. Add unit test: files sorted alphabetically in output
- [ ] S3-B-019. Verify PyMuPDF listed in `pyproject.toml` dependencies
- [ ] S3-B-020. Verify ruff passes on `few_shot_loader.py`

### S3-B.2 Context Loader Update
- [ ] S3-B-021. Update `writing/context_loader.py` to call `FewShotLoader(few_shot_dir).build_context_block()`
- [ ] S3-B-022. Remove old `.md`-only few-shot loading code from `context_loader.py`
- [ ] S3-B-023. Add unit test: context_loader includes PDF-extracted text in output block
- [ ] S3-B-024. Verify old `.Zone.Identifier` files are gitignored or removed

## S3-C: Tracing and Metrics

### S3-C.1 tracer.py
- [x] S3-C-001. Create `src/article_writer/shared/tracer.py`
- [x] S3-C-002. Define `_DEFAULT_PATH = Path("results/traces.jsonl")`
- [x] S3-C-003. Implement `Tracer.__init__(path)` — resolve path from param or env var
- [x] S3-C-004. Implement `Tracer.log(step, model, provider, input, output, ...)` — append JSONL
- [x] S3-C-005. Implement `Tracer.log_tool(tool_name, input_data, output_data, step, metadata)`
- [x] S3-C-006. Implement `Tracer.read_all() -> list[dict]` — read all records from file
- [x] S3-C-007. Truncate `input` and `output` to 6000 chars each in `log()`
- [x] S3-C-008. Auto-create `results/` directory in `__init__`
- [x] S3-C-009. Use `datetime.now(tz=timezone.utc).isoformat()` for timestamp
- [ ] S3-C-010. Add unit test: `Tracer.log()` appends one JSONL record
- [ ] S3-C-011. Add unit test: `Tracer.read_all()` returns list of dicts
- [ ] S3-C-012. Add unit test: long input truncated to ≤6000 chars in record
- [ ] S3-C-013. Add unit test: `log_tool()` sets `tool_name` field in record
- [ ] S3-C-014. Add unit test: multiple calls produce multiple records (append, not overwrite)
- [ ] S3-C-015. Add unit test: non-existent file returns `[]` from `read_all()`
- [ ] S3-C-016. Verify ruff passes on `tracer.py`
- [ ] S3-C-017. Verify `tracer.py` ≤ 150 lines

### S3-C.2 metrics_tracker.py
- [x] S3-C-018. Create `src/article_writer/shared/metrics_tracker.py`
- [x] S3-C-019. Define `_DEFAULT_PATH = Path("results/metrics.jsonl")`
- [x] S3-C-020. Implement `MetricsTracker.__init__(path)` — resolve from param or env var
- [x] S3-C-021. Implement `MetricsTracker.log(step, model, latency_ms, input_tokens, output_tokens, cost_usd)` — append JSONL
- [x] S3-C-022. Compute `total_tokens = input_tokens + output_tokens` in `log()`
- [x] S3-C-023. Round `cost_usd` to 6 decimal places in `log()`
- [x] S3-C-024. Implement `MetricsTracker.summary() -> dict` — aggregate totals
- [x] S3-C-025. Return zeroed dict from `summary()` when file doesn't exist
- [ ] S3-C-026. Add unit test: `log()` writes record with all expected fields
- [ ] S3-C-027. Add unit test: `summary()` totals tokens and cost correctly
- [ ] S3-C-028. Add unit test: `summary()` returns zeros when no file
- [ ] S3-C-029. Add unit test: `total_tokens` = input + output in each record
- [ ] S3-C-030. Verify ruff passes on `metrics_tracker.py`

## S3-D: Review Loop

### S3-D.1 reviewer.py
- [x] S3-D-001. Create `src/article_writer/writing/reviewer.py`
- [x] S3-D-002. Define `_REVIEWER_SYSTEM` prompt — strict isolation notice, JSON output schema
- [x] S3-D-003. Implement `ReviewComment(BaseModel)` with `profile`, `location`, `comment` fields
- [x] S3-D-004. Implement `ArticleReview(BaseModel)` with `comments`, `overall_score`, `pass_fail`
- [x] S3-D-005. Implement `Reviewer.__init__(llm)` — defaults to `LLMClient()`
- [x] S3-D-006. Implement `Reviewer.review(draft_path, guideline_path, research_path, profiles_dir) -> ArticleReview`
- [x] S3-D-007. Implement `Reviewer._load_profiles(profiles_dir)` — concat all `*.md` files
- [x] S3-D-008. Implement `Reviewer._parse(raw) -> ArticleReview` — JSON extraction + Pydantic validation
- [x] S3-D-009. Add fallback `ArticleReview` in `_parse` when JSON parse fails
- [x] S3-D-010. Verify `Reviewer` NEVER instantiates `FewShotLoader` or loads few-shot files
- [x] S3-D-011. Use `temperature=0.1` for reviewer (low variance desired)
- [ ] S3-D-012. Add unit test: `_parse` with valid JSON returns correct `ArticleReview`
- [ ] S3-D-013. Add unit test: `_parse` with invalid JSON returns fallback `ArticleReview`
- [ ] S3-D-014. Add unit test: `review()` with mock LLM returns `ArticleReview`
- [ ] S3-D-015. Add unit test: `_load_profiles` loads all `.md` files in profiles dir
- [ ] S3-D-016. Add unit test: reviewer user message contains draft + guideline + research + profiles
- [ ] S3-D-017. Add unit test: reviewer user message does NOT contain "FEW-SHOT" keyword
- [ ] S3-D-018. Add unit test: `pass_fail` is "PASS" or "FAIL" only
- [ ] S3-D-019. Verify ruff passes on `reviewer.py`
- [ ] S3-D-020. Verify `reviewer.py` ≤ 150 lines

### S3-D.2 editor.py
- [x] S3-D-021. Create `src/article_writer/writing/editor.py`
- [x] S3-D-022. Define `_EDITOR_SYSTEM` prompt — correction priority rules, LaTeX-only output
- [x] S3-D-023. Implement `Editor.__init__(llm, few_shot_dir)` — defaults to `LLMClient()`
- [x] S3-D-024. Implement `Editor.apply(draft_path, review, guideline_path, research_path, profiles_dir, version) -> Path`
- [x] S3-D-025. Implement `Editor._format_comments(review) -> str` — priority-sorted comment list
- [x] S3-D-026. Implement `Editor._load_profiles(profiles_dir) -> str`
- [x] S3-D-027. Ensure editor output saved to `results/draft_v{version}.tex`
- [x] S3-D-028. Include few-shot context in editor prompt (unlike reviewer)
- [x] S3-D-029. Use `temperature=0.2` for editor (slightly more creative than reviewer)
- [x] S3-D-030. Use `max_tokens=12000` for editor (full draft can be long)
- [ ] S3-D-031. Add unit test: `_format_comments` puts Coverage before Structure
- [ ] S3-D-032. Add unit test: `_format_comments` puts Accuracy before Terminology
- [ ] S3-D-033. Add unit test: `apply()` with mock LLM writes `draft_v{N}.tex`
- [ ] S3-D-034. Add unit test: editor prompt includes few-shot header
- [ ] S3-D-035. Add unit test: editor prompt includes all profile sections
- [ ] S3-D-036. Verify ruff passes on `editor.py`
- [ ] S3-D-037. Verify `editor.py` ≤ 150 lines

### S3-D.3 review_loop.py
- [x] S3-D-038. Create `src/article_writer/writing/review_loop.py`
- [x] S3-D-039. Implement `ReviewLoop.__init__(iterations, guideline_path, ...)` — clamp iterations 2–4
- [x] S3-D-040. Implement `ReviewLoop.run(initial_draft) -> Path` — returns `draft_final.tex`
- [x] S3-D-041. Implement `ReviewLoop._save_review(review, version)` — writes `review_v{N}.json`
- [x] S3-D-042. Print progress: iteration/total, score, pass_fail, comment count
- [x] S3-D-043. Implement early stop: `pass_fail == "PASS" AND iteration >= 2`
- [x] S3-D-044. Always write `draft_final.tex` (copy of last draft) at end
- [x] S3-D-045. Create `results/` directory in `__init__`
- [ ] S3-D-046. Add unit test: minimum 2 iterations always run even on PASS in iteration 1
- [ ] S3-D-047. Add unit test: early stop at iteration 2 when PASS
- [ ] S3-D-048. Add unit test: `review_v1.json` saved with correct structure
- [ ] S3-D-049. Add unit test: `draft_final.tex` exists after `run()`
- [ ] S3-D-050. Add unit test: `draft_v2.tex` exists after one edit cycle
- [ ] S3-D-051. Add integration test: full 3-iteration loop with mock LLM
- [ ] S3-D-052. Verify ruff passes on `review_loop.py`

### S3-D.4 Version File Integrity
- [ ] S3-D-053. Test: after 2 iterations, `results/` contains draft_v1, review_v1, draft_v2, review_v2, draft_final
- [ ] S3-D-054. Test: after 3 iterations, results contain v1 through v3 plus final
- [ ] S3-D-055. Test: `review_v{N}.json` is valid JSON parseable as `ArticleReview.model_validate()`
- [ ] S3-D-056. Test: `draft_final.tex` content equals the last `draft_v{N}.tex`
- [ ] S3-D-057. Ensure version counter does not reset on retry (no file collision)
- [ ] S3-D-058. Ensure `draft_v1.tex` produced by `DraftGenerator` feeds into `ReviewLoop.run()`

## S3-E: Eval Dataset

### S3-E.1 article_extractor.py
- [x] S3-E-001. Create `src/article_writer/eval/article_extractor.py`
- [x] S3-E-002. Define `ExtractedArticle` dataclass with `filename, page_count, full_text, abstract, keywords, sections`
- [x] S3-E-003. Define `_MIN_PAGES = 13`, `_MAX_PAGES = 20` filter constants
- [x] S3-E-004. Implement `ArticleExtractor.extract(pdf_path) -> ExtractedArticle`
- [x] S3-E-005. Implement `ArticleExtractor.extract_directory(directory) -> list[ExtractedArticle]`
- [x] S3-E-006. Filter out articles outside 13–20 page range in `extract_directory`
- [x] S3-E-007. Implement `_parse_abstract` — find "abstract" in text, extract until "keyword"
- [x] S3-E-008. Implement `_parse_keywords` — find "keywords", split on comma/semicolon
- [x] S3-E-009. Implement `_parse_sections` — find IMRAD headings, extract up to 3000 chars each
- [ ] S3-E-010. Add unit test: `extract()` on `behavsci-16-00973.pdf` returns page_count = 16
- [ ] S3-E-011. Add unit test: `extract()` on `foods-15-02113.pdf` returns page_count = 20
- [ ] S3-E-012. Add unit test: `extract()` on `animals-16-01806.pdf` returns page_count = 18
- [ ] S3-E-013. Add unit test: `_parse_abstract` returns non-empty string for MDPI article
- [ ] S3-E-014. Add unit test: `_parse_keywords` returns list of ≥3 keywords
- [ ] S3-E-015. Add unit test: `_parse_sections` finds "Introduction" key
- [ ] S3-E-016. Add unit test: PDF not found raises `RuntimeError`
- [ ] S3-E-017. Add unit test: article with 12 pages excluded by `extract_directory`
- [ ] S3-E-018. Add unit test: article with 21 pages excluded by `extract_directory`
- [ ] S3-E-019. Verify ruff passes on `article_extractor.py`
- [ ] S3-E-020. Verify `article_extractor.py` ≤ 150 lines

### S3-E.2 dataset_builder.py
- [x] S3-E-021. Create `src/article_writer/eval/dataset_builder.py`
- [x] S3-E-022. Define `_LABEL_SYSTEM` LLM system prompt for binary labelling
- [x] S3-E-023. Define `LabelledSample` dataclass with all fields
- [x] S3-E-024. Implement `DatasetBuilder.__init__(llm, seed)` — default seed 42 for reproducibility
- [x] S3-E-025. Implement `DatasetBuilder.build_from_articles(articles, output_dir) -> dict`
- [x] S3-E-026. Implement `DatasetBuilder._label(art) -> tuple[str, str]` — LLM label + critique
- [x] S3-E-027. Implement `DatasetBuilder._split(samples) -> dict` — deterministic shuffle + split
- [x] S3-E-028. Implement `DatasetBuilder._save(splits, out_dir)` — writes JSONL per split
- [x] S3-E-029. Add JSON parse fallback in `_label` when LLM returns unparseable output
- [x] S3-E-030. Create `eval_dataset/splits/` directories in `_save`
- [ ] S3-E-031. Add unit test: `_label` with mock LLM returning valid JSON
- [ ] S3-E-032. Add unit test: `_label` with unparseable JSON falls back to FAIL
- [ ] S3-E-033. Add unit test: `_split` with 20 samples gives ≥2 in dev and test
- [ ] S3-E-034. Add unit test: all split samples have correct `split` field set
- [ ] S3-E-035. Add unit test: JSONL files exist after `_save`
- [ ] S3-E-036. Add integration test: `build_from_articles` with 3 real MDPI PDFs
- [ ] S3-E-037. Verify `_split` is deterministic with same seed
- [ ] S3-E-038. Verify ruff passes on `dataset_builder.py`
- [ ] S3-E-039. Verify `dataset_builder.py` ≤ 150 lines
- [ ] S3-E-040. Create `eval_dataset/raw/` directory for user to drop PDFs into

### S3-E.3 judge.py
- [x] S3-E-041. Create `src/article_writer/eval/judge.py`
- [x] S3-E-042. Define `_DEFAULT_PROMPT` — strict JSON schema with dimension_scores
- [x] S3-E-043. Implement `JudgeResult(BaseModel)` with all fields
- [x] S3-E-044. Implement `ArticleJudge.__init__(llm, prompt)` — prompt defaults to `_DEFAULT_PROMPT`
- [x] S3-E-045. Implement `ArticleJudge.judge(article_text, guideline, research, article_id) -> JudgeResult`
- [x] S3-E-046. Implement `ArticleJudge.judge_from_paths(article_path, ...) -> JudgeResult`
- [x] S3-E-047. Implement `ArticleJudge._parse(raw, article_id) -> JudgeResult`
- [x] S3-E-048. Add fallback `JudgeResult` in `_parse` when JSON fails
- [x] S3-E-049. Use `temperature=0.1` for judge (want consistent scoring)
- [ ] S3-E-050. Add unit test: `_parse` valid JSON returns correct `JudgeResult`
- [ ] S3-E-051. Add unit test: `_parse` invalid JSON returns fallback with FAIL
- [ ] S3-E-052. Add unit test: `judge()` passes correct fields to LLM
- [ ] S3-E-053. Add unit test: `judge_from_paths` reads files and delegates to `judge()`
- [ ] S3-E-054. Add unit test: `JudgeResult.dimension_scores` has all 5 keys
- [ ] S3-E-055. Verify ruff passes on `judge.py`
- [ ] S3-E-056. Verify `judge.py` ≤ 150 lines

### S3-E.4 f1_metrics.py
- [x] S3-E-057. Create `src/article_writer/eval/f1_metrics.py`
- [x] S3-E-058. Define `F1Result` dataclass with `precision, recall, f1, tp, fp, fn, tn, accuracy`
- [x] S3-E-059. Implement `compute_f1(predictions, ground_truth, positive_class) -> F1Result`
- [x] S3-E-060. Implement `format_report(result, split_name) -> str`
- [x] S3-E-061. Handle zero-division in precision, recall, F1, accuracy
- [ ] S3-E-062. Add unit test: all PASS predictions vs all PASS labels → precision=1.0 recall=1.0 F1=1.0
- [ ] S3-E-063. Add unit test: all wrong → precision=0.0 recall=0.0 F1=0.0
- [ ] S3-E-064. Add unit test: mixed predictions → known expected F1
- [ ] S3-E-065. Add unit test: different lengths raise `ValueError`
- [ ] S3-E-066. Add unit test: `format_report` contains "F1" and numeric value
- [ ] S3-E-067. Add unit test: accuracy computed correctly
- [ ] S3-E-068. Verify ruff passes on `f1_metrics.py`

### S3-E.5 judge_loop.py
- [x] S3-E-069. Create `src/article_writer/eval/judge_loop.py`
- [x] S3-E-070. Define `_PROMPT_REFINER_SYSTEM` for prompt refinement agent
- [x] S3-E-071. Define `_F1_TARGET = 0.80`, `_MAX_ITERS = 5`
- [x] S3-E-072. Implement `LoopIteration` dataclass
- [x] S3-E-073. Implement `JudgeLoop.__init__(llm, f1_target, max_iterations, guideline_path, research_path)`
- [x] S3-E-074. Implement `JudgeLoop.run(dev_samples, test_samples, initial_prompt) -> dict`
- [x] S3-E-075. Implement `JudgeLoop._evaluate_split(judge, samples) -> tuple[list, list]`
- [x] S3-E-076. Implement `JudgeLoop._refine_prompt(current, f1, samples, preds, labels) -> str`
- [x] S3-E-077. Implement `JudgeLoop._describe_errors(samples, preds, labels) -> str` — max 5 examples
- [x] S3-E-078. Final test split evaluated AFTER loop, not modified during loop
- [ ] S3-E-079. Add unit test: early stop when F1 ≥ target after first iteration
- [ ] S3-E-080. Add unit test: max_iterations respected even if F1 never reaches target
- [ ] S3-E-081. Add unit test: `_describe_errors` returns FP and FN correctly labelled
- [ ] S3-E-082. Add unit test: `run()` result dict has `test_f1`, `dev_f1_history`, `final_prompt`
- [ ] S3-E-083. Add unit test: `_evaluate_split` returns predictions and labels of same length
- [ ] S3-E-084. Verify ruff passes on `judge_loop.py`

### S3-E.6 Eval Module Init
- [x] S3-E-085. Create `src/article_writer/eval/__init__.py`
- [ ] S3-E-086. Add `eval_dataset/raw/` directory with `.gitkeep`
- [ ] S3-E-087. Add `eval_dataset/splits/` directory with `.gitkeep`
- [ ] S3-E-088. Create CLI script `scripts/run_eval_pipeline.py` — extract → label → split → judge_loop
- [ ] S3-E-089. Add `[project.scripts]` entry in `pyproject.toml` for eval pipeline
- [ ] S3-E-090. Document eval pipeline in README under "Running the Eval Pipeline"

## S3-F: Content Files

### S3-F.1 data/guideline.md
- [x] S3-F-001. Write `data/guideline.md` from scratch based on MDPI PDF examples
- [x] S3-F-002. Include Topic and full title
- [x] S3-F-003. Include Target Journal field
- [x] S3-F-004. Include Angle — empirical-theoretical hybrid
- [x] S3-F-005. Include Abstract Structure — 4-sentence target
- [x] S3-F-006. Include Keywords (6–8)
- [x] S3-F-007. Include Required Sections table with min lengths
- [x] S3-F-008. Include Key Points list (8 mandatory points)
- [x] S3-F-009. Include Narrative Arc (6-step story)
- [x] S3-F-010. Include Target Length (min 15 pages, expected 16–18)
- [x] S3-F-011. Include Language Requirements (English + Hebrew BiDi)
- [x] S3-F-012. Include Required Visual Elements table (2 tables, 2 figures, 1 equation)
- [x] S3-F-013. Include Cover Page Information table
- [x] S3-F-014. Include Citation Style (numbered [N], MDPI format)
- [x] S3-F-015. Include Priority Hierarchy (guideline > research > profiles)
- [ ] S3-F-016. Verify guideline references all 3 MDPI PDF examples' structural patterns
- [ ] S3-F-017. Verify BiDi section requirement is explicit in guideline
- [ ] S3-F-018. Verify equation specified in guideline matches weighted score formula

### S3-F.2 README.md
- [x] S3-F-019. Rewrite `README.md` comprehensively
- [x] S3-F-020. Add Quick Start section with 6 commands
- [x] S3-F-021. Add Environment Variables table
- [x] S3-F-022. Add model-switching explanation (Nagham vs partner)
- [x] S3-F-023. Add Directory Structure with full annotated tree
- [x] S3-F-024. Add ASCII architecture diagram showing full pipeline
- [x] S3-F-025. Add Agent Contexts table (who sees what)
- [x] S3-F-026. Add Tracing and Metrics section with sample JSONL records
- [x] S3-F-027. Add Eval Dataset Pipeline section (5-step description)
- [x] S3-F-028. Add Configuration section with setup.json example
- [x] S3-F-029. Add Running Tests section
- [x] S3-F-030. Add Running the Eval Pipeline section
- [x] S3-F-031. Add Quality Standards table
- [x] S3-F-032. Add Skills Reference table
- [x] S3-F-033. Add Tools Reference table
- [ ] S3-F-034. Verify all directory paths in README exist in the actual project
- [ ] S3-F-035. Verify all commands in README are valid `uv run` commands

## S3-G: Tests for Stage 3 Modules

### S3-G.1 Unit Test Files
- [ ] S3-G-001. Create `tests/unit/test_llm_client.py`
- [ ] S3-G-002. Create `tests/unit/test_tracer.py`
- [ ] S3-G-003. Create `tests/unit/test_metrics_tracker.py`
- [ ] S3-G-004. Create `tests/unit/test_few_shot_loader.py`
- [ ] S3-G-005. Create `tests/unit/test_reviewer.py`
- [ ] S3-G-006. Create `tests/unit/test_editor.py`
- [ ] S3-G-007. Create `tests/unit/test_f1_metrics.py`
- [ ] S3-G-008. Create `tests/unit/test_judge.py`
- [ ] S3-G-009. Create `tests/unit/test_article_extractor.py`
- [ ] S3-G-010. Create `tests/unit/test_dataset_builder.py`

### S3-G.2 Integration Test Files
- [ ] S3-G-011. Create `tests/integration/test_review_loop.py`
- [ ] S3-G-012. Create `tests/integration/test_judge_loop.py`
- [ ] S3-G-013. Create `tests/integration/test_few_shot_real_pdfs.py`

### S3-G.3 Test Infrastructure
- [ ] S3-G-014. Create `tests/conftest.py` — fixtures: mock LLM client, temp results dir, sample draft
- [ ] S3-G-015. Add `MockLLMClient` fixture that returns configurable text
- [ ] S3-G-016. Add `sample_review_json` fixture with valid `ArticleReview` JSON
- [ ] S3-G-017. Add `sample_extracted_article` fixture with `ExtractedArticle`
- [ ] S3-G-018. Add `sample_labelled_samples` fixture for judge loop tests
- [ ] S3-G-019. Ensure all tests use temp directories (not polluting real `results/`)
- [ ] S3-G-020. Run `uv run pytest` — confirm all tests pass
- [ ] S3-G-021. Run `uv run pytest --cov=src` — confirm ≥85% coverage
- [ ] S3-G-022. Run `uv run ruff check src/` — confirm zero violations
- [ ] S3-G-023. Check all new Python files are ≤150 lines

### S3-G.4 Specific Test Cases
- [ ] S3-G-024. Test: `compute_f1([PASS, FAIL], [PASS, FAIL]) → F1=1.0`
- [ ] S3-G-025. Test: `compute_f1([PASS, PASS], [FAIL, FAIL]) → precision=0, F1=0`
- [ ] S3-G-026. Test: `compute_f1([FAIL, FAIL], [PASS, PASS]) → recall=0, F1=0`
- [ ] S3-G-027. Test: reviewer system prompt does not contain "few-shot" or "examples"
- [ ] S3-G-028. Test: editor system prompt contains "priority" ordering
- [ ] S3-G-029. Test: `ReviewLoop` with 1 PASS review still runs 2 iterations
- [ ] S3-G-030. Test: `MetricsTracker.summary()` returns correct totals after 3 log calls
- [ ] S3-G-031. Test: `LLMClient` with Anthropic provider calls `messages.create`
- [ ] S3-G-032. Test: `LLMClient` with Google provider calls `generate_content`
- [ ] S3-G-033. Test: `FewShotLoader` with mixed PDF and MD files loads both

## S3-H: Integration and End-to-End

### S3-H.1 SDK Integration
- [ ] S3-H-001. Update `src/article_writer/sdk/sdk.py` to import and use `ReviewLoop`
- [ ] S3-H-002. Update `sdk.py` — replace old eval loop with `ReviewLoop.run(initial_draft)`
- [ ] S3-H-003. Update `sdk.py` — use `LLMClient` instead of direct Anthropic calls
- [ ] S3-H-004. Update `sdk.py` — pass `few_shot_dir` to `ContextLoader` and `Editor`
- [ ] S3-H-005. Update `src/main.py` to show summary from `MetricsTracker.summary()` at end
- [ ] S3-H-006. Add `--provider` CLI flag to `src/main.py` as override for `LLM_PROVIDER`
- [ ] S3-H-007. Update `src/main.py` — print trace count at end of run
- [ ] S3-H-008. Add `--review-iterations` CLI flag to `src/main.py`

### S3-H.2 Crew Integration
- [ ] S3-H-009. Update `src/article_writer/crew.py` to use `ReviewLoop` in writing crew
- [ ] S3-H-010. Ensure `ArticleWritingCrew` passes correct paths to `ReviewLoop`
- [ ] S3-H-011. Add integration test: research crew → writing crew → review loop full chain

### S3-H.3 End-to-End Smoke Test
- [ ] S3-H-012. Create `tests/e2e/test_smoke.py` — full pipeline with stub API responses
- [ ] S3-H-013. Test: `draft_v1.tex` created by DraftGenerator
- [ ] S3-H-014. Test: `review_v1.json` created by ReviewLoop after first iteration
- [ ] S3-H-015. Test: `draft_final.tex` created at end of ReviewLoop
- [ ] S3-H-016. Test: `traces.jsonl` contains ≥3 records after one review cycle
- [ ] S3-H-017. Test: `metrics.jsonl` contains latency_ms field in every record
- [ ] S3-H-018. Test: total cost from `MetricsTracker.summary()` > 0 after a real API run

### S3-H.4 Final Quality Gate
- [ ] S3-H-019. `uv run ruff check src/` — zero violations
- [ ] S3-H-020. `uv run pytest --cov=src --cov-fail-under=85` — passes
- [ ] S3-H-021. All Python files ≤150 lines: `for f in src/**/*.py; do wc -l $f; done`
- [ ] S3-H-022. `data/guideline.md` exists and is non-empty
- [ ] S3-H-023. `data/research.md` exists (from a research run) or stub exists
- [ ] S3-H-024. All 3 MDPI PDFs exist in `few_shot_examples/`
- [ ] S3-H-025. `results/` directory writeable
- [ ] S3-H-026. `eval_dataset/splits/train.jsonl` exists with ≥1 record
- [ ] S3-H-027. `eval_dataset/splits/dev.jsonl` exists with ≥1 record
- [ ] S3-H-028. `eval_dataset/splits/test.jsonl` exists with ≥1 record

## S3-I: Observability and Reporting

### S3-I.1 Runtime Reporting
- [ ] S3-I-001. Add `print` summary at end of `ReviewLoop.run()` — total reviews, final score
- [ ] S3-I-002. Add `print` summary at end of `JudgeLoop.run()` — iterations, test F1
- [ ] S3-I-003. Add `MetricsTracker.summary()` call in `sdk.py` after full pipeline
- [ ] S3-I-004. Print cost breakdown: research phase, writing phase, review phase
- [ ] S3-I-005. Print total wall-clock time from `time.perf_counter()`

### S3-I.2 Log Files
- [ ] S3-I-006. Ensure `results/traces.jsonl` is gitignored (contains API I/O)
- [ ] S3-I-007. Ensure `results/metrics.jsonl` is gitignored
- [ ] S3-I-008. Ensure `results/draft_*.tex` and `results/review_*.json` are gitignored
- [ ] S3-I-009. Keep only `results/.gitkeep` tracked; all generated files in .gitignore
- [ ] S3-I-010. Update `.gitignore` with `results/*.jsonl`, `results/*.tex`, `results/*.json`

### S3-I.3 Trace Analysis
- [ ] S3-I-011. Create `scripts/analyze_traces.py` — reads `traces.jsonl`, prints per-step summary
- [ ] S3-I-012. Script outputs: step name, model, tokens (in/out), truncated I/O snippet
- [ ] S3-I-013. Create `scripts/analyze_metrics.py` — reads `metrics.jsonl`, prints cost table
- [ ] S3-I-014. Script outputs: step, latency_ms, cost_usd, cumulative total
- [ ] S3-I-015. Test: `analyze_traces.py` runs on a sample `traces.jsonl` without error
- [ ] S3-I-016. Test: `analyze_metrics.py` runs on a sample `metrics.jsonl` without error

## S3-J: Documentation and Prompts

### S3-J.1 promptsUsed.md
- [x] S3-J-001. Add Stage 3 prompt (Message 5) verbatim to `promptsUsed.md`
- [ ] S3-J-002. Add section header "Prompt 2 — Stage 3 Extension" above the verbatim text
- [ ] S3-J-003. Add "Key Decisions Extracted from Prompt 2" table after verbatim text
- [ ] S3-J-004. Verify `promptsUsed.md` is committed to git

### S3-J.2 PRD and PLAN Updates
- [x] S3-J-005. Append Stage 3 section to `docs/PRD.md`
- [x] S3-J-006. Append Stage 3 implementation section to `docs/PLAN.md`
- [x] S3-J-007. Add ADR-006 (reviewer isolation) to `PLAN.md`
- [x] S3-J-008. Add ADR-007 (JSONL for traces) to `PLAN.md`
- [x] S3-J-009. Add ADR-008 (F1 convergence) to `PLAN.md`

### S3-J.3 TODO File
- [x] S3-J-010. Write 650-item Stage 3 TODO list in `docs/TODO.md`
- [ ] S3-J-011. Verify all completed items are marked [x]
- [ ] S3-J-012. Verify all pending items are marked [ ]
- [ ] S3-J-013. Verify TODO count: `grep -c "^\- \[" docs/TODO.md`

### S3-J.4 skills.md and tools.md
- [ ] S3-J-014. Update `skills.md` — add any new skills introduced in Stage 3
- [ ] S3-J-015. Update `tools.md` — note PDF few-shot loading in writing tool section
- [ ] S3-J-016. Update `tools.md` — add `LLMClient` as internal tool with dual provider note

## S3-K: Security and Safety

### S3-K.1 Prompt Injection
- [ ] S3-K-001. Verify `Reviewer._REVIEWER_SYSTEM` prompt mentions isolation
- [ ] S3-K-002. Add input sanitization in `Reviewer.review()` before LLM call
- [ ] S3-K-003. Add input sanitization in `Editor.apply()` before LLM call
- [ ] S3-K-004. Add input sanitization in `ArticleJudge.judge()` before LLM call
- [ ] S3-K-005. Test: sanitizer strips `<script>` tags from draft text before review

### S3-K.2 API Key Safety
- [ ] S3-K-006. Verify no API keys in any tracked file (`git grep "sk-ant" src/`)
- [ ] S3-K-007. Verify `.env` is in `.gitignore`
- [ ] S3-K-008. Verify `traces.jsonl` does not contain API keys in logged I/O
- [ ] S3-K-009. Add warning in `Tracer.log()` if input contains "sk-" pattern
- [ ] S3-K-010. Test: `Tracer.log()` with an API key in input triggers warning

## S3-L: Performance and Rate Limits

### S3-L.1 Rate Limit Integration
- [ ] S3-L-001. Wire `LLMClient.complete()` through `ApiGatekeeper` for Anthropic calls
- [ ] S3-L-002. Wire `LLMClient.complete()` through `ApiGatekeeper` for Google calls
- [ ] S3-L-003. Update `config/rate_limits.json` with Google Gemini writing limits
- [ ] S3-L-004. Test: `ApiGatekeeper` blocks second call if rpm exceeded
- [ ] S3-L-005. Test: `ApiGatekeeper` allows call after cooldown period

### S3-L.2 Context Window Management
- [ ] S3-L-006. Ensure `Reviewer` user message does not exceed 60k tokens
- [ ] S3-L-007. Ensure `Editor` user message does not exceed 60k tokens
- [ ] S3-L-008. Add token estimation in `LLMClient` (approx 4 chars/token)
- [ ] S3-L-009. Log warning when estimated tokens > 50k
- [ ] S3-L-010. Test: oversized draft triggers warning before review call

## S3-M: Final Submission Checklist

### S3-M.1 Article Quality
- [ ] S3-M-001. Run full pipeline end-to-end with real API keys
- [ ] S3-M-002. Verify `draft_final.tex` compiles with lualatex
- [ ] S3-M-003. Verify `article_final.pdf` is ≥15 pages
- [ ] S3-M-004. Verify PDF contains all 3 profiles' requirements
- [ ] S3-M-005. Verify Hebrew BiDi chapter compiles correctly
- [ ] S3-M-006. Verify Figure 1 (architecture diagram) renders
- [ ] S3-M-007. Verify Figure 2 (F1 vs iteration) renders
- [ ] S3-M-008. Verify Table 1 (agent comparison) renders
- [ ] S3-M-009. Verify Table 2 (quantitative results) renders
- [ ] S3-M-010. Verify Equation 1 (weighted score) renders correctly

### S3-M.2 Code Quality
- [ ] S3-M-011. Zero ruff violations across all source files
- [ ] S3-M-012. ≥85% test coverage
- [ ] S3-M-013. All Python files ≤150 lines
- [ ] S3-M-014. All acceptance criteria in PRD verified
- [ ] S3-M-015. `promptsUsed.md` has both prompts

### S3-M.3 Eval Quality
- [ ] S3-M-016. Eval dataset has ≥10 labelled samples
- [ ] S3-M-017. Judge achieves F1 ≥ 0.80 on dev split
- [ ] S3-M-018. Judge validated on test split (not used during training)
- [ ] S3-M-019. `eval_dataset/splits/*.jsonl` all non-empty
- [ ] S3-M-020. Judge results logged to `results/traces.jsonl`

### S3-M.4 Repository Cleanliness
- [ ] S3-M-021. No `.env` file committed
- [ ] S3-M-022. No API keys in any tracked file
- [ ] S3-M-023. `results/` directory in `.gitignore` (except `.gitkeep`)
- [ ] S3-M-024. `__pycache__` in `.gitignore`
- [ ] S3-M-025. `uv.lock` committed and up to date
- [ ] S3-M-026. Git log has meaningful commit messages
- [ ] S3-M-027. Branch is clean (`git status` shows nothing uncommitted)
- [ ] S3-M-028. PR or submission package ready
