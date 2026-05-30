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

## 8. Memory Ledger
- **Hidden State**: A "Memory Ledger" tracks all topics and examples covered in the session.
- **Rule**: Agents are strictly forbidden from bringing up topics or using examples listed in the ledger.
- **Goal**: Ensures 100% unique progression and prevents circular reasoning.

## 9. Rebuttal First Policy
- **Constraint**: The first 50% of every response must be dedicated to a direct critique of the opponent's previous turn.
- **Sequence**: Rebuttal MUST precede the introduction of any new argument.

## 11. Fluid Panel Debate
- **Rule**: Agents must speak in a distinct, unscripted character voice.
- **Constraint**: NO fixed templates, clichéd transitions (e.g., "While you emphasize..."), or repetitive closing formulas.
- **Goal**: Mimic the unpredictable flow of a real panel debate.

## 12. Logic Dismantling
- **Mandate**: Agents must directly address and attempt to dismantle the specific logic or examples brought up by the previous speaker.
- **Constraint**: Dismantling must occur before any new point is introduced.

## 13. High-Temperature Variability
- **Hyperparameter**: The simulation uses a higher "temperature" for response generation to ensure linguistic variety.
- **Constraint**: Sentence structures, openings, and closings must vary significantly across turns.
