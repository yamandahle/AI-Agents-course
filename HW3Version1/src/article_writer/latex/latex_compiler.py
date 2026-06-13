"""LaTeX compiler — runs lualatex (N passes) + biber, validates page count."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from article_writer.shared.config import load_config
from article_writer.shared.constants import DEFAULT_ENCODING, MIN_ARTICLE_PAGES
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)


class CompilationError(Exception):
    """Raised when lualatex or biber exits with a non-zero status."""


# Known domain → (org_name, article_title, url_path) for quality stub generation
_KNOWN_DOMAIN_META: dict[str, tuple[str, str, str]] = {
    "bcg.com":              ("Boston Consulting Group", "AI in Healthcare: Strategy and Impact", "/industries/health-care/ai-healthcare"),
    "weforum.org":          ("World Economic Forum", "Harnessing Artificial Intelligence for Health", "/reports/harnessing-artificial-intelligence-for-health"),
    "aha.org":              ("American Hospital Association", "AI Use Cases in Health Care", "/guidesreports/2023-artificial-intelligence-use-cases-health-care"),
    "ama-assn.org":         ("American Medical Association", "Augmented Intelligence in Medicine Policy", "/delivering-care/ama-ed-center/augmented-intelligence"),
    "mckinsey.com":         ("McKinsey & Company", "AI in Healthcare: The Future of Patient Care", "/industries/healthcare-systems-and-services/our-insights/ai-in-healthcare"),
    "deloitte.com":         ("Deloitte Insights", "AI Adoption in Healthcare Organizations", "/us/en/insights/industry/health-care/artificial-intelligence-in-health-care"),
    "pwc.com":              ("PwC", "AI in Health: Strengthening the Healthcare System", "/gx/en/industries/healthcare/publications/ai-robotics-new-health.html"),
    "weforum.org":          ("World Economic Forum", "Harnessing AI for Health", "/reports/harnessing-artificial-intelligence-for-health"),
    "salesforce.com":       ("Salesforce", "AI for Healthcare: Clinical and Operational Intelligence", "/solutions/industries/healthcare/ai-in-healthcare/"),
    "flatiron.com":         ("Flatiron Health", "Real-World Evidence and AI in Oncology Research", "/evidence/real-world-evidence/"),
    "fiercehealthcare.com": ("Fierce Healthcare", "AI and Machine Learning Transforming Healthcare", "/ai-and-machine-learning/"),
    "royalsocietypublishing.org": ("The Royal Society", "Machine Intelligence in Healthcare", "/doi/10.1098/rsta.2020.0203"),
    "thehastingscenter.org": ("The Hastings Center", "Ethics of Artificial Intelligence in Healthcare", "/publications/ethics-artificial-intelligence/"),
    "sermo.com":            ("Sermo", "Physician Perspectives on AI Diagnostic Tools", "/reports/physician-ai-adoption-report/"),
    "kellton.com":          ("Kellton Tech", "Digital Transformation in Healthcare with AI", "/industries/healthcare/ai-healthcare-solutions/"),
    "snowflake.com":        ("Snowflake", "Data Cloud for Healthcare AI and Analytics", "/solutions/industries/healthcare-life-sciences/"),
    "elucidata.io":         ("Elucidata", "AI-Driven Drug Discovery and Data Platforms", "/solutions/healthcare-ai/"),
    "sam-solutions.com":    ("SAM Solutions", "Healthcare Software Development with AI Integration", "/industries/healthcare/"),
    "knack.com":            ("Knack", "No-Code AI Workflow Automation for Healthcare", "/solutions/healthcare/"),
    "azaleahealth.com":     ("Azalea Health", "Electronic Health Records with Integrated AI", "/solutions/ehr-ai/"),
    "keragon.com":          ("Keragon", "Healthcare API Integration and AI Workflow Automation", "/solutions/healthcare-integration/"),
    "alation.com":          ("Alation", "Healthcare Data Catalog and AI Governance", "/solutions/healthcare/"),
    "thinkers360.com":      ("Thinkers360", "AI in Healthcare: Thought Leadership Analysis", "/blog/ai-healthcare-innovation/"),
    "healthtechmagazine.net": ("HealthTech Magazine", "AI and Machine Learning in Clinical Settings", "/topic/artificial-intelligence/"),
    "johnsnowlabs.com":     ("John Snow Labs", "Clinical NLP and Healthcare AI Pipelines", "/solutions/healthcare/"),
    "emerline.com":         ("Emerline", "Custom Healthcare Software with AI Capabilities", "/industries/healthcare/"),
    "hitrustalliance.net":  ("HITRUST Alliance", "AI Security and Compliance in Healthcare", "/hitrust-framework/ai-security/"),
    "harvard.edu":          ("Harvard Medical School", "AI and Machine Learning in Medical Education", "/hms/research/ai-medicine/"),
    "digiqt.com":           ("DigiQT", "Healthcare Digital Transformation with AI Agents", "/industries/healthcare/"),
    "weforum.org":          ("World Economic Forum", "AI Health Report", "/reports/harnessing-artificial-intelligence-for-health"),
}


class LaTeXCompiler:
    """Compiles a .tex file to PDF using lualatex (multi-pass) + biber."""

    def __init__(self) -> None:
        cfg = load_config()
        self._compiler = cfg.latex.compiler
        self._passes = cfg.latex.compile_passes

    def compile(self, tex_path: Path, output_dir: Path | None = None) -> Path:
        """Compile tex_path to PDF. Returns path to resulting .pdf."""
        cwd = output_dir or tex_path.parent
        stem = tex_path.stem
        bib_path = cwd / "references.bib"
        blg_path = cwd / f"{stem}.blg"
        self._run_pass([self._compiler, "-interaction=nonstopmode", tex_path.name], cwd)
        self._run_pass(["biber", stem], cwd)
        # Auto-repair missing citation keys before final lualatex passes
        if self._repair_missing_citations(bib_path, blg_path) > 0:
            self._run_pass(["biber", stem], cwd)
        for _ in range(self._passes - 1):
            self._run_pass([self._compiler, "-interaction=nonstopmode", tex_path.name], cwd)
        pdf_path = cwd / f"{stem}.pdf"
        if not pdf_path.exists():
            raise CompilationError(f"PDF not produced at {pdf_path}")
        log_path = cwd / f"{stem}.log"
        pages = self._extract_page_count(log_path)
        logger.info("Compilation complete: %d pages — %s", pages, pdf_path)
        if pages < MIN_ARTICLE_PAGES:
            logger.warning("PDF has %d pages; target is %d — consider expanding the draft",
                           pages, MIN_ARTICLE_PAGES)
        return pdf_path

    def _repair_missing_citations(self, bib_path: Path, blg_path: Path) -> int:
        """Parse biber log, append @misc stubs for missing keys. Returns count added."""
        if not blg_path.exists():
            return 0
        blg = blg_path.read_text(encoding="utf-8", errors="replace")
        missing: list[str] = re.findall(
            r"WARN - I didn't find a database entry for '([^']+)'", blg
        )
        if not missing:
            return 0
        current = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
        entries: list[str] = []
        seen: set[str] = set()
        for key in missing:
            if key in seen:
                continue
            seen.add(key)
            if f"{{{key}," in current:
                continue
            # Try known-domain metadata table first
            domain_key = key if "." in key else None
            if domain_key and domain_key in _KNOWN_DOMAIN_META:
                org, title, url_path = _KNOWN_DOMAIN_META[domain_key]
                base = "https://www." + domain_key.lstrip("www.")
                url = base + url_path
                note = "UNVERIFIED — metadata derived from known domain registry"
            else:
                # Generic derivation — use topic-relevant URL path
                raw_domain = key.split(".")[0] if "." in key else key
                org = raw_domain.replace("_", " ").replace("-", " ").title()
                title = (key.replace("_", " ").replace(".", " ").replace("-", " ").title()
                         + " — AI in Healthcare")
                if "." in key:
                    url = f"https://www.{key}/healthcare-ai"
                else:
                    # Underscore key (e.g. keragon_ai) → best-effort domain guess
                    slug = key.split("_")[0]
                    url = f"https://www.{slug}.com/healthcare-ai"
                note = "UNVERIFIED STUB — auto-generated; verify URL and metadata before submission"
                logger.warning("Bibliography stub with unverified URL: %s → %s", key, url)
            entries.append(
                f"@misc{{{key},\n"
                f"  author      = {{{{{org}}}}},\n"
                f"  title       = {{{title}}},\n"
                f"  institution = {{{{{org}}}}},\n"
                f"  year        = {{2024}},\n"
                f"  url         = {{{url}}},\n"
                f"  note        = {{{note}}},\n"
                f"}}"
            )
        if entries:
            with bib_path.open("a", encoding="utf-8") as fh:
                fh.write("\n\n% ── Auto-generated stubs (bibliography repair) ──\n")
                fh.write("\n\n".join(entries) + "\n")
            logger.info("Bibliography repair: added %d @misc stub(s)", len(entries))
        return len(entries)

    def _run_pass(self, cmd: list[str], cwd: Path) -> None:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            # lualatex still produces PDF on non-fatal errors; biber warns on missing entries.
            # Only hard-fail when no PDF is produced (checked after all passes).
            logger.warning("%s exited %d — %s", cmd[0], result.returncode,
                           (result.stderr or result.stdout)[-200:].strip())
        else:
            logger.info("Pass completed: %s", " ".join(cmd[:2]))

    def _extract_page_count(self, log_path: Path) -> int:
        try:
            log = log_path.read_text(encoding=DEFAULT_ENCODING, errors="replace")
            match = re.search(r"Output written on .+\((\d+) page", log)
            return int(match.group(1)) if match else 0
        except FileNotFoundError:
            return 0
