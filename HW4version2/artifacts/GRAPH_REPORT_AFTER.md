# Graph Report - data/cookiecutter/cookiecutter  (2026-06-19)

## Corpus Check
- 19 files · ~9,398 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 276 nodes · 500 edges · 15 communities (13 shown, 2 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 128 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bb462d16`
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
- [[_COMMUNITY_Community 14|Community 14]]

## God Nodes (most connected - your core abstractions)
1. `CookiecutterException` - 23 edges
2. `cookiecutter()` - 16 edges
3. `generate_files()` - 14 edges
4. `prompt_for_config()` - 12 edges
5. `ContextDecodingException` - 11 edges
6. `OutputDirExistsException` - 11 edges
7. `EmptyDirNameException` - 11 edges
8. `InvalidModeException` - 11 edges
9. `FailedHookException` - 11 edges
10. `UnknownExtension` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Any` --uses--> `CookiecutterException`  [INFERRED]
  template_exceptions.py → exceptions.py
- `TemplateError` --uses--> `CookiecutterException`  [INFERRED]
  template_exceptions.py → exceptions.py
- `Any` --uses--> `InvalidModeException`  [INFERRED]
  main.py → exceptions.py
- `Path` --uses--> `InvalidModeException`  [INFERRED]
  main.py → exceptions.py
- `Path` --uses--> `RepositoryNotFound`  [INFERRED]
  repository.py → exceptions.py

## Import Cycles
- 1-file cycle: `zipfile.py -> zipfile.py`

## Communities (15 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (36): Any, OrderedDict, Validate extra context., validate_extra_context(), Context, Exception, ContextDecodingException, CookiecutterException (+28 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (33): FailedHookException, Exception for hook failures.      Raised when a hook script fails., find_hook(), Any, Path, Functions for discovering and executing various cookiecutter hooks., Execute a script after rendering it with Jinja.      :param script_path: Absolut, Try to find and execute a hook from the specified project directory.      :param (+25 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (33): choose_nested_template(), JsonPrompt, process_json(), prompt_and_delete(), prompt_choice_for_config(), prompt_choice_for_template(), prompt_for_config(), _prompts_from_options() (+25 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (22): JsonifyExtension, Environment, RandomStringExtension, Jinja2 Extension constructor., Jinja2 Extension for dates and times., Jinja2 Extension constructor., Parse datetime template and add datetime value., Jinja2 extension to convert a Python object to JSON. (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (15): cookiecutter(), _patch_import_path_for_repo, Any, Main entry point for the `cookiecutter` command.  The code in this module is als, Path, Run Cookiecutter just as if using it from the command line.      :param template, dump(), get_file_name() (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (18): Confirm, apply_overwrites_to_context(), generate_context(), generate_file(), generate_files(), is_copy_only_path(), Any, Functions for generating a project from a project template. (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (18): Prompt the user to enter a password.      :param question: Question to the user, read_repo_password(), determine_repo_dir(), expand_abbreviations(), is_repo_url(), is_zip_file(), Path, Cookiecutter repository functions. (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (13): ExtensionLoaderMixin, Any, Jinja2 environment and extensions loading., Mixin providing sane loading of extensions specified in a given context.      Th, Initialize the Jinja2 Environment object while loading extensions.          Does, Return list of extensions as str to be passed on to the Jinja2 env.          If, Create strict Jinja2 environment.      Jinja2 environment will raise error on un, Set the standard Cookiecutter StrictEnvironment.          Also loading extension (+5 more)

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

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (7): Any, Template-related exceptions for Cookiecutter., Exception for out-of-scope variables.      Raised when a template uses a variabl, Exception for out-of-scope variables., Text representation of UndefinedVariableInTemplate., UndefinedVariableInTemplate, TemplateError

## Knowledge Gaps
- **4 isolated node(s):** `Parser`, `Output`, `Logger`, `_Raw`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cookiecutter()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **Why does `Extension` connect `Community 3` to `Community 7`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `StrictEnvironment` connect `Community 7` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `CookiecutterException` (e.g. with `Any` and `UndefinedVariableInTemplate`) actually correct?**
  _`CookiecutterException` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `cookiecutter()` (e.g. with `main()` and `get_user_config()`) actually correct?**
  _`cookiecutter()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `generate_files()` (e.g. with `find_template()` and `run_hook_from_repo_dir()`) actually correct?**
  _`generate_files()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `prompt_for_config()` (e.g. with `cookiecutter()` and `UndefinedVariableInTemplate`) actually correct?**
  _`prompt_for_config()` has 3 INFERRED edges - model-reasoned connections that need verification._