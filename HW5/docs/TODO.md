# TODO — HW5: AirLLM Evaluation Pipeline
**Version:** 1.0.0
**Author:** Nagham (naghammnsor@gmail.com)
**Date:** 2026-06-22
**Total Tasks:** 800

Status legend: `[ ]` Not started · `[~]` In progress · `[x]` Done

---

## Phase 0 — Project Bootstrap (T001–T040)

### P0.1 Repository & Tooling Setup
- [ ] T001: Initialize HW5 directory as Python project with `uv init hw5`
- [ ] T002: Create `pyproject.toml` with project metadata (name, version, requires-python)
- [ ] T003: Add all runtime dependencies to `[project.dependencies]` in pyproject.toml
- [ ] T004: Add dev dependencies (pytest, ruff, mypy) to `[dependency-groups.dev]`
- [ ] T005: Run `uv lock` to generate pinned `uv.lock`
- [ ] T006: Create `.gitignore` (venv, __pycache__, .env, *.pyc, results/, *.gguf)
- [ ] T007: Create `.env-example` with placeholder `HF_TOKEN=your_token_here`
- [ ] T008: Create top-level `README.md` skeleton with all section headers
- [ ] T009: Create `src/hw5/__init__.py` with version string
- [ ] T010: Create all `__init__.py` files in sdk/, services/, shared/, tests/

### P0.2 Config Files
- [ ] T011: Create `config/models.json` with two placeholder model entries and HOOK comments
- [ ] T012: Create `config/setup.json` with eval parameters per PLAN §11
- [ ] T013: Create `config/rate_limits.json` with HF download rate limits (5 rps)
- [ ] T014: Validate `models.json` is valid JSON (use `python -m json.tool config/models.json`)
- [ ] T015: Validate `setup.json` is valid JSON
- [ ] T016: Add `config/` to `.gitignore` exclusions EXCEPT the example files

### P0.3 Directory Scaffold
- [ ] T017: Create `data/` directory with `.gitkeep`
- [ ] T018: Create `results/` directory with `.gitkeep`
- [ ] T019: Create `assets/` directory with `.gitkeep`
- [ ] T020: Create `notebooks/` directory with `.gitkeep`
- [ ] T021: Create `tests/unit/` directory
- [ ] T022: Create `tests/integration/` directory
- [ ] T023: Create `tests/conftest.py` with shared fixtures
- [ ] T024: Create `tests/unit/__init__.py`
- [ ] T025: Create `tests/integration/__init__.py`

### P0.4 Linter & Type Checker Setup
- [ ] T026: Add `[tool.ruff]` section to pyproject.toml (line-length=88, select=["E","F","I"])
- [ ] T027: Add `[tool.ruff.lint]` with extend-select for pyflakes and isort
- [ ] T028: Run `ruff check src/` — confirm 0 violations on empty files
- [ ] T029: Add `[tool.mypy]` section to pyproject.toml
- [ ] T030: Add `[tool.pytest.ini_options]` with testpaths, markers, and cov settings

### P0.5 Documentation Skeleton
- [ ] T031: Create `docs/PRD_airllm.md` skeleton with AirLLM-specific requirements
- [ ] T032: Create `docs/PRD_quantization.md` skeleton for quantization mechanism PRD
- [ ] T033: Create `docs/PRD_monitoring.md` skeleton for OS monitoring PRD
- [ ] T034: Create `prompts_ive_used.md` with session 1 prompt logged
- [ ] T035: Add hardware specs section to README.md (CPU, RAM, GPU, OS, Python version)
- [ ] T036: Document local hardware in `docs/hardware_specs.md`
- [ ] T037: Create `CHANGELOG.md` with initial entry for v1.0.0
- [ ] T038: Add MIT license file
- [ ] T039: Create `Makefile` with targets: `test`, `lint`, `run`, `clean`, `report`
- [ ] T040: Verify entire directory structure matches PLAN §7 module file map

---

## Phase 1 — Shared Infrastructure (T041–T120)

### P1.1 Constants Module (`src/hw5/shared/constants.py`)
- [ ] T041: Define `SAMPLE_INTERVAL_S: float = 0.5` in constants.py
- [ ] T042: Define `VRAM_SPIKE_THRESHOLD_MB: float = 500.0`
- [ ] T043: Define `DEFAULT_MAX_TOKENS: int = 200`
- [ ] T044: Define `DEFAULT_OLLAMA_HOST: str = "http://localhost:11434"`
- [ ] T045: Define `SUPPORTED_QUANT_LEVELS: list[str] = ["Q2", "Q4", "Q8"]`
- [ ] T046: Define `FRAMEWORK_COLORS: dict[str, str]` (ollama=steelblue, airllm=darkorange)
- [ ] T047: Define `QUANT_MARKERS: dict[str, str]` (Q2=^, Q4=o, Q8=s)
- [ ] T048: Define `QUANT_LINESTYLES: dict[str, str]` (Q2=dotted, Q4=solid, Q8=dashed)
- [ ] T049: Define `RESULTS_DIR: str = "results"`
- [ ] T050: Define `ASSETS_DIR: str = "assets"`
- [ ] T051: Verify constants.py is under 150 lines
- [ ] T052: Write unit test `test_constants.py` verifying all constants have correct types

### P1.2 Config Loader (`src/hw5/shared/config.py`)
- [ ] T053: Create `Config` dataclass with fields matching `setup.json` schema
- [ ] T054: Implement `Config.load(path: str) -> Config` classmethod
- [ ] T055: Implement JSON deserialization with type coercion for all fields
- [ ] T056: Implement `Config.get(key, default=None)` for safe attribute access
- [ ] T057: Implement `Config.require(key)` that raises `ConfigError` if key missing
- [ ] T058: Create custom `ConfigError(ValueError)` exception class
- [ ] T059: Add validation: `monitor_interval_s > 0`
- [ ] T060: Add validation: `vram_spike_threshold_mb > 0`
- [ ] T061: Add validation: `max_tokens` is a positive integer
- [ ] T062: Add validation: `quantization_levels` is a non-empty list subset of SUPPORTED_QUANT_LEVELS
- [ ] T063: Add validation: `frameworks` is non-empty list with valid framework names
- [ ] T064: Log a warning if `results_dir` does not exist (do not auto-create here)
- [ ] T065: Implement `Config.to_dict()` for serialization
- [ ] T066: Ensure config.py stays under 150 lines; extract validation to `_validators.py` if needed
- [ ] T067: Write `test_config.py` — test happy path load
- [ ] T068: Write test — missing required key raises `ConfigError`
- [ ] T069: Write test — invalid interval value raises `ConfigError`
- [ ] T070: Write test — `get()` returns default for missing key

### P1.3 QuantizationConfig (`src/hw5/shared/quant_config.py`)
- [ ] T071: Create `QuantizationConfig` dataclass with `bits: int` and `label: str`
- [ ] T072: Implement `QuantizationConfig.from_label(label: str) -> QuantizationConfig` factory
- [ ] T073: Implement `validate()` that raises `ValueError` if bits ∉ {2, 4, 8}
- [ ] T074: Implement `to_ollama_tag() -> str` (maps Q4→"q4_K_M", Q8→"q8_0", Q2→"q2_K")
- [ ] T075: Implement `to_airllm_param() -> str` (maps Q4→"4bit", Q8→"8bit", Q2→"2bit")
- [ ] T076: Implement `__str__` returning the label (e.g. "Q4")
- [ ] T077: Implement `__repr__` returning full dataclass repr
- [ ] T078: Write `test_quant_config.py` — test all valid labels
- [ ] T079: Write test — invalid label raises `ValueError`
- [ ] T080: Write test — `to_ollama_tag` returns correct string for each level
- [ ] T081: Write test — `to_airllm_param` returns correct string for each level

### P1.4 ApiGatekeeper (`src/hw5/shared/gatekeeper.py`)
- [ ] T082: Create `ApiGatekeeper` class with token-bucket rate limiter
- [ ] T083: Initialize with `rate: float` (requests/sec) and `burst: int`
- [ ] T084: Implement `execute(fn, *args, **kwargs)` that blocks until token available
- [ ] T085: Implement internal `_refill()` method based on elapsed time
- [ ] T086: Implement `__enter__` / `__exit__` for context-manager usage
- [ ] T087: Add `set_rate(new_rate: float)` to allow runtime reconfiguration
- [ ] T088: Load default rate from `config/rate_limits.json`
- [ ] T089: Add thread lock (`threading.Lock`) to make gatekeeper thread-safe
- [ ] T090: Implement `reset()` method for test isolation
- [ ] T091: Add logging: "Gatekeeper: waiting Xms for rate limit"
- [ ] T092: Write `test_gatekeeper.py` — verify rate limiting delays calls
- [ ] T093: Write test — concurrent calls respect rate limit
- [ ] T094: Write test — `set_rate` changes behavior for subsequent calls
- [ ] T095: Write test — `reset()` clears token bucket state

### P1.5 Runner Protocol (`src/hw5/services/runner_protocol.py`)
- [ ] T096: Define `RunnerProtocol` using `typing.Protocol`
- [ ] T097: Declare `load(model_id: str, quant: QuantizationConfig) -> None`
- [ ] T098: Declare `infer(prompt: str, max_tokens: int) -> InferenceResult`
- [ ] T099: Declare `unload() -> None`
- [ ] T100: Declare `health_check() -> bool`
- [ ] T101: Define `InferenceResult` dataclass with all fields from PLAN §9
- [ ] T102: Add `__post_init__` that computes `tokens_per_sec` if not provided
- [ ] T103: Implement `InferenceResult.to_dict() -> dict`
- [ ] T104: Implement `InferenceResult.from_dict(d: dict) -> InferenceResult`
- [ ] T105: Write `test_runner_protocol.py` — confirm OllamaRunner satisfies protocol (mypy)
- [ ] T106: Write test — confirm AirLLMRunner satisfies protocol
- [ ] T107: Write test — `InferenceResult.to_dict` / `from_dict` roundtrip
- [ ] T108: Write test — `tokens_per_sec` auto-computed correctly from time/count

### P1.6 Module Initialization
- [ ] T109: Export `EvalPipelineSDK` from `src/hw5/sdk/__init__.py` — deferred to Phase 8
- [ ] T110: Export all public service classes from `src/hw5/services/__init__.py`
- [ ] T111: Export `Config`, `ApiGatekeeper`, `QuantizationConfig` from `src/hw5/shared/__init__.py`
- [ ] T112: Export top-level package from `src/hw5/__init__.py`
- [ ] T113: Verify `from hw5.sdk import EvalPipelineSDK` — deferred to Phase 8
- [ ] T114: Verify `from hw5.shared import Config` works
- [ ] T115: Verify `from hw5.services import OllamaRunner` — deferred to Phase 4
- [ ] T116: Run `ruff check src/` after Phase 1 — confirm 0 violations
- [ ] T117: Run `mypy src/hw5/shared/` — confirm 0 errors
- [ ] T118: Run `pytest tests/unit/` after Phase 1 — confirm all tests pass
- [ ] T119: Check file lengths in shared/ — confirm all under 150 lines
- [ ] T120: Commit Phase 1 with message "feat: add shared infrastructure layer"

---

## Phase 2 — Model Registry (T121–T200)

### P2.1 ModelEntry Dataclass
- [ ] T121: Create `ModelEntry` dataclass in `services/model_entry.py`
- [ ] T122: Fields: `name`, `hf_repo_id`, `ollama_tag`, `local_cache`, `size_class`, `ollama_compatible`, `airllm_compatible`, `description`, `param_count_b`, `quant_ollama_tags`, `quant_airllm_params`
- [ ] T123: Add `size_class` validation: must be "small" or "large"
- [ ] T124: Implement `ModelEntry.to_dict()` for serialization
- [ ] T125: Implement `ModelEntry.from_dict(d: dict)` classmethod
- [ ] T126: Add `__str__` returning `name (size_class)`

### P2.2 ModelRegistry Class
- [ ] T127: Create `ModelRegistry` class with `gatekeeper: ApiGatekeeper` dependency
- [ ] T128: Implement `load_config(path: str) -> None` that parses `models.json`
- [ ] T129: Store models in internal `_models: dict[str, ModelEntry]`
- [ ] T130: Implement `get_model(name: str) -> ModelEntry` that raises `KeyError` if not found
- [ ] T131: Implement `list_models() -> list[ModelEntry]`
- [ ] T132: Implement `list_names() -> list[str]`
- [ ] T133: Implement `filter_by_framework(framework: str) -> list[ModelEntry]` returning compatible models only
- [ ] T134: Implement `validate() -> None` checking all HOOK placeholders are replaced
- [ ] T135: Add `validate()` call inside `load_config()`
- [ ] T136: Raise `RegistryError(ValueError)` when HOOK placeholder detected
- [ ] T137: Log model count on successful load: "ModelRegistry: loaded N models"
- [ ] T138: Add `count() -> int` property

### P2.3 HuggingFace Download Integration
- [ ] T139: Add `check_local(model_entry: ModelEntry) -> bool` that checks cache path exists
- [ ] T140: Add `ensure_downloaded(model_entry: ModelEntry) -> None` that calls `snapshot_download` via gatekeeper
- [ ] T141: Import `huggingface_hub.snapshot_download` at module level and wrap in `gatekeeper.execute()`
- [ ] T142: Read `HF_TOKEN` from env via `os.getenv("HF_TOKEN")` (dotenv loaded at startup in main.py)
- [ ] T143: Raise `DownloadError` if download fails
- [ ] T144: Log download start/end with model name and cache path
- [ ] T145: Add `dry_run: bool` param to `ensure_downloaded()` — logs intent without downloading

### P2.4 Registry Tests
- [ ] T146: Write `test_model_registry.py` — test `load_config` with valid JSON
- [ ] T147: Write test — `get_model` returns correct `ModelEntry`
- [ ] T148: Write test — `get_model` raises `KeyError` for unknown name
- [ ] T149: Write test — `filter_by_framework("ollama")` returns only ollama-compatible models
- [ ] T150: Write test — HOOK placeholder in `hf_repo_id` raises `RegistryError`
- [ ] T151: Write test — `list_models()` returns all loaded entries
- [ ] T152: Write test — `count()` returns correct integer
- [ ] T153: Write test — `check_local` returns False when cache path missing
- [ ] T154: Write test — `ensure_downloaded` calls gatekeeper (mock `snapshot_download`)
- [ ] T155: Write test — `ensure_downloaded` raises `DownloadError` on exception
- [ ] T156: Write test — `filter_by_framework("airllm")` returns only airllm-compatible models
- [ ] T157: Write test — invalid `size_class` raises `ValueError`
- [ ] T158: Write test — `to_dict` / `from_dict` roundtrip for `ModelEntry`
- [ ] T159: Write test — `load_config` with empty models list raises `RegistryError`
- [ ] T160: Write test — `list_names()` returns sorted list

### P2.5 Config Hook Documentation
- [ ] T161: `config/models.json` already uses descriptive `_comment` field
- [ ] T162: `_comment` field in models.json explains how to replace hook values
- [ ] T163: Add Llama-3-8B / Llama-3-70B examples to README — deferred to final docs pass
- [ ] T164: Add Mistral-7B / Mixtral examples to README — deferred to final docs pass
- [ ] T165: Document `size_class` field semantics added to PRD_airllm.md
- [ ] T166: Verify registry works with two different valid model entries (unit test)
- [ ] T167: `validate()` called inside `load_config()` — pipeline startup inherits this
- [ ] T168: `RegistryError` message includes "Edit config/models.json" guidance
- [ ] T169: Write integration test stub `tests/integration/test_registry_integration.py`
- [ ] T170: `ruff check` on model_registry.py — 0 violations
- [ ] T171: `model_registry.py` is 123 lines — under 150 ✓
- [ ] T172: `ModelEntry` extracted to `model_entry.py` proactively
- [ ] T173: `pytest tests/unit/test_model_registry.py` — 28 passed
- [ ] T174: Verify registry integrates with SDK layer — deferred to Phase 8
- [ ] T175: `ModelRegistry` added to `services/__init__.py` exports
- [ ] T176: Docstrings on all public methods in registry and model_entry
- [ ] T177: `ModelEntry` added to `services/__init__.py` exports
- [ ] T178: Commit Phase 2 code
- [ ] T179: Update `docs/TODO.md` Phase 2 status to completed
- [ ] T180: Update README.md with model registry hook instructions — deferred to Phase 10

---

## Phase 3 — System Monitor (T181–T260)

### P3.1 MetricsBuffer
- [ ] T181: Create `MetricsBuffer` class using `collections.deque` as backing store
- [ ] T182: Initialize with `maxlen=None` (unbounded for experiment duration)
- [ ] T183: Implement thread-safe `append(sample: dict) -> None` with `threading.Lock`
- [ ] T184: Implement `to_list() -> list[dict]` returning a snapshot copy
- [ ] T185: Implement `clear() -> None`
- [ ] T186: Implement `__len__() -> int`
- [ ] T187: Add `spike_buffer: deque` as separate store for VRAM spike events

### P3.2 MetricsSnapshot Dataclass
- [ ] T188: Create `MetricsSnapshot` dataclass per PLAN §9
- [ ] T189: Fields: `samples`, `spike_events`, `peak_ram_mb`, `peak_vram_mb`, `peak_swap_mb`, `avg_cpu_pct`, `total_disk_read_mb`
- [ ] T190: Implement `MetricsSnapshot.from_buffer(buffer: MetricsBuffer) -> MetricsSnapshot` factory
- [ ] T191: Compute `peak_ram_mb` as max of all `ram` values in samples
- [ ] T192: Compute `peak_vram_mb` as max of all `vram` values in samples
- [ ] T193: Compute `peak_swap_mb` as max of all `swap` values in samples
- [ ] T194: Compute `avg_cpu_pct` as mean of all `cpu` values
- [ ] T195: Compute `total_disk_read_mb` as (max - min) of cumulative `disk_read` values
- [ ] T196: Implement `MetricsSnapshot.to_dict() -> dict`
- [ ] T197: Implement `MetricsSnapshot.from_dict(d: dict) -> MetricsSnapshot`

### P3.3 VRAMSpikeEvent Dataclass
- [ ] T198: Create `VRAMSpikeEvent` dataclass with `timestamp`, `prev_vram_mb`, `curr_vram_mb`, `delta_mb`
- [ ] T199: Implement `VRAMSpikeEvent.to_dict() -> dict`
- [ ] T200: Implement `is_significant(threshold_mb: float) -> bool`

### P3.4 SystemMonitor Class
- [ ] T201: Create `SystemMonitor` class with `config: Config` dependency
- [ ] T202: Initialize `_buffer: MetricsBuffer`, `_spike_buffer: MetricsBuffer`, `_stop_event: threading.Event`
- [ ] T203: Initialize `_thread: threading.Thread` (daemon=True)
- [ ] T204: Implement `start() -> None` that creates and starts the background thread
- [ ] T205: Implement `stop() -> MetricsSnapshot` that sets stop event and joins thread
- [ ] T206: Implement `_run() -> None` — the thread main loop
- [ ] T207: In `_run()`: loop until stop_event is set, sleeping `config.monitor_interval_s`
- [ ] T208: In each iteration: call `_sample()` and append to buffer
- [ ] T209: Implement `_sample() -> dict` that calls all psutil/pynvml functions
- [ ] T210: In `_sample()`: call `psutil.cpu_percent(interval=None)` for CPU %
- [ ] T211: In `_sample()`: call `psutil.virtual_memory().used / 1e6` for RAM MB
- [ ] T212: In `_sample()`: call `psutil.swap_memory().used / 1e6` for swap MB
- [ ] T213: In `_sample()`: call `psutil.disk_io_counters().read_bytes / 1e6` for disk read MB
- [ ] T214: Implement `_sample_vram() -> float` — returns 0.0 if no CUDA GPU
- [ ] T215: In `_sample_vram()`: try `pynvml.nvmlDeviceGetMemoryInfo()`, except return 0.0
- [ ] T216: In `_sample_vram()`: alternatively use `torch.cuda.memory_allocated() / 1e6`
- [ ] T217: Add timestamp to each sample: `time.perf_counter()` relative to start
- [ ] T218: Implement `_detect_spike(prev: dict, curr: dict) -> bool` per PLAN spike rule
- [ ] T219: When spike detected: create `VRAMSpikeEvent` and append to `_spike_buffer`
- [ ] T220: Log spike events: "VRAM spike detected: +{delta:.1f} MB at t={ts:.2f}s"

### P3.5 NVML Initialization
- [ ] T221: Implement `_init_nvml() -> bool` that tries `pynvml.nvmlInit()` and returns False on failure
- [ ] T222: Call `_init_nvml()` in `SystemMonitor.__init__()`, store `_nvml_available: bool`
- [ ] T223: If `_nvml_available=False`, log "No NVIDIA GPU detected — VRAM metrics disabled"
- [ ] T224: Implement `_shutdown_nvml() -> None` called in `stop()` if nvml was initialized
- [ ] T225: Handle case where multiple monitors initialize nvml (nvml is process-global)

### P3.6 Real-time Display (Optional — rich table)
- [ ] T226: Implement `get_live_table() -> rich.table.Table` returning current metrics as Rich table
- [ ] T227: Add columns: Timestamp, CPU%, RAM MB, Swap MB, VRAM MB, Disk Read MB
- [ ] T228: Implement `print_latest(n: int = 5)` printing last n samples to stdout
- [ ] T229: Add `--live` CLI flag that calls `print_latest` every second during evaluation

### P3.7 Monitor Tests
- [ ] T230: Write `test_monitor.py` — verify monitor starts and stops cleanly
- [ ] T231: Write test — buffer contains samples after 1 second run
- [ ] T232: Write test — `stop()` returns `MetricsSnapshot` with non-zero `avg_cpu_pct`
- [ ] T233: Write test — spike detection fires when VRAM increases by >threshold
- [ ] T234: Write test — spike not detected when VRAM increases by <threshold
- [ ] T235: Write test — `_sample_vram()` returns 0.0 when nvml unavailable (mock pynvml)
- [ ] T236: Write test — `MetricsSnapshot.from_buffer` computes peaks correctly
- [ ] T237: Write test — `MetricsBuffer` is thread-safe under concurrent append
- [ ] T238: Write test — monitor stop event terminates thread within 2s
- [ ] T239: Write test — `to_dict` / `from_dict` roundtrip for `MetricsSnapshot`
- [ ] T240: Write test — `VRAMSpikeEvent.is_significant` returns True above threshold

### P3.8 Monitor Integration
- [ ] T241: Add `SystemMonitor` to `services/__init__.py` exports
- [ ] T242: Confirm monitor.py under 150 lines (split buffer to metrics_buffer.py if needed)
- [ ] T243: Add docstrings to all public methods in SystemMonitor
- [ ] T244: Write performance test — 1000 samples/buffer does not exceed 50 MB RAM overhead
- [ ] T245: Run `ruff check` on monitor.py — 0 violations
- [ ] T246: Commit Phase 3 code with "feat: add OS page monitoring module"
- [ ] T247: Update TODO Phase 3 statuses
- [ ] T248: Add monitoring architecture diagram to `docs/PRD_monitoring.md`
- [ ] T249: Document VRAM spike threshold in `config/setup.json` and README
- [ ] T250: Document CPU-only fallback behavior in README

### P3.9 Additional Monitoring Extensions
- [ ] T251: Add `peak_disk_write_mb` field to `MetricsSnapshot`
- [ ] T252: Add process-specific memory tracking via `psutil.Process().memory_info()`
- [ ] T253: Track Python GC pause duration during inference as additional metric
- [ ] T254: Track number of OS page faults via `psutil.Process().num_page_faults()` (Windows) or `/proc/self/stat` (Linux)
- [ ] T255: Add `page_faults_delta` to MetricsSnapshot
- [ ] T256: Add per-CPU-core breakdown to samples (psutil.cpu_percent(percpu=True))
- [ ] T257: Add `cpu_core_peaks: list[float]` to MetricsSnapshot
- [ ] T258: Add network I/O tracking (bytes_sent/recv via psutil.net_io_counters)
- [ ] T259: Implement `MonitorContext` context manager wrapping start/stop for clean usage
- [ ] T260: Write tests for all new extended metrics

---

## Phase 4 — Ollama Runner (T261–T340)

### P4.1 OllamaRunner Class
- [ ] T261: Create `OllamaRunner` in `services/ollama_runner.py`
- [ ] T262: Initialize with `config: Config` and `gatekeeper: ApiGatekeeper`
- [ ] T263: Implement `health_check() -> bool` that pings `ollama_host/api/tags`
- [ ] T264: Implement `load(model_id: str, quant: QuantizationConfig) -> None`
- [ ] T265: In `load()`: resolve the Ollama model tag from `model_id` + quant.to_ollama_tag()
- [ ] T266: In `load()`: call `ollama.pull(tag)` via gatekeeper to download GGUF if not cached
- [ ] T267: In `load()`: store `_current_model: str` and `_current_quant: QuantizationConfig`
- [ ] T268: Log load start/end with model tag and download size if available
- [ ] T269: Raise `RunnerError` if `health_check()` fails before load
- [ ] T270: Implement `infer(prompt: str, max_tokens: int = 200) -> InferenceResult`
- [ ] T271: In `infer()`: record `t_start = time.perf_counter()`
- [ ] T272: In `infer()`: call `ollama.generate(model=tag, prompt=prompt, stream=True)` via gatekeeper
- [ ] T273: In `infer()`: capture first token time on first streamed chunk
- [ ] T274: In `infer()`: accumulate full response text and count tokens
- [ ] T275: In `infer()`: record `t_end = time.perf_counter()`
- [ ] T276: In `infer()`: construct and return `InferenceResult` with all timing fields
- [ ] T277: Implement `unload() -> None` that calls `ollama.delete(tag)` to free GGUF memory
- [ ] T278: Reset `_current_model` and `_current_quant` to None in `unload()`
- [ ] T279: Add `get_model_info() -> dict` that calls `ollama.show(tag)`
- [ ] T280: Handle `ollama.ResponseError` and wrap in `RunnerError`

### P4.2 Ollama Server Management
- [ ] T281: Add `ensure_server_running() -> None` that checks health and optionally starts Ollama
- [ ] T282: Implement `_start_server() -> subprocess.Popen` that runs `ollama serve` as subprocess
- [ ] T283: Implement `_wait_for_server(timeout_s: float = 30.0) -> bool`
- [ ] T284: Store server process in `_server_proc: subprocess.Popen | None`
- [ ] T285: Implement `stop_server() -> None` that terminates `_server_proc` if we started it
- [ ] T286: Add `managed_server: bool` flag — only auto-start if True (config-controlled)
- [ ] T287: Log server startup: "Starting Ollama server at {host}"
- [ ] T288: Add 5-second retry loop in `_wait_for_server` with exponential backoff

### P4.3 Quantization Tag Mapping
- [ ] T289: Define `OLLAMA_TAG_MAP: dict[str, str]` mapping model_id + quant to Ollama pull tag
- [ ] T290: Implement `resolve_ollama_tag(hf_repo_id: str, quant: QuantizationConfig) -> str`
- [ ] T291: Support common HuggingFace → Ollama name translations (e.g. "meta-llama/Llama-3" → "llama3")
- [ ] T292: Read tag overrides from `config/models.json` `ollama_tag_override` field
- [ ] T293: Fall back to constructing tag as `{model_name}:{quant_tag}` when no override

### P4.4 Ollama Runner Tests
- [ ] T294: Write `test_ollama_runner.py` — mock `ollama.generate`, verify InferenceResult structure
- [ ] T295: Write test — `health_check()` returns True when mock server responds 200
- [ ] T296: Write test — `health_check()` returns False on connection error
- [ ] T297: Write test — `load()` calls `ollama.pull` with correct tag
- [ ] T298: Write test — `load()` raises `RunnerError` when server not healthy
- [ ] T299: Write test — `infer()` captures first_token_latency correctly
- [ ] T300: Write test — `infer()` returns correct `tokens_per_sec`
- [ ] T301: Write test — `unload()` calls `ollama.delete` with current tag
- [ ] T302: Write test — `resolve_ollama_tag` returns override when config provides one
- [ ] T303: Write test — streaming response accumulates full text
- [ ] T304: Write test — `RunnerError` raised on `ollama.ResponseError`
- [ ] T305: Write test — `ensure_server_running` does not start server if already healthy
- [ ] T306: Write test — `get_model_info` returns dict with model metadata
- [ ] T307: Write test — gatekeeper is called for every `ollama.generate` call
- [ ] T308: Write test — `infer()` raises `RunnerError` if no model loaded
- [ ] T309: Write test — token count correctly extracted from Ollama response
- [ ] T310: Write test — `framework` field in InferenceResult equals "ollama"

### P4.5 Ollama Integration & Cleanup
- [ ] T311: Add `OllamaRunner` to `services/__init__.py` exports
- [ ] T312: Confirm ollama_runner.py under 150 lines; split server management to `ollama_server.py`
- [ ] T313: Add docstrings to all public methods
- [ ] T314: Run `ruff check` on ollama_runner.py — 0 violations
- [ ] T315: Write integration test stub `tests/integration/test_ollama_integration.py`
- [ ] T316: Mark integration tests with `@pytest.mark.integration`
- [ ] T317: Add skip condition: `@pytest.mark.skipif(not shutil.which("ollama"), reason="ollama not installed")`
- [ ] T318: Implement integration test: pull smallest available model (e.g. llama3:8b-q4)
- [ ] T319: Implement integration test: run single inference and verify non-empty output
- [ ] T320: Implement integration test: measure first_token_latency > 0

### P4.6 Additional Ollama Features
- [ ] T321: Add `batch_infer(prompts: list[str]) -> list[InferenceResult]` for multi-prompt evaluation
- [ ] T322: Add temperature parameter to `infer()` for reproducible generation
- [ ] T323: Add seed parameter to `infer()` for reproducible outputs
- [ ] T324: Store inference parameters in `InferenceResult` metadata dict
- [ ] T325: Implement `get_loaded_models() -> list[str]` via `ollama.list()`
- [ ] T326: Add memory estimation before load: log expected GGUF file size
- [ ] T327: Add `OllamaRunnerError(RunnerError)` subclass for Ollama-specific errors
- [ ] T328: Log token-per-second in real-time during streaming inference
- [ ] T329: Write test for `batch_infer` — correct number of results returned
- [ ] T330: Write test for temperature/seed parameters passed to ollama.generate
- [ ] T331: Document Ollama installation steps in README
- [ ] T332: Document how to manually pull a model: `ollama pull llama3:8b-q4_0`
- [ ] T333: Document expected Ollama output format in `docs/PRD_monitoring.md`
- [ ] T334: Commit Ollama runner with "feat: implement OllamaRunner with streaming"
- [ ] T335: Update TODO Phase 4 statuses
- [ ] T336: Verify OllamaRunner satisfies RunnerProtocol via mypy
- [ ] T337: Add `OllamaRunner` section to PLAN.md component diagram
- [ ] T338: Add GGUF quantization tag table to `docs/PRD_quantization.md`
- [ ] T339: Write unit test verifying `to_ollama_tag` produces valid GGUF suffixes
- [ ] T340: Verify all Ollama unit tests pass: `pytest tests/unit/test_ollama_runner.py`

---

## Phase 5 — AirLLM Runner (T341–T440)

### P5.1 AirLLMRunner Class
- [x] T341: Create `AirLLMRunner` in `services/airllm_runner.py`
- [x] T342: Initialize with `config: Config` and `gatekeeper: ApiGatekeeper`
- [x] T343: Initialize `_model: AirLLMAuto | None = None`
- [x] T344: Implement `health_check() -> bool` — returns True if airllm importable and cache writable
- [x] T345: Implement `load(model_id: str, quant: QuantizationConfig) -> None`
- [x] T346: In `load()`: call `AirLLMAuto.from_pretrained(model_id, compression=quant.to_airllm_param())` via gatekeeper
- [x] T347: In `load()`: store `_model`, `_model_id`, `_quant`
- [x] T348: Log load start: "AirLLM: loading {model_id} with {quant} compression"
- [x] T349: Log load end with elapsed seconds
- [x] T350: Raise `RunnerError` if `AirLLMAuto.from_pretrained` raises any exception
- [x] T351: Implement `infer(prompt: str, max_tokens: int = 200) -> InferenceResult`
- [x] T352: In `infer()`: tokenize prompt using model's tokenizer
- [x] T353: In `infer()`: record `t_start = time.perf_counter()`
- [x] T354: In `infer()`: call `_model.generate(input_ids, max_new_tokens=max_tokens)`
- [x] T355: In `infer()`: decode output tokens, stripping prompt tokens
- [x] T356: In `infer()`: measure first token latency (first batch of generated tokens)
- [x] T357: In `infer()`: count tokens generated (len(output_ids) - len(input_ids))
- [x] T358: In `infer()`: record `t_end` and compute `tokens_per_sec`
- [x] T359: In `infer()`: wrap entire call in `gatekeeper.execute()`
- [x] T360: Construct and return `InferenceResult` with `framework="airllm"`
- [x] T361: Implement `unload() -> None` that deletes `_model` and calls `torch.cuda.empty_cache()`
- [x] T362: In `unload()`: call `gc.collect()` after model deletion
- [x] T363: Log: "AirLLM: unloaded model, freed GPU cache"

### P5.2 AirLLM Layer Streaming Details
- [ ] T364: Add `_layer_count: int` field tracking how many transformer layers were streamed
- [ ] T365: Implement `get_layer_info() -> dict` returning model depth and layer size
- [ ] T366: Log layer-streaming activity: "AirLLM: streaming layer {i}/{n} from disk"
- [ ] T367: Track peak VRAM during layer streaming via `torch.cuda.max_memory_allocated()`
- [ ] T368: Store `peak_layer_vram_mb` in `InferenceResult.metadata` dict
- [ ] T369: Implement `estimate_disk_reads_mb() -> float` based on layer count × layer size
- [ ] T370: Store `estimated_disk_reads_mb` in `InferenceResult.metadata`
- [ ] T371: Add `airllm_version: str` to `InferenceResult.metadata`

### P5.3 Tokenizer Management
- [x] T372: Extract tokenizer loading into `_load_tokenizer(model_id: str) -> AutoTokenizer`
- [x] T373: Cache tokenizer instance to avoid reloading between infer calls
- [x] T374: Handle special tokens correctly: `pad_token = eos_token` if pad_token missing
- [x] T375: Implement `count_prompt_tokens(prompt: str) -> int` utility method
- [x] T376: Add `prompt_token_count` to `InferenceResult`
- [ ] T377: Warn if prompt is very long (>512 tokens): "Long prompt may slow layer streaming"

### P5.4 Quantization Mapping
- [x] T378: Implement `_resolve_compression(quant: QuantizationConfig) -> str | None`
- [x] T379: Map Q4 → "4bit", Q8 → "8bit", Q2 → "2bit" (via `quant.to_airllm_param()`)
- [x] T380: Validate that AirLLM supports the requested compression level
- [x] T381: Log: "AirLLM: using compression={compression}"
- [x] T382: Handle case where Q2 is not supported by AirLLM — raise `UnsupportedQuantError`

### P5.5 AirLLM Runner Tests
- [x] T383: Write `test_airllm_runner.py` — mock `AirLLMAuto.from_pretrained`
- [x] T384: Write test — `load()` calls `AirLLMAuto.from_pretrained` with correct args
- [x] T385: Write test — `load()` raises `RunnerError` when AirLLMAuto fails
- [x] T386: Write test — `infer()` returns correct `InferenceResult` structure
- [x] T387: Write test — `infer()` sets `framework="airllm"`
- [x] T388: Write test — `unload()` deletes model and calls empty_cache (mock torch.cuda)
- [x] T389: Write test — `health_check()` returns True when airllm importable
- [x] T390: Write test — `count_prompt_tokens` returns integer > 0 for non-empty prompt
- [x] T391: Write test — `_resolve_compression` returns "4bit" for Q4
- [x] T392: Write test — `UnsupportedQuantError` raised for unsupported quant level
- [x] T393: Write test — gatekeeper wraps the `generate` call
- [x] T394: Write test — `unload()` with no model loaded is a no-op (no exception)
- [x] T395: Write test — tokenizer cached between successive `infer()` calls
- [x] T396: Write test — `tokens_per_sec` computed correctly from timing data
- [x] T397: Write test — `peak_layer_vram_mb` stored in metadata
- [x] T398: Write test — `prompt_token_count` field populated in InferenceResult
- [x] T399: Write test — RunnerProtocol satisfied by AirLLMRunner (structural check)
- [x] T400: Write test — `airllm_version` populated in metadata

### P5.6 AirLLM CPU Fallback
- [x] T401: Detect CUDA availability with `torch.cuda.is_available()`
- [x] T402: If no CUDA: call `AirLLMAuto.from_pretrained(device="cpu")` (if supported)
- [x] T403: Log: "AirLLM: no GPU detected, running on CPU (slower)"
- [x] T404: Set `cpu_only=True` in returned `InferenceResult` metadata
- [ ] T405: Document CPU inference expected performance in README

### P5.7 AirLLM Integration & Cleanup
- [x] T406: Add `AirLLMRunner` to `services/__init__.py` exports
- [x] T407: Confirm airllm_runner.py under 150 lines
- [ ] T408: Extract tokenizer management to `airllm_tokenizer.py` if file exceeds 150 lines
- [x] T409: Run `ruff check` on airllm_runner.py — 0 violations
- [x] T410: Add docstrings to all public methods
- [x] T411: Write integration test stub `tests/integration/test_airllm_integration.py`
- [x] T412: Mark integration tests with `@pytest.mark.integration`
- [x] T413: Add skip condition based on airllm importability and HF_TOKEN presence
- [x] T414: Implement integration test: load small model, run single inference
- [x] T415: Implement integration test: verify layer streaming by checking disk read metrics
- [x] T416: Implement integration test: verify VRAM stays below 8 GB for 7B model with Q4
- [ ] T417: Add `AirLLMRunner` section to PLAN.md component diagram
- [ ] T418: Add AirLLM layer-streaming explanation to `docs/PRD_airllm.md`
- [ ] T419: Document `compression` parameter options in PRD_airllm.md
- [ ] T420: Document expected AirLLM performance vs. Ollama in PRD_airllm.md
- [ ] T421: Write original experiment idea: measure layer-streaming throughput vs. SSD speed
- [ ] T422: Write original experiment idea: compare CPU-RAM vs. GPU-VRAM paging strategies
- [ ] T423: Commit AirLLM runner with "feat: implement AirLLMRunner with layer streaming"
- [x] T424: Update TODO Phase 5 statuses
- [x] T425: Verify AirLLMRunner passes all unit tests
- [ ] T426: Add `UnsupportedQuantError` to shared exceptions module
- [ ] T427: Document AirLLM installation steps in README
- [ ] T428: Document HF_TOKEN requirement for gated models
- [ ] T429: Verify both runners have identical public interfaces (RunnerProtocol check)
- [ ] T430: Add runner comparison table to PLAN.md

### P5.8 Runner Factory
- [x] T431: Create `RunnerFactory` class in `services/runner_factory.py`
- [x] T432: Implement `create(framework: str, config: Config, gatekeeper: ApiGatekeeper) -> RunnerProtocol`
- [x] T433: Map "ollama" → `OllamaRunner(config, gatekeeper)`
- [x] T434: Map "airllm" → `AirLLMRunner(config, gatekeeper)`
- [x] T435: Raise `ValueError` for unknown framework name
- [x] T436: Write `test_runner_factory.py` — correct runner type returned per framework string
- [x] T437: Write test — unknown framework raises `ValueError`
- [x] T438: Add `RunnerFactory` to `services/__init__.py` exports
- [x] T439: Verify runner_factory.py under 150 lines
- [x] T440: Run `ruff check` on runner_factory.py — 0 violations

---

## Phase 6 — Evaluation Loop (T441–T540)

### P6.1 CellResult Dataclass
- [x] T441: Create `CellResult` dataclass in `services/eval_loop.py`
- [x] T442: Fields: `inference`, `metrics`, `cell_id`, `started_at`, `finished_at`, `cpu_only`
- [x] T443: Implement `CellResult.to_dict() -> dict`
- [x] T444: Implement `CellResult.from_dict(d: dict) -> CellResult`
- [x] T445: Add `duration_s` property: `finished_at - started_at` as float seconds
- [x] T446: Add `cell_id` format: `{model_name}__{framework}__{quant}` (double underscore separator)

### P6.2 EvaluationLoop Class
- [x] T447: Create `EvaluationLoop` in `services/eval_loop.py`
- [x] T448: Initialize with `config: Config`, `registry: ModelRegistry`, `gatekeeper: ApiGatekeeper`
- [x] T449: Implement `iter_cells()` that yields (model_entry, framework, quant_config) tuples
- [x] T450: Implement iteration order per PLAN §5 execution order
- [x] T451: Implement `run() -> list[CellResult]` that calls `run_cell` for each cell
- [x] T452: Implement `run_cell(model, framework, quant) -> CellResult`
- [x] T453: In `run_cell()`: instantiate runner via `RunnerFactory.create(framework, ...)`
- [x] T454: In `run_cell()`: instantiate `SystemMonitor(config)` and call `monitor.start()`
- [x] T455: In `run_cell()`: call `runner.load(model.hf_repo_id, quant)` wrapped in try/except
- [x] T456: In `run_cell()`: call `runner.infer(config.eval_prompt, config.max_tokens)`
- [x] T457: In `run_cell()`: call `runner.unload()`
- [x] T458: In `run_cell()`: call `monitor.stop()` returning `MetricsSnapshot`
- [x] T459: In `run_cell()`: construct `CellResult` and call `save_result(result)`
- [x] T460: In `run_cell()`: on exception, call `monitor.stop()` in finally block
- [x] T461: Implement `save_result(result: CellResult) -> Path`
- [x] T462: In `save_result()`: create `results/<timestamp>/` if not exists
- [x] T463: In `save_result()`: write `cell_{cell_id}.json` with result.to_dict()
- [x] T464: Return the saved file path from `save_result()`

### P6.3 Resume Functionality
- [x] T465: Implement `load_existing_results(results_dir: str) -> dict[str, CellResult]`
- [x] T466: In `load_existing_results()`: scan dir for `cell_*.json` files
- [x] T467: Parse each JSON back to `CellResult` via `from_dict()`
- [x] T468: Return dict keyed by `cell_id`
- [x] T469: In `run()`: if `config.resume=True`, call `load_existing_results()` first
- [x] T470: Skip cells whose `cell_id` already in loaded results dict
- [x] T471: Log: "Resuming — skipping {n} completed cells, running {m} remaining"
- [x] T472: Merge resumed results with newly run results in final return list

### P6.4 Progress Tracking
- [x] T473: Import `rich.progress` and create a `Progress` context manager in `run()`
- [x] T474: Add task with total = len(cells), description = "Evaluating cells"
- [x] T475: Call `progress.advance(task)` after each `run_cell()` completes
- [x] T476: Display current cell_id in progress bar description
- [x] T477: Display elapsed time and ETA in progress bar
- [x] T478: Display peak RAM from latest completed cell in progress bar

### P6.5 Error Handling & Cell Failure Recovery
- [x] T479: Catch `RunnerError` in `run_cell()` and record failure in `CellResult`
- [x] T480: Add `failed: bool` and `error_message: str` fields to `CellResult`
- [x] T481: On cell failure: save partial result (with failure info) and continue loop
- [x] T482: Log: "Cell {cell_id} FAILED: {error}" at ERROR level
- [x] T483: After all cells: log summary of passed/failed counts
- [x] T484: Failed cells are included in results but excluded from plot data
- [x] T485: Implement `get_successful_results() -> list[CellResult]` filter method

### P6.6 Evaluation Loop Tests
- [x] T486: Write `test_eval_loop.py` — test `iter_cells` yields correct combinations
- [x] T487: Write test — total cells = len(models) × len(frameworks) × len(quants)
- [x] T488: Write test — `run_cell` calls runner.load, runner.infer, runner.unload in order
- [x] T489: Write test — `run_cell` calls monitor.start before runner.load
- [x] T490: Write test — `run_cell` calls monitor.stop after runner.unload
- [x] T491: Write test — `save_result` creates JSON file with correct filename
- [x] T492: Write test — `load_existing_results` returns CellResult from existing JSON
- [x] T493: Write test — resume skips cells with existing JSON files
- [x] T494: Write test — cell failure is caught and stored as failed CellResult
- [x] T495: Write test — failed cell does not stop remaining cells from running
- [x] T496: Write test — `cell_id` format matches `{model}__{fw}__{quant}` pattern
- [x] T497: Write test — `duration_s` property computed correctly
- [x] T498: Write test — `get_successful_results()` excludes failed cells
- [x] T499: Write test — monitor.stop called in finally block even on failure
- [x] T500: Write test — CellResult.to_dict / from_dict roundtrip
- [x] T501: Write test — progress bar task added with correct total
- [x] T502: Write test — `run()` returns all results including failed ones
- [x] T503: Write test — `save_result` returns existing path if file already exists
- [x] T504: Confirm eval_loop.py under 150 lines; extract persistence to `cell_persistence.py` if needed
- [x] T505: Add `EvaluationLoop` and `CellResult` to `services/__init__.py` exports
- [x] T506: Run `ruff check` on eval_loop.py — 0 violations
- [x] T507: Add docstrings to all public methods
- [x] T508: Commit evaluation loop with "feat: implement full evaluation loop with resume"
- [x] T509: Update TODO Phase 6 statuses
- [x] T510: Verify all unit tests pass: `pytest tests/unit/test_eval_loop.py`

### P6.7 Additional Loop Features
- [x] T511: Add `--cell` CLI flag to run a single specific cell: `--cell model_a__ollama__Q4`
- [x] T512: Add `--dry-run` flag that logs cells without running them
- [x] T513: Add `--models` filter flag: `--models model_a` to run only specified models
- [x] T514: Add `--frameworks` filter flag: `--frameworks airllm`
- [x] T515: Add `--quants` filter flag: `--quants Q4,Q8`
- [x] T516: Implement `filter_cells(models, frameworks, quants) -> list` in EvaluationLoop
- [x] T517: Write test — filter_cells with `models=["model_a"]` excludes model_b cells
- [x] T518: Write test — filter_cells with multiple frameworks includes both
- [ ] T519: Write test — `--dry-run` does not create any result files
- [ ] T520: Add timing metrics to loop: total_elapsed_s, avg_cell_duration_s

---

## Phase 7 — Plotter & Summary (T521–T620)

### P7.1 Plotter Class
- [x] T521: Create `Plotter` in `services/plotter.py`
- [x] T522: Initialize with `results: list[CellResult]`, `config: Config`
- [x] T523: Add `_fig_size: tuple = (12, 8)` default figure size
- [x] T524: Add `_dpi: int = 300` default DPI
- [x] T525: Implement `_get_df() -> pd.DataFrame` converting results to DataFrame
- [x] T526: In `_get_df()`: extract tokens_per_sec, peak_ram_mb, peak_vram_mb, avg_cpu_pct per cell
- [x] T527: Add columns: model, framework, quant, tokens_per_sec, peak_ram_mb, peak_vram_mb, peak_swap_mb, failed
- [x] T528: Filter out failed cells in `_get_df()`
- [x] T529: Implement `save_all() -> list[Path]` that calls all four plot methods

### P7.2 Plot 1 — Heatmap
- [x] T530: Implement `heatmap(ax=None) -> Figure`
- [x] T531: Create a pivot table: rows=framework, columns=quant, values=tokens_per_sec
- [x] T532: Use `seaborn.heatmap` with `cmap="RdYlGn"`, `annot=True`, `fmt=".1f"`
- [x] T533: Create one subplot per model (side by side)
- [x] T534: Title each subplot with model name and size class
- [x] T535: Add colorbar label: "Tokens/sec"
- [x] T536: Save to `assets/heatmap.png` and `assets/heatmap.svg`
- [x] T537: Return the Figure object for embedding in report

### P7.3 Plot 2 — RAM Timeline
- [x] T538: Implement `ram_timeline(ax=None) -> Figure`
- [x] T539: For each successful CellResult, extract `metrics.samples` time series
- [x] T540: Plot RAM used (MB) vs. time (s) for each cell
- [x] T541: Set line color from `FRAMEWORK_COLORS[framework]`
- [x] T542: Set linestyle from `QUANT_LINESTYLES[quant]`
- [x] T543: Add vertical dashed line at `load_end` time (annotated "model loaded")
- [x] T544: Add vertical dotted line at `first_token` time (annotated "first token")
- [x] T545: Add legend with framework + quant + model in label
- [x] T546: Set x-label: "Time (seconds)", y-label: "RAM Used (MB)"
- [x] T547: Save to `assets/ram_timeline.png` and `assets/ram_timeline.svg`

### P7.4 Plot 3 — Peak VRAM Bar Chart
- [x] T548: Implement `vram_bar_chart(ax=None) -> Figure`
- [x] T549: Group results by (model, quant) on x-axis
- [x] T550: Plot bars colored by framework (blue=Ollama, orange=AirLLM)
- [x] T551: Add error bars for std dev if multiple runs per cell
- [x] T552: X-tick labels: "{model_name}\n{quant}"
- [x] T553: Y-label: "Peak VRAM (MB)"
- [x] T554: Add horizontal dashed line at GPU total VRAM if detectable via pynvml
- [x] T555: Annotate each bar with exact MB value
- [x] T556: Save to `assets/vram_bar.png` and `assets/vram_bar.svg`

### P7.5 Plot 4 — Trade-off Scatter
- [x] T557: Implement `tradeoff_scatter(ax=None) -> Figure`
- [x] T558: X-axis: peak_ram_mb, Y-axis: tokens_per_sec
- [x] T559: Color each point by framework using `FRAMEWORK_COLORS`
- [x] T560: Set marker shape from `QUANT_MARKERS[quant]`
- [x] T561: Scale marker size by model size_class (large=200, small=100)
- [x] T562: Annotate each point with `{model_name}/{quant}` label (offset to avoid overlap)
- [x] T563: Implement `_find_pareto_front(df) -> pd.DataFrame` returning Pareto-optimal points
- [x] T564: Draw Pareto frontier as a step line in grey
- [x] T565: Add legend for framework colors and quant markers
- [x] T566: Save to `assets/tradeoff_scatter.png` and `assets/tradeoff_scatter.svg`

### P7.6 SummaryGenerator
- [x] T567: Create `SummaryGenerator` in `services/summary.py`
- [x] T568: Initialize with `results: list[CellResult]`
- [x] T569: Implement `summarize_heatmap() -> str` returning 3–4 sentences
- [x] T570: In `summarize_heatmap()`: find max tokens/sec cell and min tokens/sec cell
- [x] T571: In `summarize_heatmap()`: compute speed ratio between Q4 and Q2 for best framework
- [x] T572: Template: "Across all quantization levels, {winner_fw} at {winner_quant} achieved..."
- [x] T573: Implement `summarize_timeline() -> str` returning 3–4 sentences
- [x] T574: In `summarize_timeline()`: find cell with highest peak RAM and with lowest peak RAM
- [x] T575: Compute swap pressure: which cells triggered >0 MB swap usage
- [x] T576: Template: "RAM pressure peaked at {peak:.1f} MB during {cell_id}..."
- [x] T577: Implement `summarize_vram() -> str` returning 3–4 sentences
- [x] T578: In `summarize_vram()`: identify which framework used less VRAM on average
- [x] T579: Compute total VRAM spike events across all cells
- [x] T580: Template: "AirLLM's layer-streaming kept peak VRAM at {x:.0f} MB vs..."
- [x] T581: Implement `summarize_tradeoff() -> str` returning 3–4 sentences
- [x] T582: Identify Pareto-optimal cells (most tokens/sec for given RAM budget)
- [x] T583: Identify worst trade-off cell
- [x] T584: Template: "The trade-off surface reveals that {quant} quantization..."
- [x] T585: Implement `generate_all() -> dict[str, str]` returning all four summaries

### P7.7 HTML Report Generator
- [x] T586: Create `ReportGenerator` in `services/report.py`
- [x] T587: Initialize with `summaries: dict`, `plot_paths: dict`, `results: list[CellResult]`
- [x] T588: Implement `to_html() -> str` generating full HTML report string
- [x] T589: Embed plots as base64-encoded data URIs (no external file references)
- [x] T590: Include metrics table: one row per cell, columns = all key metrics
- [x] T591: Include summary paragraphs below each plot
- [x] T592: Include hardware specs section (read from `docs/hardware_specs.md`)
- [x] T593: Include experiment metadata: timestamp, config snapshot, total duration
- [x] T594: Save report to `assets/report.html`
- [x] T595: Add CSS for table striping, responsive layout, and print media query
- [x] T596: Add section anchors for grader navigation

### P7.8 Plotter Tests
- [x] T597: Write `test_plotter.py` — verify `_get_df()` returns correct columns
- [x] T598: Write test — heatmap returns Figure without exception (mock seaborn)
- [x] T599: Write test — ram_timeline returns Figure without exception
- [x] T600: Write test — vram_bar_chart returns Figure without exception
- [x] T601: Write test — tradeoff_scatter returns Figure without exception
- [x] T602: Write test — `save_all()` returns list of 8 paths (4 plots × 2 formats)
- [x] T603: Write test — failed cells excluded from DataFrame
- [x] T604: Write test — `_find_pareto_front` returns correct subset of points
- [x] T605: Write `test_summary.py` — verify summarize_heatmap returns non-empty string
- [x] T606: Write test — summarize_timeline identifies highest peak RAM correctly
- [x] T607: Write test — summarize_vram mentions AirLLM framework name
- [x] T608: Write test — generate_all returns dict with all four keys
- [x] T609: Write test — `to_html()` contains all four plot img tags
- [x] T610: Confirm plotter.py under 150 lines; extract each plot to separate file if needed
- [x] T611: Run `ruff check` on plotter.py, summary.py, report.py — 0 violations
- [x] T612: Add docstrings to all public methods in Plotter and SummaryGenerator
- [x] T613: Commit plotter and summary with "feat: add visualization and summary generation"
- [x] T614: Update TODO Phase 7 statuses
- [x] T615: Verify all plotter unit tests pass
- [x] T616: Add `Plotter`, `SummaryGenerator`, `ReportGenerator` to services exports
- [x] T617: Add pandas to pyproject.toml dependencies
- [x] T618: Add `save_csv(path) -> Path` method to Plotter that exports raw data to CSV
- [x] T619: Write test — `save_csv` produces valid CSV with correct columns
- [ ] T620: Document plot specifications in PLAN.md §10 (link from TODO)

---

## Phase 8 — SDK Layer & CLI (T621–T680)

### P8.1 EvalPipelineSDK
- [x] T621: Create `EvalPipelineSDK` in `src/hw5/sdk/sdk.py`
- [x] T622: Initialize with optional `config_path: str = "config/setup.json"`
- [x] T623: In `__init__()`: load Config, ModelRegistry, ApiGatekeeper
- [x] T624: Implement `run_full_evaluation() -> list[CellResult]` — delegates to EvaluationLoop
- [x] T625: Implement `run_single_cell(model, framework, quant) -> CellResult`
- [x] T626: Implement `list_models() -> list[str]` — delegates to ModelRegistry.list_names()
- [x] T627: Implement `get_results(results_dir: str) -> list[CellResult]` loading all JSONs
- [x] T628: Implement `generate_plots(results: list[CellResult]) -> list[Path]`
- [x] T629: Implement `generate_report(results: list[CellResult]) -> Path`
- [x] T630: Implement `generate_summaries(results: list[CellResult]) -> dict[str, str]`
- [x] T631: Confirm all business logic is in services, not in SDK (SDK only delegates)
- [x] T632: Confirm sdk.py under 150 lines

### P8.2 CLI (`src/hw5/main.py`)
- [x] T633: Create `main.py` with `argparse.ArgumentParser`
- [x] T634: Add `--mode` arg: choices=["full", "single", "plot", "report"], default="full"
- [x] T635: Add `--config` arg: path to setup.json (default "config/setup.json")
- [x] T636: Add `--cell` arg: specific cell ID to run in single mode
- [x] T637: Add `--resume` flag: resume from existing results
- [x] T638: Add `--models` arg: comma-separated model names to include
- [x] T639: Add `--frameworks` arg: comma-separated frameworks to include
- [x] T640: Add `--quants` arg: comma-separated quant levels to include
- [x] T641: Add `--dry-run` flag: print cells without executing
- [x] T642: Add `--live` flag: show real-time metrics table during inference
- [x] T643: Implement `main()` function dispatching to SDK methods based on mode
- [x] T644: Add logging setup: `logging.basicConfig(level=logging.INFO)`
- [x] T645: Load `.env` file at startup via `python-dotenv.load_dotenv()`
- [x] T646: Add `--log-level` arg: choices=["DEBUG","INFO","WARNING","ERROR"]
- [x] T647: Print final summary to stdout after run completes
- [x] T648: Return exit code 1 if any cells failed, 0 if all succeeded
- [x] T649: Add `if __name__ == "__main__": main()` at end of file
- [x] T650: Confirm main.py under 150 lines

### P8.3 SDK Tests
- [x] T651: Write `test_sdk.py` — mock all service classes, verify SDK delegation
- [x] T652: Write test — `run_full_evaluation()` calls EvaluationLoop.run()
- [x] T653: Write test — `list_models()` calls registry.list_names()
- [x] T654: Write test — `generate_plots()` calls Plotter.save_all()
- [x] T655: Write test — `generate_report()` calls ReportGenerator.to_html()
- [x] T656: Write test — SDK initializes without exception when config file present
- [x] T657: Write test — `run_single_cell` calls EvaluationLoop.run_cell with correct args
- [x] T658: Write test — `get_results` loads all JSONs from results dir
- [x] T659: Confirm SDK test file under 150 lines
- [x] T660: Run `ruff check` on sdk.py and main.py — 0 violations
- [x] T661: Add docstrings to all SDK public methods
- [x] T662: Commit SDK and CLI with "feat: add SDK layer and CLI entry point"
- [x] T663: Update TODO Phase 8 statuses
- [x] T664: Verify `uv run python src/hw5/main.py --help` outputs usage
- [x] T665: Verify `uv run python src/hw5/main.py --mode full --dry-run` prints all 12 cells

### P8.4 End-to-End Smoke Test
- [x] T666: Write `tests/integration/test_e2e_smoke.py` with `@pytest.mark.integration`
- [x] T667: Smoke test: run `--mode full --dry-run`, verify 0 errors and 12 cells listed
- [x] T668: Smoke test: run `--mode plot` on pre-saved mock results, verify PNG files created
- [x] T669: Smoke test: run `--mode report` on pre-saved mock results, verify HTML created
- [x] T670: Smoke test: verify `assets/` contains expected file names after plot run
- [x] T671: Verify smoke test pass without GPU: `CUDA_VISIBLE_DEVICES="" uv run pytest ...`
- [x] T672: Add smoke test to Makefile `test-smoke` target
- [x] T673: Document smoke test in README under "Running Tests"
- [x] T674: Add `--output-dir` CLI arg to redirect results/assets to custom directory
- [x] T675: Write test — `--output-dir` creates results in specified path
- [x] T676: Add `--eval-prompt` CLI arg to override prompt from command line
- [x] T677: Write test — `--eval-prompt` overrides config value
- [x] T678: Add `--max-tokens` CLI arg
- [x] T679: Write test — `--max-tokens` overrides config value
- [x] T680: Commit smoke tests with "test: add integration smoke tests for full pipeline"

---

## Phase 9 — Testing & Quality (T681–T760)

### P9.1 Test Coverage
- [ ] T681: Run `pytest --cov=src --cov-report=term-missing` and record initial coverage
- [ ] T682: Identify all uncovered lines from coverage report
- [ ] T683: Write additional tests to bring coverage to ≥85%
- [ ] T684: Target highest-risk uncovered paths: exception handling branches, fallback paths
- [ ] T685: Add coverage badge to README.md
- [ ] T686: Configure `fail_under=85` in `[tool.pytest.ini_options]` cov settings
- [ ] T687: Add `pytest-cov` to dev dependencies in pyproject.toml

### P9.2 Linting & Formatting
- [ ] T688: Run `ruff check src/` — fix all violations
- [ ] T689: Run `ruff check tests/` — fix all violations
- [ ] T690: Run `ruff format src/` — auto-format all files
- [ ] T691: Run `ruff format tests/` — auto-format all test files
- [ ] T692: Add `ruff check` and `ruff format --check` to Makefile `lint` target
- [ ] T693: Verify zero Ruff violations after formatting

### P9.3 Type Checking
- [ ] T694: Run `mypy src/hw5/` — fix all type errors
- [ ] T695: Add type annotations to all function signatures in services/
- [ ] T696: Add type annotations to all function signatures in shared/
- [ ] T697: Add type annotations to SDK layer
- [ ] T698: Add `mypy` to Makefile `lint` target
- [ ] T699: Resolve any `Any` types where concrete types are known
- [ ] T700: Add `from __future__ import annotations` to all modules

### P9.4 File Length Audit
- [ ] T701: Run `find src -name "*.py" -exec wc -l {} \; | sort -n` to list all file lengths
- [ ] T702: Identify any file exceeding 150 lines
- [ ] T703: Split any over-length file into two modules
- [ ] T704: Re-run file length check after splits
- [ ] T705: Confirm zero files exceed 150 lines
- [ ] T706: Add file-length check to Makefile `lint` target

### P9.5 Docstring Audit
- [ ] T707: Audit every public function/class for one-line docstrings
- [ ] T708: Add missing docstrings using `pydocstyle` or manual inspection
- [ ] T709: Ensure no multi-paragraph docstrings (per code style guidelines)
- [ ] T710: Verify docstrings describe the "why" or the non-obvious, not just the "what"

### P9.6 Edge Case Tests
- [ ] T711: Write test — pipeline handles 0 results gracefully in Plotter (empty DataFrame)
- [ ] T712: Write test — monitor handles 0 samples in MetricsSnapshot.from_buffer
- [ ] T713: Write test — EvaluationLoop with empty model list raises RegistryError
- [ ] T714: Write test — Config with missing required field raises ConfigError on load
- [ ] T715: Write test — ApiGatekeeper with rate=0 raises ValueError
- [ ] T716: Write test — QuantizationConfig with bits=16 raises ValueError
- [ ] T717: Write test — OllamaRunner.infer without prior load raises RunnerError
- [ ] T718: Write test — AirLLMRunner.infer without prior load raises RunnerError
- [ ] T719: Write test — monitor.stop() called twice is idempotent
- [ ] T720: Write test — results directory not writable: save_result raises IOError
- [ ] T721: Write test — Plotter with all-failed results produces empty plots without crash
- [ ] T722: Write test — ReportGenerator with no plots raises no exception
- [ ] T723: Write test — SummaryGenerator with single cell result produces valid output
- [ ] T724: Write test — EvaluationLoop resume with corrupt JSON file logs error and skips
- [ ] T725: Write test — Config.get returns default for deeply nested missing key
- [ ] T726: Write test — ModelRegistry.validate detects double-HOOK placeholder
- [ ] T727: Write test — RunnerFactory.create with empty string framework raises ValueError
- [ ] T728: Write test — VRAMSpikeEvent.to_dict / from_dict roundtrip
- [ ] T729: Write test — MetricsBuffer thread safety under 100 concurrent writes
- [ ] T730: Write test — CellResult.from_dict handles missing optional fields

### P9.7 Performance Tests
- [ ] T731: Write test — MetricsBuffer.append handles 10,000 items without memory error
- [ ] T732: Write test — Plotter._get_df processes 100 CellResults in under 1 second
- [ ] T733: Write test — SummaryGenerator.generate_all runs in under 100ms
- [ ] T734: Write test — ReportGenerator.to_html with 4 base64 plots completes in under 5s
- [ ] T735: Write test — Config.load parses JSON in under 10ms
- [ ] T736: Write test — ModelRegistry.load_config with 20 models completes in under 100ms

### P9.8 Final Test Run
- [ ] T737: Run full test suite: `pytest tests/unit/ -v` — 0 failures
- [ ] T738: Run `pytest --cov=src --cov-report=term` — verify ≥85%
- [ ] T739: Run `ruff check src/ tests/` — 0 violations
- [ ] T740: Run `mypy src/hw5/` — 0 errors
- [ ] T741: Commit with "test: achieve ≥85% coverage, 0 linting violations"
- [ ] T742: Update TODO Phase 9 statuses
- [ ] T743: Save coverage report as `assets/coverage_report.txt`
- [ ] T744: Add test run screenshot/output to notebooks/ for grader reference
- [ ] T745: Verify all integration test stubs are properly marked and skip correctly
- [ ] T746: Add `pytest --markers` output to README under "Running Tests"
- [ ] T747: Write test — `prompts_ive_used.md` file exists and is non-empty
- [ ] T748: Write test — `docs/PRD.md` exists and contains "Acceptance Criteria" section
- [ ] T749: Write test — `config/models.json` is valid JSON
- [ ] T750: Write test — `config/setup.json` is valid JSON
- [ ] T751: Write test — `config/rate_limits.json` is valid JSON
- [ ] T752: Write test — all required directories exist (data/, results/, assets/, notebooks/)
- [ ] T753: Write test — no `.env` file committed (only `.env-example`)
- [ ] T754: Write test — `assets/` contains all 8 expected plot files after a plot run
- [ ] T755: Write test — `report.html` contains all four section headings
- [ ] T756: Write test — `uv.lock` exists and is non-empty
- [ ] T757: Write test — `pyproject.toml` has `[tool.ruff]` section
- [ ] T758: Write test — `pyproject.toml` has `[tool.pytest.ini_options]` section
- [ ] T759: Write test — no file in src/ named with spaces or non-ASCII characters
- [ ] T760: Write test — all Python files import correctly (no circular imports)

---

## Phase 10 — Documentation & Submission (T761–T800)

### P10.1 README Completion
- [x] T761: Write Installation Instructions section in README (uv, Ollama, HF token)
- [x] T762: Write Usage Instructions in README (all CLI modes with examples)
- [x] T763: Write Examples & Demos section (sample output, expected plots)
- [x] T764: Write Configuration Guide section (how to edit models.json, setup.json)
- [x] T765: Write Contribution Guidelines section (coding standards, branch naming)
- [x] T766: Write License & Credits section (MIT + library attributions)
- [x] T767: Add hardware specs table to README (CPU, RAM, GPU, OS, Python version)
- [x] T768: Add Expected Output section listing what files are created by pipeline
- [x] T769: Add Troubleshooting section (common errors and fixes)
- [x] T770: Add badge row at top: Python version, test coverage, Ruff status

### P10.2 Specialized PRD Documents
- [x] T771: Complete `docs/PRD_airllm.md` with AirLLM theory (layer streaming, OS paging)
- [x] T772: Add AirLLM vs Ollama comparison table to PRD_airllm.md
- [x] T773: Add memory equation to PRD_airllm.md: VRAM = single_layer_size × batch_size
- [x] T774: Complete `docs/PRD_quantization.md` with Q2/Q4/Q8 mathematical definitions
- [x] T775: Add perplexity impact table per quantization level to PRD_quantization.md
- [x] T776: Add GGUF format explanation to PRD_quantization.md
- [x] T777: Complete `docs/PRD_monitoring.md` with OS page monitoring theory
- [x] T778: Add virtual memory / swap explanation to PRD_monitoring.md
- [x] T779: Add VRAM spike detection algorithm explanation to PRD_monitoring.md
- [x] T780: Add original experiment ideas section to PRD_monitoring.md

### P10.3 Jupyter Notebook
- [x] T781: Create `notebooks/01_exploration.ipynb` with data loading and EDA
- [x] T782: Add cell showing how to load results/ JSON files into DataFrame
- [x] T783: Add cell reproducing all four plots inline
- [x] T784: Add cell computing summary statistics per framework and quant level
- [x] T785: Add cell showing VRAM spike timeline for one cell as line chart
- [x] T786: Add cell with original analysis: correlation between swap usage and tokens/sec
- [x] T787: Add cell with original analysis: disk read bytes vs. first_token_latency
- [x] T788: Add markdown cells explaining each analysis block
- [x] T789: Save notebook as .ipynb (HTML export requires executing the notebook first)

### P10.4 Final Submission Checklist
- [x] T790: Run full pipeline once and verify all 12 cells complete (or document partial)
- [x] T791: Verify `assets/` contains: heatmap.png/svg, ram_timeline.png/svg, vram_bar.png/svg, tradeoff_scatter.png/svg
- [x] T792: Verify `assets/report.html` opens in browser with all plots and summaries
- [x] T793: Verify `results/` contains all cell JSON files
- [x] T794: Verify `prompts_ive_used.md` documents all prompts used in session
- [x] T795: Verify `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` all complete
- [x] T796: Run final lint + test + coverage check: all pass (270 tests, 92.51% coverage, 0 ruff violations, all src files ≤150 lines)
- [ ] T797: Commit final state with "chore: final submission HW5 — AirLLM evaluation pipeline"
- [ ] T798: Push branch to GitHub remote
- [ ] T799: Submit GitHub URL per course submission instructions
- [ ] T800: Archive local results and assets as `hw5_submission_backup.zip`
