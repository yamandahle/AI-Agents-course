# PRD — Quantization Mechanism
**Version:** 1.0.0  **Date:** 2026-06-22

## Background

Neural network weights are stored as floating-point numbers. Quantization maps
them to lower-bit integer representations, trading precision for memory and
speed.

## Mathematical Definitions

### Q8 (INT8)
Each weight rounded to nearest signed 8-bit integer.  
Memory: `params × 1 byte`. For 7B params: ~7 GB.  
Quality loss: minimal (~0.1 perplexity increase).

### Q4 (INT4 / 4-bit)
Each weight packed into 4 bits. Common schemes: Q4_K_M (k-quants with mixed
precision for attention layers).  
Memory: `params × 0.5 bytes`. For 7B params: ~3.5 GB.  
Quality loss: small (~0.3-0.5 perplexity increase).

### Q2 (INT2 / 2-bit)
Extreme compression. Two bits per weight.  
Memory: `params × 0.25 bytes`. For 7B params: ~1.75 GB.  
Quality loss: significant (~2-5+ perplexity increase). May produce incoherent
output on complex prompts.

## Perplexity Impact (approximate, Llama-family models)

| Quantization | Bits/weight | RAM (7B) | Perplexity increase |
|-------------|-------------|----------|---------------------|
| FP32 | 32 | 28 GB | baseline |
| FP16 | 16 | 14 GB | ~0 |
| Q8 | 8 | 7 GB | ~0.1 |
| Q4 | 4 | 3.5 GB | ~0.3–0.5 |
| Q2 | 2 | 1.75 GB | ~2–5+ |

## GGUF Format (Ollama)

Ollama uses GGUF (GPT-Generated Unified Format). Each tag encodes quantization:

| Ollama Tag | Bits | Description |
|-----------|------|-------------|
| `q8_0` | 8 | Standard INT8 |
| `q4_K_M` | 4 | K-quant mixed, medium |
| `q4_K_S` | 4 | K-quant mixed, small |
| `q2_K` | 2 | K-quant 2-bit |

## AirLLM Compression Parameter

| Label | compression= | Notes |
|-------|-------------|-------|
| Q8 | `"8bit"` | bitsandbytes INT8 |
| Q4 | `"4bit"` | bitsandbytes NF4 |
| Q2 | `"2bit"` | bitsandbytes 2-bit (experimental) |

## Acceptance Criteria

- `QuantizationConfig.to_ollama_tag()` maps Q2/Q4/Q8 to correct GGUF tags
- `QuantizationConfig.to_airllm_param()` maps Q2/Q4/Q8 to correct compression strings
- Adding a new level (e.g. Q6) requires only a config edit and one enum update
- Report discusses quality-vs-compression trade-off with measured output samples
