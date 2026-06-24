# Changelog

## [1.0.0] — 2026-06-22

### Added
- Project scaffold: pyproject.toml, .gitignore, .env-example
- docs/PRD.md — full product requirements document
- docs/PLAN.md — modular pipeline architecture (C4 diagrams, ADRs, API contracts)
- docs/TODO.md — 800-item task list across 10 phases
- docs/PRD_airllm.md — AirLLM layer-streaming mechanism spec
- docs/PRD_quantization.md — Q2/Q4/Q8 quantization mechanism spec
- docs/PRD_monitoring.md — OS page monitoring mechanism spec
- docs/hardware_specs.md — documented machine specs (i7-1165G7, 8 GB RAM, no GPU)
- config/models.json — hookable model registry (Qwen2.5-7B + Qwen2.5-1.5B defaults)
- config/setup.json — evaluation parameters
- config/rate_limits.json — ApiGatekeeper rate limits
- prompts_ive_used.md — AI agent prompt log
- src/hw5/__init__.py — package root with version string
- tests/conftest.py — shared pytest fixtures
- Makefile — dev workflow targets (test, lint, run, clean, report)
