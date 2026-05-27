import json
from pathlib import Path
from ..config import load_config

ANALYTICS_PATH = Path("outputs/analytics/win_loss_matrix.json")

def display_full_analytics_report() -> None:
    """
    Parses historical metrics and prints a highly scannable, 
    complete report of the debate outcomes and qualitative justifications.
    """
    config = load_config()
    matrix_path = Path(config.get("analytics", {}).get("matrix_file", str(ANALYTICS_PATH)))
    
    if not matrix_path.exists() or matrix_path.stat().st_size == 0:
        print("\n❌ No analytics data recorded yet. Please run a complete debate match first!")
        return

    # 1. Ingest Matrix Totals
    matrix_data = json.loads(matrix_path.read_text(encoding="utf-8"))
    
    print("\n" + "="*65)
    print("📊 MULTI-AGENT DEBATE PLATFORM — PERFORMANCE REPORT")
    print("="*65)
    print(f"• Total Tournament Runs Indexed : {matrix_data.get('total_debates_run', 1)}")
    print(f"• Proponent Win Record          : {matrix_data.get('proponent_wins', 0)}")
    print(f"• Opponent Win Record           : {matrix_data.get('opponent_wins', 0)}")
    print(f"• Systemic Bias Risk Warning    : {matrix_data.get('detected_bias_risk', 'NONE')}")
    print("-"*65)

    # 2. Extract and Format Comprehensive Session History
    print("\n📜 HISTORICAL MATCH VERDICTS & VERBAL JUSTIFICATIONS:")
    
    history = matrix_data.get("historical_results", [])
    if not history:
        print("  No granular match logs present in the tracking ledger.")
        return

    for item in history:
        print(f"\n[🏆 DEBATE MATCH #{item['debate_number']}]")
        print(f"  └── 🥇 Declared Winner: {item['winner']}")
        print(f"  └── 🧮 Scoreboard Check: Proponent [{item['points'].get('Proponent', 0)}] vs Opponent [{item['points'].get('Opponent', 0)}]")
        print("  └── ⚖️ Adjudicator Verbal Assessment:")
        
        # Grab the justification data
        verdict = item.get('verdict', {})
        justification_text = verdict.get('justification') or verdict.get('tie_breaker_justification') or 'No extensive breakdown available.'
        
        # Wrap and indent long sentences beautifully
        import textwrap
        wrapped_lines = textwrap.wrap(justification_text, width=60)
        for line in wrapped_lines:
            print(f"      > {line}")
            
    print("\n" + "="*65)

def update_analytics(winner: str, points: dict = None, verdict: dict = None):
    """
    Updates the win/loss ledger and detects bias risks.
    """
    config = load_config()
    matrix_path = Path(config.get("analytics", {}).get("matrix_file", str(ANALYTICS_PATH)))
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    
    if matrix_path.exists():
        with open(matrix_path, "r") as f:
            data = json.load(f)
    else:
        data = {
            "total_debates_run": 0,
            "proponent_wins": 0,
            "opponent_wins": 0,
            "detected_bias_risk": "NONE",
            "historical_results": []
        }
    
    data["total_debates_run"] += 1
    if winner.lower() == "proponent":
        data["proponent_wins"] += 1
    elif winner.lower() == "opponent":
        data["opponent_wins"] += 1
        
    # Store the latest result
    result_entry = {
        "debate_number": data["total_debates_run"],
        "winner": winner,
        "points": points or {},
        "verdict": verdict or {}
    }
    if "historical_results" not in data:
        data["historical_results"] = []
    data["historical_results"].append(result_entry)
    
    # Bias detection logic
    p_wins = data["proponent_wins"]
    o_wins = data["opponent_wins"]
    total = data["total_debates_run"]
    
    if total >= 5:
        ratio = p_wins / total
        if ratio > 0.7:
            data["detected_bias_risk"] = "HIGH_PROPONENT_BIAS"
        elif ratio < 0.3:
            data["detected_bias_risk"] = "HIGH_OPPONENT_BIAS"
        else:
            data["detected_bias_risk"] = "LOW"
            
    with open(matrix_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return data
