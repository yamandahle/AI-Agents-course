# Costs & Resource Awareness (costs.md)

## 1. Token Usage Analysis
The system's sequential 10-round debate structure implies a linear growth in token usage per session.

- **Per Response (Estimated)**: ~150-250 tokens (including system prompts, stance logic, and history).
- **Per Round**: 2 Debaters + 1 Judge synthesis = ~600 tokens.
- **Per Session (10 Rounds)**: ~6,000 - 8,000 tokens.

## 2. Economic Implications of Design Choices
- **Multiprocessing vs. Single-Process**: Using independent processes adds memory overhead but ensures robust failure isolation (handled by the Watchdog). In a cloud environment, this favors horizontally scalable instances over a single high-compute node.
- **Summarization Strategy**: By summarizing turns into `MEMORY.md`, we reduce the need to pass the *full* raw history back to the LLM in later rounds, potentially saving 20-30% in input token costs for very long debates.
- **Fixed Topic Logic**: Hardcoding the topic eliminates "hallucination costs" or redundant prompt refinement cycles often required for user-input topics.

## 3. Resource Awareness
- **FIFO Logging**: Limits disk space usage to 20 files, preventing storage overflow in long-running deployments.
- **Sequential Execution**: By running agents one after another (`parent -> child -> parent`), we peak at the resource usage of only one active inference loop at a time, rather than parallel bursts, making it compatible with lower-tier API rate limits.
