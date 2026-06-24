# PRD — AirLLM Layer-Streaming Mechanism
**Version:** 1.0.0  **Date:** 2026-06-22

## Background

Standard LLM inference loads the entire model into GPU VRAM or CPU RAM before
processing a single token. For a 7B model in FP16, that is ~14 GB. AirLLM (by
lyogavin) solves this by loading one transformer layer at a time from disk,
running the forward pass, then discarding that layer before loading the next.

## Memory Equation

```
VRAM_peak ≈ single_layer_size_bytes × batch_size
single_layer_size = model_total_bytes / num_layers
```

A Llama-3 7B model has 32 layers. With 4-bit quantization the total is ~4 GB,
so each layer is ~128 MB. AirLLM holds only 128 MB in memory at once.

## OS Paging Context

When RAM is exhausted, the OS swaps pages to disk (Linux: swap partition or
swapfile; Windows: pagefile). AirLLM deliberately trades VRAM for disk I/O
latency. This pipeline measures that trade-off by recording:
- disk_read_mb per inference
- peak_ram_mb vs. standard loading approach
- swap_mb — whether the OS was forced to page beyond AirLLM's own paging

## AirLLM vs. Ollama Comparison

| Aspect | Ollama (GGUF) | AirLLM |
|--------|--------------|--------|
| Memory strategy | Quantize entire model ahead-of-time | Stream layers on demand |
| Min VRAM required | ~model_size_q / 2 | single layer size |
| First-token latency | Fast (model preloaded) | Slower (first layer load) |
| Disk reads per token | Minimal | High (layer reload each forward) |
| Setup complexity | Low (ollama pull) | Medium (HF repo + airllm install) |
| Quantization control | GGUF tags (Q4_K_M etc.) | compression= parameter |

## Original Experiment Ideas

1. **SSD vs. HDD speed impact:** Measure first_token_latency on a machine with
   an NVMe SSD vs. a spinning HDD — AirLLM should show much larger difference
   than Ollama, which pre-loads.
2. **Layer cache warm-up:** Run the same prompt twice; check if the OS file
   cache reduces disk reads on the second run.
3. **Batch size scaling:** Increase batch_size in AirLLM; measure whether
   VRAM grows linearly with batch or has overhead.

## Acceptance Criteria

- Pipeline records `disk_read_mb` for every AirLLM cell
- `peak_vram_mb` for AirLLM cells is ≤ 1 layer size × 2 (double-buffering)
- Report explains layer-streaming in the executive summary section
