"""run_all.py — Full pipeline: train → save → figures → RNN epochs experiment.
One command does everything sequentially.
  uv run python run_all.py
"""
import json
import os
import numpy as np
import torch
from src.services.data_generator import build_datasets
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.train import train_model
from src.services.experiment_runner import ExperimentResult, save_results
from run_figures import main as generate_figures
from run_rnn_epochs import main as run_rnn_experiment

with open("config/setup.json") as f:
    config = json.load(f)
config["data"]["window_sizes"] = [10]
config["noise"] = {k: v for k, v in config["noise"].items() if k != "med"}

RESULTS_PATH = "outputs/results/results.json"
MODELS_DIR   = "outputs/models"
SIG_NAMES    = ["S1", "S2", "S3", "S4"]
SIG_LABELS   = ["S1 (1Hz)", "S2 (2Hz)", "S3 (5Hz)", "S4 (10Hz)"]
MODEL_MAP    = {"FC": FC, "RNN": SignalRNN, "LSTM": SignalLSTM}
NOISES       = list(config["noise"].keys())
N_EVAL, W    = 200, 10

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs("outputs/results", exist_ok=True)
if os.path.exists(RESULTS_PATH):
    os.remove(RESULTS_PATH)
    print("Deleted old results.json")

results_list = []
total = len(NOISES) * len(MODEL_MAP)
run = 0

for noise in NOISES:
    train_ds, val_ds = build_datasets(config, noise, window_size=W)
    full_ds = val_ds.dataset
    for model_name, ModelClass in MODEL_MAP.items():
        run += 1
        print(f"[{run}/{total}] noise={noise}  W={W}  model={model_name}")
        model = ModelClass(W)
        res   = train_model(model, train_ds, val_ds, config)
        model.save(f"{MODELS_DIR}/{noise}_{model_name}.pt")
        print(f"       saved -> {MODELS_DIR}/{noise}_{model_name}.pt")

        for sig_idx, sig_name in enumerate(SIG_NAMES):
            n_per_sig = len(full_ds) // 4
            model.eval()
            preds_e, tgts_e = [], []
            with torch.no_grad():
                for i in range(N_EVAL):
                    x, y = full_ds[sig_idx * n_per_sig + i * W]
                    preds_e.append(model(x.unsqueeze(0)).squeeze().numpy())
                    tgts_e.append(y.numpy())
            mse = float(np.mean((np.concatenate(preds_e) - np.concatenate(tgts_e)) ** 2))
            results_list.append(ExperimentResult(
                signal=sig_name, noise_level=noise, window_size=W, model=model_name,
                best_mse=mse, best_epoch=res["best_epoch"],
                train_losses=res["train_losses"], val_losses=res["val_losses"],
            ))

save_results(results_list, RESULTS_PATH)

# ── print per-signal summary tables ───────────────────────────────────────────
lookup = {(r.signal, r.noise_level, r.model): r for r in results_list}
for sig_name, sig_label in zip(SIG_NAMES, SIG_LABELS):
    print(f"\n{'='*56}\n  {sig_label}\n{'='*56}")
    print(f"{'Noise':<6}  {'Model':<6}  {'Best Ep':>8}  {'Train MSE':>10}  {'Val MSE':>10}")
    print("-" * 46)
    for noise in NOISES:
        for model_name in MODEL_MAP:
            r  = lookup[(sig_name, noise, model_name)]
            ep = min(r.best_epoch, len(r.train_losses) - 1)
            print(f"{noise:<6}  {model_name:<6}  {r.best_epoch:>8}"
                  f"  {r.train_losses[ep]:>10.4f}  {r.best_mse:>10.4f}")

print(f"\nTraining done. {len(results_list)} results saved.")

print("\n" + "="*56)
print("Generating all figures...")
print("="*56)
generate_figures()

print("\n" + "="*56)
print("Running RNN epochs experiment (50 vs 100)...")
print("="*56)
run_rnn_experiment()

print("\nAll done. Outputs saved to outputs/")
