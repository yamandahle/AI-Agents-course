# Cookiecutter architecture index

Scope: `cookiecutter/` package only (18 Python files). Tests and docs excluded.

## Graph summary

- 269 nodes · 504 edges · 15 communities
- 72% EXTRACTED · 28% INFERRED

## Modules

| Module | Role |
|--------|------|
| [[cookiecutter/main.py]] | Entry: `cookiecutter()` orchestrates the run |
| [[cookiecutter/cli.py]] | CLI argument parsing |
| [[cookiecutter/generate.py]] | File and context generation |
| [[cookiecutter/prompt.py]] | User prompts and config |
| [[cookiecutter/hooks.py]] | Pre/post generation hooks |
| [[cookiecutter/repository.py]] | Template repo detection |
| [[cookiecutter/vcs.py]] | Git clone helpers |
| [[cookiecutter/zipfile.py]] | Zip template handling |
| [[cookiecutter/config.py]] | User and default config |
| [[cookiecutter/environment.py]] | Jinja2 environment |
| [[cookiecutter/extensions.py]] | Jinja2 extensions |
| [[cookiecutter/exceptions.py]] | Exception hierarchy |
| [[cookiecutter/utils.py]] | Shared utilities |
| [[cookiecutter/replay.py]] | Replay saved runs |
| [[cookiecutter/log.py]] | Logging setup |
| [[cookiecutter/find.py]] | Template discovery |

## Navigation

- [[hot.md]] — hubs for bug investigation
- [[GRAPH_REPORT.md]] — full Grphify report

## Research focus

1. Hub: `cookiecutter()` in `main.py`
2. Hub: `generate_files()` in `generate.py`
3. Exception hub: `exceptions.py` (many dependents)
