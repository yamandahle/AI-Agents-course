"""run_figures.py — Generate all 19 figures from saved models + results.json.
Requires run_all.py to have been executed at least once (models + results on disk).
Safe to re-run anytime — fast (~10 s), no retraining.
Can also be called from run_all.py via main().
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from src.services.data_generator import build_datasets, SignalGenerator
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.experiment_runner import ExperimentResult
from src.services.figure_plotter import (
    BG, PANEL, SCOL, MCOL, style,
    plot_clean_vs_noisy, plot_reconstruction,
    plot_loss_curves, plot_fft_comparison, plot_winner_heatmap,
)

FIGS_DIR   = "outputs/figures"
MODELS_DIR = "outputs/models"


def main():
    os.makedirs(FIGS_DIR, exist_ok=True)
    with open("config/setup.json") as f:
        config = json.load(f)
    config["data"]["window_sizes"] = [10]
    config["noise"] = {k: v for k, v in config["noise"].items() if k != "med"}

    SIG_NAMES  = ["S1", "S2", "S3", "S4"]
    SIG_LABELS = ["S1 (1Hz)", "S2 (2Hz)", "S3 (5Hz)", "S4 (10Hz)"]
    MODEL_MAP  = {"FC": FC, "RNN": SignalRNN, "LSTM": SignalLSTM}
    NOISES     = list(config["noise"].keys())
    W, FS      = 10, config["signal"]["sample_rate"]
    N_WINS     = int(2.0 * FS) // W

    with open("outputs/results/results.json") as f:
        results_list = [ExperimentResult(**r) for r in json.load(f)]
    lookup = {(r.signal, r.noise_level, r.model): r for r in results_list}

    trained = {}
    for noise in NOISES:
        for name, ModelClass in MODEL_MAP.items():
            m = ModelClass(W)
            m.load(f"{MODELS_DIR}/{noise}_{name}.pt")
            m.eval()
            trained[(noise, name)] = m

    gen       = SignalGenerator(config)
    t_wins    = gen.t[:N_WINS * W]
    clean_raw = [gen.clean(i) for i in range(4)] + [gen.clean_s5()]
    norms     = [float(np.max(np.abs(s))) or 1.0 for s in clean_raw]
    clean_n   = [s / n for s, n in zip(clean_raw, norms)]

    val_datasets = {}
    for noise in NOISES:
        _, val_ds = build_datasets(config, noise, window_size=W)
        val_datasets[noise] = val_ds

    # ── signals overview ──────────────────────────────────────────────────────
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(14, 7))
    fig.patch.set_facecolor(BG)
    fig.suptitle("All Signals Overview", fontsize=13, color="white")
    style(a1); style(a2)
    for i in range(4):
        a1.plot(t_wins, clean_n[i][:N_WINS*W], color=SCOL[i], lw=1.8, label=SIG_LABELS[i])
    a1.set_title("Individual Sinusoids S1–S4", fontsize=11)
    a1.set_ylabel("Amplitude"); a1.set_xlabel("Time (s)")
    a1.legend(facecolor=BG, labelcolor="white"); a1.grid(True, alpha=0.2, color="gray")
    a2.plot(t_wins, clean_n[4][:N_WINS*W], color="white", lw=2)
    a2.set_title("Combined Signal S5 = S1+S2+S3+S4 (Clean)", fontsize=11)
    a2.set_ylabel("Amplitude"); a2.set_xlabel("Time (s)"); a2.grid(True, alpha=0.2, color="gray")
    plt.tight_layout()
    plt.savefig(f"{FIGS_DIR}/signals_overview.png", facecolor=BG); plt.close()
    print("Saved: signals_overview.png")

    # ── per-signal figures ────────────────────────────────────────────────────
    noise_fig  = "low"
    alpha_f    = config["noise"][noise_fig]["alpha"]
    beta_f     = config["noise"][noise_fig]["beta"]
    val_ds_fig = val_datasets[noise_fig]
    freqs_fft  = np.fft.rfftfreq(W, d=1.0 / FS)

    for sig_idx, (sig_name, sig_label) in enumerate(zip(SIG_NAMES, SIG_LABELS)):
        print(f"\nGenerating figures for {sig_name}...")
        n_per_sig = len(val_ds_fig.dataset) // 4
        sig_start = sig_idx * n_per_sig

        np.random.seed(config["data"]["seed"])
        noisy_seg = np.concatenate([
            gen.noisy_s5_window(i * W, W, alpha_f, beta_f) for i in range(N_WINS)
        ]) / norms[4]
        plot_clean_vs_noisy(FIGS_DIR, sig_idx, sig_name, sig_label,
                            t_wins, clean_n, noisy_seg, alpha_f)

        clean_recon = np.concatenate([
            val_ds_fig.dataset[sig_start + i * W][1].numpy() for i in range(N_WINS)
        ])
        one_hot_t = torch.zeros(4); one_hot_t[sig_idx] = 1.0
        np.random.seed(config["data"]["seed"] + 1)
        noisy_recon, preds_fig = [], {name: [] for name in MCOL}
        with torch.no_grad():
            for i in range(N_WINS):
                win = gen.noisy_s5_window(i * W, W, alpha_f, beta_f) / norms[4]
                noisy_recon.append(win)
                x = torch.cat([one_hot_t, torch.tensor(win, dtype=torch.float32)]).unsqueeze(0)
                for name in MCOL:
                    preds_fig[name].append(trained[(noise_fig, name)](x).squeeze().numpy())
        noisy_recon = np.concatenate(noisy_recon)
        preds_fig   = {n: np.concatenate(p) for n, p in preds_fig.items()}
        plot_reconstruction(FIGS_DIR, sig_name, sig_label, t_wins,
                            clean_recon, noisy_recon, preds_fig,
                            lookup, noise_fig, W, alpha_f)

        plot_loss_curves(FIGS_DIR, sig_name, sig_label, lookup, noise_fig, W, alpha_f)

        clean_win = val_ds_fig.dataset[sig_start][1].numpy()
        noisy_win = gen.noisy_s5_window(0, W, alpha_f, beta_f) / norms[4]
        plot_fft_comparison(FIGS_DIR, sig_idx, sig_name, sig_label,
                            clean_win, noisy_win, trained,
                            lookup, noise_fig, freqs_fft, alpha_f, W)

    # ── winner heatmap ────────────────────────────────────────────────────────
    print("\nGenerating winner heatmap...")
    plot_winner_heatmap(FIGS_DIR, SIG_NAMES, SIG_LABELS, NOISES,
                        config["noise"], lookup)

    print(f"\nAll 19 figures saved to {FIGS_DIR}/")


if __name__ == "__main__":
    main()
