"""ArticleWriterSDK — single entry point for all article-writing pipeline operations."""
from __future__ import annotations

from pathlib import Path

from article_writer.shared.config import AppConfig, load_config
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger
from article_writer.shared.metrics_tracker import MetricsTracker

logger = get_logger(__name__)


class ArticleWriterSDK:
    """Facade over the full pipeline. All external callers use this class."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or load_config()
        self._gate = ApiGatekeeper()
        self._metrics = MetricsTracker()

    def start_research_session(self, guideline_path: str) -> Path:
        """Run the researcher agent pipeline. Returns path to data/research.md."""
        from article_writer.agents.researcher_agent import build_researcher_agent
        from article_writer.crew import ArticleResearchCrew
        from article_writer.tasks.research_tasks import (
            make_research_artifact_task,
            make_research_batch_task,
            make_research_filter_task,
        )
        from article_writer.writing.context_loader import ContextLoader
        topic = ContextLoader(guideline_path=guideline_path).load_guideline()[:200]
        researcher = build_researcher_agent()
        batch = make_research_batch_task(researcher, topic)
        filter_t = make_research_filter_task(researcher, batch)
        artifact = make_research_artifact_task(researcher, filter_t)
        crew = ArticleResearchCrew(researcher, [batch, filter_t, artifact])
        crew.kickoff({"topic": topic})
        return Path("data/research.md")

    def start_writing_session(
        self,
        guideline_path: str = "data/guideline.md",
        research_path: str = "data/research.md",
        few_shot_dir: str = "few_shot_examples",
    ) -> Path:
        """Load context + generate initial draft. Returns results/draft_v1.tex."""
        from article_writer.writing.context_loader import ContextLoader
        from article_writer.writing.draft_generator import DraftGenerator
        loader = ContextLoader(
            guideline_path=guideline_path,
            research_path=research_path,
            few_shot_dir=few_shot_dir,
        )
        context = loader.build_writer_context()
        return DraftGenerator(context, self._config).generate()

    def run_review_loop(
        self,
        draft_path: str | Path = "results/draft_v1.tex",
        iterations: int | None = None,
    ) -> Path:
        """Run 3-4 Reviewer→Editor cycles. Returns results/draft_final.tex."""
        from article_writer.writing.review_loop import ReviewLoop
        from article_writer.shared.llm_client import LLMClient
        n = iterations or getattr(self._config.writing, "review_iterations", 3)
        llm = LLMClient()
        loop = ReviewLoop(
            iterations=n,
            guideline_path="data/guideline.md",
            research_path="data/research.md",
            profiles_dir="profiles",
            few_shot_dir="few_shot_examples",
            results_dir="results",
            llm=llm,
        )
        final = loop.run(Path(draft_path))
        summary = self._metrics.summary()
        logger.info("Review loop complete. Cost so far: $%.4f | tokens: %d",
                    summary["total_cost_usd"], summary["total_tokens"])
        return final

    def run_evaluator_loop(self, draft_path: str, max_iter: int | None = None) -> Path:
        """Legacy evaluator-optimizer loop (kept for backwards compatibility)."""
        return self.run_review_loop(draft_path, max_iter)

    def compile_to_pdf(self, tex_path: str) -> Path:
        """Compile LaTeX to PDF via lualatex. Returns path to article_final.pdf."""
        from article_writer.latex.latex_compiler import LaTeXCompiler
        compiler = LaTeXCompiler()
        pdf = compiler.compile(Path(tex_path))
        final = Path("results/article_final.pdf")
        if pdf != final:
            final.parent.mkdir(parents=True, exist_ok=True)
            final.write_bytes(pdf.read_bytes())
        logger.info("Final PDF: %s", final)
        summary = self._metrics.summary()
        logger.info("Total pipeline cost: $%.4f | %d tokens | %dms",
                    summary["total_cost_usd"], summary["total_tokens"],
                    summary["total_latency_ms"])
        return final
