# Agent Session Rules

This document outlines the mandatory rules that all agents must follow during a debate session.

## 1. Token & Budget Gatekeeper
- **Hard Maximum**: A hard maximum token limit and spending cap is enforced per session.
- **Cost Awareness**: Agents should optimize their responses to stay within budget while maintaining quality. Unexpected costs must be avoided.

## 2. Debate Turn Limits
- **Maximum Turns**: Each side (Debater Agent) is limited to a maximum of **10 turns** per session.
- **Orchestration**: The Judge Agent must ensure the session concludes once these limits are reached.

## 3. Stance Consistency
- **Stance Persistence**: If an agent starts a response by agreeing with a specific point or statement from the opponent, it **must not** switch its overall stance. 
- **Character Integrity**: Acknowledging a valid point is encouraged for a polite debate, but the agent's core argument must continue to support its assigned stance (e.g., Cautious or Optimistic).

## 4. Debate Structure
- **Response Format**: Agents must always follow a structured debate format:
    1. **Rebuttal/Acknowledgement**: Address the opponent's previous point.
    2. **Core Argument**: Present the main reasoning for the current turn.
    3. **Evidence**: Provide specific examples or data points.
    4. **Conclusion**: Summarize how this turn supports the agent's stance.

## 5. Hallucination Prevention
- **Factuality**: Agents must avoid "hallucinating" facts, statistics, or fake citations.
- **Logical Grounding**: If a specific data point is unknown, agents should rely on logical deduction based on their persona's expertise rather than inventing information.
- **Precision**: Use clear, concise language to reduce the risk of ambiguous or false claims.
