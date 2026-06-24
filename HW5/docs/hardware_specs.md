# Hardware Specifications

Documented on: 2026-06-22

## System

| Component | Details |
|-----------|---------|
| OS | Linux 6.6.87.2-microsoft-standard-WSL2 (Windows Subsystem for Linux 2) |
| Architecture | x86_64 |
| Shell | bash |

## CPU

| Spec | Value |
|------|-------|
| Model | Intel Core i7-1165G7 (11th Gen) |
| Base clock | 2.80 GHz |
| Threads visible to WSL | 8 |
| Cache | L3: 12 MB |
| Notes | Tiger Lake mobile CPU; supports AVX2, AVX-512 |

## Memory (RAM)

| Spec | Value |
|------|-------|
| Total RAM | ~7.6 GB (8 GB physical, WSL2 takes a share) |
| Swap | WSL2 default (auto-configured) |
| Notes | Tight for 7B Q8 — Q4 and Q2 recommended for that model size |

## GPU / VRAM

| Spec | Value |
|------|-------|
| NVIDIA GPU | None detected |
| Mode | CPU-only inference |
| VRAM metrics | Will report 0.0 (no GPU to measure) |
| Notes | AirLLM and Ollama will both use CPU + RAM for inference |

## Storage

| Spec | Value |
|------|-------|
| Type | WSL2 virtual disk (backed by Windows host SSD) |
| Notes | Layer-streaming disk reads via AirLLM will depend on host SSD speed |

## Impact on Experiments

- **No GPU:** All VRAM metrics will be 0; plots annotate CPU-only cells
- **8 GB RAM cap:** Q8 on the 7B model may be slow or OOM; pipeline will record
  failures and continue
- **WSL2 disk I/O:** AirLLM disk-read metrics reflect virtual disk speed, not
  native NVMe; expect higher latency than bare-metal Linux
- **Expected inference speed:** ~1–5 tokens/sec for 7B-Q4 on CPU (vs. ~40–80
  tokens/sec on a mid-range GPU)
