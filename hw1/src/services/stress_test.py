import json
import torch
import numpy as np
from src.services.data_generator import SignalGenerator, build_datasets
from src.services.train import train_model
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM

def run_stress_experiment(name, alpha, beta, base_conf):
    print(f"\n>>> Running Stress Test: {name} (alpha={alpha}, beta={beta})")
    
    # deep copy and inject stress levels
    conf = json.loads(json.dumps(base_conf))
    conf["noise"]["stress"] = {"alpha": alpha, "beta": beta}
    conf["training"]["epochs"] = 30 # Reduce to 30 for speed in stress test
    
    train_ds, val_ds = build_datasets(conf, noise_level="stress", window_size=10)
    
    models = {
        "FC": FC(window_size=10),
        "RNN": SignalRNN(window_size=10),
        "LSTM": SignalLSTM(window_size=10)
    }
    
    results = {}
    for m_name, model in models.items():
        print(f"  Training {m_name}...")
        history = train_model(model, train_ds, val_ds, conf)
        results[m_name] = history["best_val_mse"]
    return results

if __name__ == "__main__":
    with open("config/setup.json", "r") as f:
        base_conf = json.load(f)
    
    experiments = [
        ("Clean", 0.0, 0.0),
        ("Pure Amplitude Noise", 0.5, 0.0),
        ("Pure Phase Noise", 0.0, 0.5)
    ]
    
    summary = {}
    for name, a, b in experiments:
        summary[name] = run_stress_experiment(name, a, b, base_conf)
        
    print("\n" + "="*40)
    print("STRESS TEST SUMMARY (MSE)")
    print("="*40)
    print(f"{'Experiment':<25} | {'FC':<10} | {'RNN':<10} | {'LSTM':<10}")
    for name, res in summary.items():
        print(f"{name:<25} | {res['FC']:<10.4f} | {res['RNN']:<10.4f} | {res['LSTM']:<10.4f}")
    
    fc_phase_spike = summary["Pure Phase Noise"]["FC"] / summary["Clean"]["FC"]
    lstm_phase_spike = summary["Pure Phase Noise"]["LSTM"] / summary["Clean"]["LSTM"]
    
    print("\nCRITICAL INSIGHT:")
    print(f"FC Phase Sensitivity Spike: {fc_phase_spike:.2f}x")
    print(f"LSTM Phase Sensitivity Spike: {lstm_phase_spike:.2f}x")
    if fc_phase_spike > lstm_phase_spike:
        print("RESULT: Hypothesis Confirmed. FC MSE spikes significantly more than LSTM under Pure Phase Noise.")
