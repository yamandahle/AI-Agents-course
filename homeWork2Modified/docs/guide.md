# Project Guide: Setup and Usage

## 1. Prerequisites
- **Python 3.10+**
- Access to a terminal with `multiprocessing` support.

## 2. Setup
1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd homeWork2Modified
   ```
2. **Environment Configuration**:
   - Rename `.env-example` to `.env`.
   - Add your necessary configuration keys to the `.env` file (though current mocks run locally).

## 3. Usage
1. **Run the Main System**:
   Execute the following command from the project root:
   ```bash
   python3 -m src.my_package.main
   ```
2. **Interact with the Menu**:
   - Select `1` to start the automated 10-round debate.
   - The system will handle process spawning, scoring, and report generation automatically.
3. **Review Results**:
   - **Live Output**: Follow the Judge's log in the terminal.
   - **Final Report**: Check `results/results.md` for a permanent record of the session, including scores and the winner.

## 4. Understanding the Architecture
- All core logic resides in `src/my_package/core/`.
- Agent behaviors are modified via `system_instructions` within their respective classes.
- Scoring rules can be adjusted in the `JudgeAgent` class.
