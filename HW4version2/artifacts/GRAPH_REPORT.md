# Graph Report - data/cookiecutter/cookiecutter  (2026-06-19)

## Corpus Check
- 19 files · ~9,298 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 283 nodes · 518 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 142 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c5ee2fa8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]

## God Nodes (most connected - your core abstractions)
1. `UndefinedVariableInTemplate` - 21 edges
2. `CookiecutterException` - 20 edges
3. `generate_files()` - 14 edges
4. `cookiecutter()` - 14 edges
5. `prompt_for_config()` - 12 edges
6. `Context` - 11 edges
7. `Parameter` - 11 edges
8. `ContextDecodingException` - 11 edges
9. `OutputDirExistsException` - 11 edges
10. `EmptyDirNameException` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Any` --uses--> `InvalidModeException`  [INFERRED]
  main.py → exceptions.py
- `Path` --uses--> `RepositoryNotFound`  [INFERRED]
  repository.py → exceptions.py
- `Path` --uses--> `InvalidZipRepository`  [INFERRED]
  zipfile.py → exceptions.py
- `Context` --uses--> `UndefinedVariableInTemplate`  [INFERRED]
  cli.py → exceptions.py
- `Parameter` --uses--> `UndefinedVariableInTemplate`  [INFERRED]
  cli.py → exceptions.py

## Import Cycles
- 1-file cycle: `zipfile.py -> zipfile.py`

## Communities (14 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (39): Any, Exception for out-of-scope variables.      Raised when a template uses a variabl, Exception for out-of-scope variables., Text representation of UndefinedVariableInTemplate., UndefinedVariableInTemplate, choose_nested_template(), JsonPrompt, process_json() (+31 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (32): find_hook(), Any, Path, Functions for discovering and executing various cookiecutter hooks., Execute a script after rendering it with Jinja.      :param script_path: Absolut, Try to find and execute a hook from the specified project directory.      :param, Run hook from repo directory, clean project directory if hook fails.      :param, Run pre_prompt hook from repo directory.      :param repo_dir: Project template (+24 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (38): Any, OrderedDict, Validate extra context., validate_extra_context(), Context, Exception, ContextDecodingException, CookiecutterException (+30 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (22): JsonifyExtension, Environment, RandomStringExtension, Jinja2 Extension constructor., Jinja2 Extension for dates and times., Jinja2 Extension constructor., Parse datetime template and add datetime value., Jinja2 extension to convert a Python object to JSON. (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (18): Confirm, apply_overwrites_to_context(), generate_context(), generate_file(), generate_files(), is_copy_only_path(), Any, Functions for generating a project from a project template. (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (13): ExtensionLoaderMixin, Any, Jinja2 environment and extensions loading., Mixin providing sane loading of extensions specified in a given context.      Th, Initialize the Jinja2 Environment object while loading extensions.          Does, Return list of extensions as str to be passed on to the Jinja2 env.          If, Create strict Jinja2 environment.      Jinja2 environment will raise error on un, Set the standard Cookiecutter StrictEnvironment.          Also loading extension (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (22): cookiecutter(), Any, Main entry point for the `cookiecutter` command.  The code in this module is als, Run Cookiecutter just as if using it from the command line., build_context(), enrich_context(), patch_import_path_for_repo, Any (+14 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (18): Prompt the user to enter a password.      :param question: Question to the user, read_repo_password(), determine_repo_dir(), expand_abbreviations(), is_repo_url(), is_zip_file(), Path, Cookiecutter repository functions. (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.21
Nodes (15): _expand_path(), get_config(), get_user_config(), merge_configs(), Any, Path, Global configuration handling., Expand both environment variables and user home in the given path. (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (11): list_installed_templates(), main(), Main `cookiecutter` CLI., Create a project from a Cookiecutter project template (TEMPLATE).      Cookiecut, Return the Cookiecutter version, location and Python powering it., List installed (locally cloned) templates. Use cookiecutter --list-installed., version_msg(), configure_logger() (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.24
Nodes (10): Exception when version control is unavailable.      Raised if the version contro, VCSNotInstalled, clone(), identify_repo(), is_vcs_installed(), Path, Helper functions for working with version control systems., Determine if `repo_url` should be treated as a URL to a git or hg repo.      Rep (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.29
Nodes (7): NonTemplatedInputDirException, Exception for when a project's input dir is not templated.      The name of the, find_template(), Environment, Path, Functions for finding Cookiecutter templates and other components., Determine which child directory of ``repo_dir`` is the project template.      :p

## Knowledge Gaps
- **7 isolated node(s):** `TemplateError`, `Any`, `Parser`, `Output`, `Logger` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Extension` connect `Community 3` to `Community 5`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `StrictEnvironment` connect `Community 5` to `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Why does `UndefinedVariableInTemplate` connect `Community 0` to `Community 2`, `Community 4`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `UndefinedVariableInTemplate` (e.g. with `Any` and `OrderedDict`) actually correct?**
  _`UndefinedVariableInTemplate` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `generate_files()` (e.g. with `UndefinedVariableInTemplate` and `find_template()`) actually correct?**
  _`generate_files()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `cookiecutter()` (e.g. with `main()` and `get_user_config()`) actually correct?**
  _`cookiecutter()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Any` (e.g. with `ContextDecodingException` and `EmptyDirNameException`) actually correct?**
  _`Any` has 10 INFERRED edges - model-reasoned connections that need verification._