# Foundational Planning Documentation (FPD)

## 1. Problem Statement
In the era of AI-driven information, understanding the nuances of complex debates (such as social media's impact on democracy) often gets lost in polarized echo chambers. There is a need for a structured, automated way to simulate diverse perspectives and synthesize them into a balanced, evidence-based conclusion.

## 2. Goals
- **Structured Synthesis**: Automate the process of debating complex topics using process-isolated AI personas.
- **Persona Fidelity**: Ensure agents strictly adhere to their assigned stances (Cautious vs. Optimistic) and roles (Ethics Researcher vs. Tech Entrepreneur).
- **Quantitative Evaluation**: Implement a data-driven scoring system to determine the quality and depth of arguments.
- **Process Isolation**: Utilize a multi-process architecture to ensure clean separation of concerns and state between agents.

## 3. System Design
The system follows a **"Judge-Orchestrator"** pattern:
- **Judge (Father Process)**: Acting as the central router, the Judge initiates the topic, manages the conversation history, and controls the sequential flow.
- **Debaters (Child Processes)**: Two independent processes represent the conflicting stances. They communicate with the Judge via `multiprocessing.Pipe`.
- **Sequential Routing**: The flow is strictly `Judge -> Agent 1 -> Judge -> Agent 2`, preventing direct agent-to-agent communication and ensuring the Judge maintains a full audit log.
- **Persistent Memory**: A temporary memory layer stores summaries of each turn to facilitate deep analysis and tie-breaking logic.
