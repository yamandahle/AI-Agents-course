"""Phase 2 — generates the initial LaTeX draft from unified writer context."""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

from article_writer.shared.config import AppConfig, load_config
from article_writer.shared.constants import RESULTS_DIR
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.llm_client import LLMClient
from article_writer.shared.logger import get_logger
from article_writer.writing._draft_prompt import DRAFT_SYSTEM_PROMPT

load_dotenv()
logger = get_logger(__name__)

_PROVIDER_TO_SERVICE = {"anthropic": "anthropic", "google": "gemini"}

# Import curated set lazily to avoid circular deps at module load time
def _curated_keys() -> frozenset[str]:
    from article_writer.latex.latex_sanitizer import _CURATED_KEYS
    return _CURATED_KEYS

_CITE_RE = re.compile(r"\\cite\{([^}]+)\}")


def _invalid_cite_keys(source: str) -> set[str]:
    curated = _curated_keys()
    bad: set[str] = set()
    for m in _CITE_RE.finditer(source):
        for key in m.group(1).split(","):
            key = key.strip()
            if key and key not in curated:
                bad.add(key)
    return bad


_VALID_KEYS_BLOCK = """\
topol2019highperformance  esteva2017dermatologist  lecun2015deep
davenport2019ai  rajpurkar2017chexnet  mckinney2020international
campanella2019deep  shah2019artificial  saito2015precision
fleming2018artificial  wang2019deep  russell2010artificial
topol2019deep  goodfellow2016deep  who2021ai  fda_ai_ml_samd
gov_uk_mhra_roadmap  nih_ethical_implications  regdesk_eu_ai_act
zynxhealth_clinical_decision_support  relias_healthcare_lms
alation_data_catalog  ey_global_regulatory  jll_commercial_real_estate
dataart_digital_transformation  televox_patient_engagement  oracle_cloud
deepscribe_ai_medical_scribe  ibm_watson_health  microsoft_azure_ai"""


def _strip_code_fence(text: str) -> str:
    """Strip markdown code fences (```latex or ```) from LLM output."""
    import re
    text = text.strip()
    m = re.search(r"```(?:latex|tex)?\s*([\s\S]+?)\s*```\s*$", text)
    return m.group(1).strip() if m else text


# Hard-required structural markers (non-fatal markers are handled in _validate)
_REQUIRED_MARKERS = (r"\begin{document}", r"\end{document}", r"\tableofcontents")


class DraftGenerator:
    """Generates the initial LaTeX draft from combined writer context."""

    def __init__(self, context: str, config: AppConfig | None = None) -> None:
        self._context = context
        self._config = config or load_config()
        self._gate = ApiGatekeeper()

    def generate(self) -> Path:
        """Call LLM to generate draft, validate, save to results/draft_v1.tex."""
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        service = _PROVIDER_TO_SERVICE.get(provider, provider)
        llm = LLMClient()
        user_msg = (
            f"Write a complete LaTeX article (≥{self._config.writing.target_pages} pages) "
            f"based on the following context:\n\n{self._context}"
        )

        def _call():
            return llm.complete(
                system=DRAFT_SYSTEM_PROMPT,
                user=user_msg,
                step="draft_generation",
                max_tokens=32768,
            )

        response = self._gate.execute(service, _call)
        latex_source = _strip_code_fence(response.text)
        logger.log_token_usage(service, response.input_tokens, response.output_tokens)
        latex_source = self._repair_cite_keys(latex_source, service, llm)
        latex_source = self._validate(latex_source)
        return self._save(latex_source, "draft_v1.tex")

    def _repair_cite_keys(self, source: str, service: str, llm: LLMClient) -> str:
        """One-shot correction pass: ask the LLM to fix any invalid \\cite{} keys it generated."""
        bad = _invalid_cite_keys(source)
        if not bad:
            return source
        logger.warning(
            "Draft contains %d invalid cite key(s) — running correction pass: %s",
            len(bad), ", ".join(sorted(bad)),
        )
        bad_list = ", ".join(sorted(bad))
        correction_msg = (
            f"Your LaTeX draft contains {len(bad)} \\cite{{}} key(s) that do NOT exist "
            f"in references.bib:\n\n  {bad_list}\n\n"
            "Return the COMPLETE corrected LaTeX source with every invalid key replaced "
            "by the nearest semantically relevant key from this EXACT list:\n\n"
            f"{_VALID_KEYS_BLOCK}\n\n"
            "Rules:\n"
            "- Replace ONLY the invalid \\cite{} keys; every other character stays identical\n"
            "- If unsure which replacement fits best, use: who2021ai\n"
            "- Output ONLY raw LaTeX — no prose, no markdown fences\n\n"
            + source
        )

        def _call():
            return llm.complete(
                system=DRAFT_SYSTEM_PROMPT,
                user=correction_msg,
                step="cite_key_repair",
                max_tokens=32768,
            )

        resp = self._gate.execute(service, _call)
        corrected = _strip_code_fence(resp.text)
        logger.log_token_usage(service, resp.input_tokens, resp.output_tokens)
        # Safety: if LLM returned garbage, keep original and let sanitizer remap
        remaining = _invalid_cite_keys(corrected)
        if remaining and len(remaining) >= len(bad):
            logger.warning("Cite-key repair pass did not improve output — keeping original for sanitizer")
            return source
        logger.info(
            "Cite-key repair: %d → %d invalid key(s) remaining", len(bad), len(remaining)
        )
        return corrected

    def _validate(self, source: str) -> str:
        """Warn on missing markers; inject fallbacks if absent (non-fatal).

        Never inject \\maketitle when a custom \\begin{titlepage} is present.
        Only injects \\maketitle if BOTH \\maketitle AND \\begin{titlepage} are absent.
        """
        for marker in _REQUIRED_MARKERS[:2]:  # hard requirements
            if marker not in source:
                raise ValueError(f"Generated LaTeX missing required marker: {marker}")
        # Inject \\tableofcontents only if missing
        if r"\tableofcontents" not in source:
            logger.warning("Missing \\tableofcontents — injecting after \\begin{document}")
            source = source.replace(
                r"\begin{document}", r"\begin{document}" + "\n" + r"\tableofcontents", 1
            )
        # Only inject \\maketitle if BOTH \\maketitle AND \\begin{titlepage} are absent
        has_titlepage = r"\begin{titlepage}" in source
        has_maketitle = r"\maketitle" in source
        if not has_maketitle and not has_titlepage:
            logger.warning("No titlepage and no \\maketitle — injecting \\maketitle")
            source = source.replace(
                r"\begin{document}", r"\begin{document}" + "\n" + r"\maketitle", 1
            )
        return source

    def _save(self, source: str, filename: str) -> Path:
        out_dir = Path(RESULTS_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / filename
        path.write_text(source, encoding="utf-8")
        logger.info("Draft saved: %s (%d chars)", path, len(source))
        return path
