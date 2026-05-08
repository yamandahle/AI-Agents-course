"""run_rnn_epochs.py — RNN epochs experiment (50 vs 100).

Loads FC, LSTM, RNN 50-epoch histories from results.json (no retraining needed).
Trains a fresh RNN for 100 epochs, then plots all four curves together.
Shows empirically that more epochs help RNN but it still cannot match LSTM-50.
Can also be called from run_all.py via main().
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.services.data_generator import build_datasets
from src.sdk.models.rnn import SignalRNN
from src.services.train import train_model

FIGS_DIR = "outputs/figures"
BG, PANEL = "#1a1a2e", "#16213e"


def style(ax):
    ax.set_facecolor(PANEL); ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white"); ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for s in ax.spines.values(): s.set_edgecolor("#444")


def main():
    os.makedirs(FIGS_DIR, exist_ok=True)

    with open("config/setup.json") as f:
        config = json.load(f)
    config["data"]["window_sizes"] = [10]

    W, NOISE = 10, "low"

    # load 50-epoch histories from results.json
    with open("outputs/results/results.json") as f:
        all_results = json.load(f)

    def get_val_losses(model_name):
        for r in all_results:
            if r["model"] == model_name and r["noise_level"] == NOISE:
                return r["val_losses"]
        raise ValueError(f"No results for model={model_name} noise={NOISE}")

    rnn50_val  = get_val_losses("RNN")
    lstm50_val = get_val_losses("LSTM")
    fc50_val   = get_val_losses("FC")

    # train RNN for 100 epochs
    print("Training RNN for 100 epochs (low noise, W=10)...")
    cfg100 = {**config, "training": {**config["training"], "epochs": 100}}
    train_ds, val_ds = build_datasets(cfg100, NOISE, window_size=W)
    res100 = train_model(SignalRNN(W), train_ds, val_ds, cfg100)
    rnn100_val = res100["val_losses"]
    print(f"RNN-100 best val MSE: {res100['best_val_mse']:.5f}  (epoch {res100['best_epoch']})")

    # plot
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(BG); style(ax)

    ax.plot(fc50_val,   color="royalblue", lw=2,   ls="-",  label="FC — 50 epochs")
    ax.plot(lstm50_val, color="magenta",   lw=2,   ls="-",  label="LSTM — 50 epochs")
    ax.plot(rnn50_val,  color="orange",    lw=1.8, ls="--", label="RNN — 50 epochs")
    ax.plot(rnn100_val, color="orange",    lw=2.5, ls="-",  label="RNN — 100 epochs")

    ax.set_title(
        "RNN Epochs Experiment — more training helps RNN, but LSTM-50 still wins",
        fontsize=12, color="white"
    )
    ax.set_xlabel("Epoch"); ax.set_ylabel("Val MSE (log scale)")
    ax.set_yscale("log")
    ax.legend(facecolor=BG, labelcolor="white", fontsize=11)
    ax.grid(True, which="both", alpha=0.2, color="gray")

    out_path = f"{FIGS_DIR}/rnn_epochs_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path, facecolor=BG); plt.close()
    print(f"Saved: {out_path}")

    print("\nFinal val MSE comparison (low noise, W=10):")
    print(f"  FC    50ep : {min(fc50_val):.5f}")
    print(f"  LSTM  50ep : {min(lstm50_val):.5f}")
    print(f"  RNN   50ep : {min(rnn50_val):.5f}")
    print(f"  RNN  100ep : {res100['best_val_mse']:.5f}")


if __name__ == "__main__":
    main()
