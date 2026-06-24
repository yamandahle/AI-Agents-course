# PRD — OS Page Monitoring Mechanism
**Version:** 1.0.0  **Date:** 2026-06-22

## Background

Running a large LLM stresses every level of the memory hierarchy:
- **L3 cache:** weight tensors thrash the cache during each forward pass
- **RAM:** full model weights, KV cache, and activations compete for space
- **Swap:** when RAM is exhausted, the OS spills pages to disk
- **VRAM:** GPU memory holds weight copies and gradient buffers

This module hooks into OS-level diagnostics via `psutil` and `pynvml` to capture
real-time metrics, enabling us to observe the memory pressure each framework
creates.

## Metrics Collected

| Metric | Source | Unit | Sampling |
|--------|--------|------|---------|
| CPU utilization | `psutil.cpu_percent()` | % | 500 ms |
| RAM used | `psutil.virtual_memory().used` | MB | 500 ms |
| Swap used | `psutil.swap_memory().used` | MB | 500 ms |
| VRAM allocated | `pynvml` or `torch.cuda.memory_allocated()` | MB | 500 ms |
| Disk read | `psutil.disk_io_counters().read_bytes` | MB cumulative | 500 ms |
| Page faults | `/proc/self/stat` field 9 (Linux) | count delta | 500 ms |

## VRAM Spike Detection Algorithm

```
threshold = config.vram_spike_threshold_mb   # default: 500 MB

for each consecutive pair (prev_sample, curr_sample):
    delta = curr_sample.vram_mb - prev_sample.vram_mb
    if delta > threshold:
        emit VRAMSpikeEvent(ts=curr_sample.ts, delta=delta)
```

Spikes correlate with model layer loads in AirLLM and GGUF model pulls in Ollama.

## Why Background Thread, Not Async

`psutil` calls are synchronous C-extension blocking calls. Running them in
`asyncio` would require an executor, adding context-switch overhead with no
benefit — LLM forward passes block the GIL anyway, so async cancellation is
not useful here. A daemon thread with a stop_event is simpler and sufficient.

## Virtual Memory & Swap (OS Context)

Linux uses a two-level memory system:
1. **Physical RAM** — fast, limited
2. **Swap space** — slow (disk), acts as overflow

When a process exceeds available RAM, the kernel moves cold pages to swap.
This is called a **page fault** when the process later accesses a swapped page.
AirLLM's layer-streaming exploits this deliberately: it evicts layers it has
already processed, so the OS does not need to swap — AirLLM does its own
application-level paging.

## Original Experiment Ideas

1. **Swap pressure comparison:** Disable swap entirely (`sudo swapoff -a`) and
   measure which framework crashes first on a model that barely fits.
2. **Page fault rate correlation:** Plot page_faults_delta vs. tokens_per_sec
   to see if page faults are the bottleneck.
3. **Monitor granularity study:** Vary sampling interval (0.1s, 0.5s, 2s) and
   measure monitor thread overhead as % of total CPU time.

## Acceptance Criteria

- Monitor starts before model load and stops after model unload
- Every cell result includes `peak_ram_mb`, `peak_vram_mb`, `peak_swap_mb`, `avg_cpu_pct`
- VRAM spike events are logged and stored in `cell_result.metrics.spike_events`
- CPU-only fallback: when no NVIDIA GPU, `peak_vram_mb = 0.0` (not null/NaN)
- Monitor thread terminates within 2 seconds of `stop()` call
