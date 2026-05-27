import multiprocessing
import time
import json
from .sdk.models.debater_agent import DebaterAgent
from .sdk.models.judge_agent import JudgeAgent
from .services.session_recorder import persist_session_message, initialize_or_restore_session
from .services.fifo_logger import setup_fifo_logger
from .services.watchdog import ProcessWatchdog
from .services.analytics import update_analytics, display_full_analytics_report
from .services.recovery_logger import update_recovery_checkpoint
from .config import load_config
from .shared.debate_flow import DEBATE_FLOW

logger = setup_fifo_logger()

def debater_worker(name, persona_path, provider, input_queue, output_queue):
    agent = DebaterAgent(name, persona_path, provider)
    logger.info(f"Worker {name} started.")
    
    while True:
        task = input_queue.get()
        if task is None: # Exit signal
            break
        
        context = task.get("context", [])
        search_query = task.get("search_query")
        speech_instructions = task.get("speech_instructions")
        
        try:
            response, queries = agent.run_turn(context, search_query, speech_instructions)
            output_queue.put({"status": "SUCCESS", "message": response, "queries": queries})
        except Exception as e:
            logger.error(f"Error in {name} worker: {str(e)}")
            output_queue.put({"status": "ERROR", "message": str(e)})

def judge_worker(name, persona_path, provider, input_queue, proponent_queue, opponent_queue, main_queue):
    agent = JudgeAgent(name, persona_path, provider)
    logger.info(f"Worker {name} started.")
    
    while True:
        task = input_queue.get()
        if task is None:
            break
        
        action = task.get("action")
        context = task.get("context", [])
        
        try:
            if action == "RELAY":
                response = agent.run_turn(context)
                target = task.get("target")
                if target == "Proponent":
                    proponent_queue.put({"context": context + [{"speaker": "Judge", "message": response}]})
                else:
                    opponent_queue.put({"context": context + [{"speaker": "Judge", "message": response}]})
                main_queue.put({"status": "RELAYED", "message": response})
            elif action == "JUDGE_ROUND":
                topic = task.get("topic")
                speech_type = task.get("speech_type")
                p_msg = task.get("proponent_message")
                o_msg = task.get("opponent_message")
                result = agent.judge_round(topic, speech_type, p_msg, o_msg)
                main_queue.put({"status": "ROUND_JUDGED", "result": result})
            elif action == "EVALUATE":
                result = agent.evaluate_winner(context)
                main_queue.put({"status": "EVALUATED", "result": result})
        except Exception as e:
            logger.error(f"Error in {name} worker: {str(e)}")
            main_queue.put({"status": "ERROR", "message": str(e)})

class DebateOrchestrator:
    def __init__(self):
        self.config = load_config()
        self.provider = self.config.get("use_provider", "anthropic")
        self.topic = self.config["debate_constraints"]["topic"]
        
        self.proponent_q = multiprocessing.Queue()
        self.opponent_q = multiprocessing.Queue()
        self.judge_q = multiprocessing.Queue()
        self.main_q = multiprocessing.Queue()
        
    def start_debate(self):
        logger.info(f"Starting debate on topic: {self.topic}")
        history = initialize_or_restore_session()
        
        # Scorecard
        points = {"Proponent": 0, "Opponent": 0}
        quality_scores = {"Proponent": 0, "Opponent": 0}
        
        # Start workers
        p_proc = multiprocessing.Process(target=debater_worker, args=("Proponent", "personas/proponent.md", self.provider, self.proponent_q, self.judge_q))
        o_proc = multiprocessing.Process(target=debater_worker, args=("Opponent", "personas/opponent.md", self.provider, self.opponent_q, self.judge_q))
        j_proc = multiprocessing.Process(target=judge_worker, args=("Judge", "personas/judge.md", self.provider, self.judge_q, self.proponent_q, self.opponent_q, self.main_q))
        
        p_proc.start()
        o_proc.start()
        j_proc.start()
        
        try:
            round_proponent_msg = None
            round_speech_type = None
            max_turns = self.config["debate_constraints"].get("max_turns", len(DEBATE_FLOW))

            for i, turn_info in enumerate(DEBATE_FLOW):
                if i >= max_turns:
                    break
                
                speaker = turn_info["speaker"]
                speech_type = turn_info["speech_type"]
                instructions = turn_info
                
                # Determine target queue and process
                target_q = self.proponent_q if speaker == "Proponent" else self.opponent_q
                active_pid = p_proc.pid if speaker == "Proponent" else o_proc.pid
                
                # 1. Debater Turn
                search_query = self.topic if turn_info["turn_index"] == 1 else f"counter argument for {history[-2]['message'][:50]}" if len(history) > 1 else None
                
                watchdog = ProcessWatchdog(active_pid, timeout_seconds=60.0)
                watchdog.start()
                target_q.put({"context": history, "search_query": search_query, "speech_instructions": instructions})
                debater_res = self.judge_q.get()
                watchdog.stop()
                
                if debater_res["status"] == "ERROR": break
                
                message = debater_res["message"]
                persist_session_message(speaker, message, debater_res["queries"])
                update_recovery_checkpoint(speaker, speech_type, message)
                history.append({"speaker": speaker, "message": message})
                
                if speaker == "Proponent":
                    round_proponent_msg = message
                    round_speech_type = speech_type
                else:
                    # End of round (Opponent just spoke)
                    # 2. Judge Round Adjudication
                    watchdog = ProcessWatchdog(j_proc.pid, timeout_seconds=60.0)
                    watchdog.start()
                    self.judge_q.put({
                        "action": "JUDGE_ROUND",
                        "topic": self.topic,
                        "speech_type": round_speech_type,
                        "proponent_message": round_proponent_msg,
                        "opponent_message": message
                    })
                    judge_round_res = self.main_q.get()
                    watchdog.stop()
                    
                    if judge_round_res["status"] == "ROUND_JUDGED":
                        result = judge_round_res["result"].get("round_judgment", {})
                        winner = result.get("round_winner")
                        points[winner] += 1
                        quality_scores[winner] += result.get("quality_score", 0)
                        logger.info(f"Round winner: {winner}. Current Score: P {points['Proponent']} - O {points['Opponent']}")
                        persist_session_message("System-Judge", f"Round Adjudication: {json.dumps(result, indent=2)}")

                # 3. Judge Relay
                next_speaker = "Opponent" if speaker == "Proponent" else "Proponent"
                watchdog = ProcessWatchdog(j_proc.pid, timeout_seconds=60.0)
                watchdog.start()
                self.judge_q.put({"action": "RELAY", "context": history, "target": next_speaker})
                judge_relay_res = self.main_q.get()
                watchdog.stop()
                
                if judge_relay_res["status"] == "ERROR": break
                
                judge_msg = judge_relay_res["message"]
                persist_session_message("Judge", judge_msg)
                update_recovery_checkpoint("Judge", "Moderation Relay", judge_msg)
                history.append({"speaker": "Judge", "message": judge_msg})

            # Final Evaluation
            logger.info("Debate finished. Evaluating final winner...")
            self.judge_q.put({"action": "EVALUATE", "context": history})
            eval_res = self.main_q.get()
            
            if eval_res["status"] == "EVALUATED":
                verdict = eval_res["result"].get("verdict", {})
                
                # Tie-breaker logic
                if points["Proponent"] == points["Opponent"]:
                    logger.info("Point tie detected! Applying quality score tie-breaker.")
                    if quality_scores["Proponent"] > quality_scores["Opponent"]:
                        master_winner = "Proponent"
                    else:
                        master_winner = "Opponent"
                    verdict["final_winner"] = master_winner
                    verdict["tie_breaker_justification"] += f" [TIE-BREAKER APPLIED: Proponent Quality {quality_scores['Proponent']} vs Opponent Quality {quality_scores['Opponent']}]"
                else:
                    master_winner = "Proponent" if points["Proponent"] > points["Opponent"] else "Opponent"
                    verdict["final_winner"] = master_winner

                logger.info(f"Final Winner: {master_winner}")
                
                # Format and print the final report
                report = verdict.get("detailed_report", "No detailed report provided.")
                print("\n" + "#" * 60)
                print("         🏆 JUDGE'S FINAL REPORT 🏆")
                print("#" * 60)
                print(f"WINNER: {master_winner}")
                print("-" * 60)
                print(report)
                print("#" * 60 + "\n")

                persist_session_message("System-Judge", f"### 🏆 FINAL VERDICT REPORT\n\n**Winner**: {master_winner}\n\n**Justification**: {verdict.get('tie_breaker_justification', 'N/A')}\n\n**Detailed Report**:\n{report}")
                update_analytics(master_winner, points=points, verdict=verdict)
                display_full_analytics_report()
                return verdict
            
        finally:
            self.proponent_q.put(None); self.opponent_q.put(None); self.judge_q.put(None)
            for p in [p_proc, o_proc, j_proc]:
                p.join(timeout=2)
                if p.is_alive(): p.terminate()
