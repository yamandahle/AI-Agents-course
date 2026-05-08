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
from matplotlib.patches import Patch
from src.services.data_generator import build_datasets, SignalGenerator
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.experiment_runner import ExperimentResult

FIGS_DIR   = "outputs/figures"
MODELS_DIR = "outputs/models"
BG, PANEL  = "#1a1a2e", "#16213e"
SCOL       = ["royalblue", "orange", "limegreen", "magenta", "white"]
MCOL       = {"FC": "royalblue", "RNN": "orange", "LSTM": "magenta"}


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
    config["noise"] = {k: v for k, v in config["noise"].items() if k != "med"}

    SIG_NAMES  = ["S1", "S2", "S3", "S4"]
    SIG_LABELS = ["S1 (1Hz)", "S2 (2Hz)", "S3 (5Hz)", "S4 (10Hz)"]
    MODEL_MAP  = {"FC": FC, "RNN": SignalRNN, "LSTM": SignalLSTM}
    NOISES     = list(config["noise"].keys())
    W          = 10
    FS         = config["signal"]["sample_rate"]
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

        # clean vs noisy
        np.random.seed(config["data"]["seed"])
        noisy_seg = np.concatenate([
            gen.noisy_s5_window(i * W, W, alpha_f, beta_f) for i in range(N_WINS)
        ]) / norms[4]
        fig, ax = plt.subplots(figsize=(14, 5)); fig.patch.set_facecolor(BG); style(ax)
        fig.suptitle(f"Source Separation — {sig_label}  (α=β={alpha_f})",
                     fontsize=13, color="white")
        ax.plot(t_wins, clean_n[sig_idx][:N_WINS*W], color=SCOL[sig_idx], lw=2,
                label="Clean target", zorder=3)
        ax.scatter(t_wins, noisy_seg, color="tomato", s=4, alpha=0.6,
                   label="Noisy S5 (input)", zorder=2)
        ax.set_ylabel("Amplitude"); ax.set_xlabel("Time (s)")
        ax.legend(facecolor=BG, labelcolor="white", markerscale=4)
        ax.grid(True, alpha=0.2, color="gray")
        plt.tight_layout()
        plt.savefig(f"{FIGS_DIR}/{sig_name}_clean_vs_noisy.png", facecolor=BG); plt.close()
        print(f"  Saved: {sig_name}_clean_vs_noisy.png")

        # reconstruction
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

        fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
        fig.patch.set_facecolor(BG)
        fig.suptitle(f"Reconstruction — {sig_label}, α=β={alpha_f}, W={W}",
                     fontsize=13, color="white")
        for ax, name in zip(axes, ["FC", "RNN", "LSTM"]):
            style(ax)
            ax.scatter(t_wins, noisy_recon, color="gray", s=3, alpha=0.35,
                       label="Noisy S5 (input)", zorder=2)
            ax.plot(t_wins, clean_recon, color="limegreen", lw=2,
                    label="Clean target", zorder=4)
            ax.plot(t_wins, preds_fig[name], color=MCOL[name], lw=1.8, ls="--",
                    label=f"{name} prediction", zorder=3)
            r = lookup[(sig_name, noise_fig, name)]
            ax.set_title(f"{name}   best val MSE = {r.best_mse:.6f}", fontsize=11)
            ax.set_ylabel("Amplitude")
            ax.legend(facecolor=BG, labelcolor="white", markerscale=4)
            ax.grid(True, alpha=0.2, color="gray")
        axes[-1].set_xlabel("Time (s)")
        plt.tight_layout()
        plt.savefig(f"{FIGS_DIR}/{sig_name}_reconstruction.png", facecolor=BG); plt.close()
        print(f"  Saved: {sig_name}_reconstruction.png")

        # loss curves
        fig, ax = plt.subplots(figsize=(10, 5)); fig.patch.set_facecolor(BG); style(ax)
        for name in MCOL:
            r = lookup[(sig_name, noise_fig, name)]
            ax.plot(r.train_losses, color=MCOL[name], lw=2,   label=f"{name} train")
            ax.plot(r.val_losses,   color=MCOL[name], lw=1.5, ls="--", label=f"{name} val")
        ax.set_title(f"MSE Loss Curves — {sig_label}, α=β={alpha_f}, W={W}", fontsize=12)
        ax.set_xlabel("Epoch"); ax.set_ylabel("MSE (log scale)"); ax.set_yscale("log")
        ax.legend(facecolor=BG, labelcolor="white")
        ax.grid(True, which="both", alpha=0.2, color="gray")
        plt.tight_layout()
        plt.savefig(f"{FIGS_DIR}/{sig_name}_loss_curves.png", facecolor=BG); plt.close()
        print(f"  Saved: {sig_name}_loss_curves.png")

        # FFT spectral comparison
        clean_win  = val_ds_fig.dataset[sig_start][1].numpy()
        noisy_win  = gen.noisy_s5_window(0, W, alpha_f, beta_f) / norms[4]
        one_hot_t2 = torch.zeros(4); one_hot_t2[sig_idx] = 1.0
        x_in = torch.cat([one_hot_t2,
                           torch.tensor(noisy_win, dtype=torch.float32)]).unsqueeze(0)

        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        fig.patch.set_facecolor(BG)
        fig.suptitle(f"FFT Spectral Analysis — {sig_label}  (α=β={alpha_f}, W={W})",
                     fontsize=13, color="white")
        for ax, name in zip(axes, ["FC", "RNN", "LSTM"]):
            style(ax)
            with torch.no_grad():
                pred_win = trained[(noise_fig, name)](x_in).squeeze().numpy()
            ax.plot(freqs_fft, np.abs(np.fft.rfft(clean_win)),
                    color="limegreen", lw=2,   label="Clean target")
            ax.plot(freqs_fft, np.abs(np.fft.rfft(noisy_win)),
                    color="tomato",    lw=1.2, ls="--", alpha=0.7, label="Noisy S5 input")
            ax.plot(freqs_fft, np.abs(np.fft.rfft(pred_win)),
                    color=MCOL[name],  lw=2,   ls="-.", label=f"{name} prediction")
            r = lookup[(sig_name, noise_fig, name)]
            ax.set_title(f"{name}   val MSE = {r.best_mse:.5f}", fontsize=11)
            ax.set_ylabel("Magnitude"); ax.set_yscale("log")
            ax.legend(facecolor=BG, labelcolor="white")
            ax.grid(True, which="both", alpha=0.2, color="gray")
        axes[-1].set_xlabel("Frequency (Hz)")
        plt.tight_layout()
        plt.savefig(f"{FIGS_DIR}/{sig_name}_fft_comparison.png", facecolor=BG); plt.close()
        print(f"  Saved: {sig_name}_fft_comparison.png")

    # ── winner heatmap ────────────────────────────────────────────────────────
    print("\nGenerating winner heatmap...")
    COLOR_MAP = {"FC": "royalblue", "RNN": "orange", "LSTM": "magenta"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Best Model per Signal & Noise Level  (val MSE)",
                 fontsize=13, color="white")
    for ax, noise in zip(axes, NOISES):
        ax.set_facecolor(PANEL)
        ax.set_title(f"Noise: {noise}  (α=β={config['noise'][noise]['alpha']})",
                     fontsize=11, color="white")
        for col_idx, sig_name in enumerate(SIG_NAMES):
            best_model = min(MODEL_MAP, key=lambda m: lookup[(sig_name, noise, m)].best_mse)
            best_mse   = lookup[(sig_name, noise, best_model)].best_mse
            rect = plt.Rectangle([col_idx - 0.4, -0.4], 0.8, 0.8,
                                  color=COLOR_MAP[best_model], alpha=0.85)
            ax.add_patch(rect)
            ax.text(col_idx,  0.15, best_model, ha="center", va="center",
                    color="white", fontsize=13, fontweight="bold")
            ax.text(col_idx, -0.15, f"{best_mse:.4f}", ha="center", va="center",
                    color="white", fontsize=10)
        ax.set_xlim(-0.6, len(SIG_NAMES) - 0.4); ax.set_ylim(-0.6, 0.6)
        ax.set_xticks(range(len(SIG_NAMES)))
        ax.set_xticklabels(SIG_LABELS, color="white", fontsize=10)
        ax.set_yticks([]); ax.tick_params(colors="white")
        for s in ax.spines.values(): s.set_edgecolor("#444")

    legend_handles = [Patch(color=c, label=m) for m, c in COLOR_MAP.items()]
    fig.legend(handles=legend_handles, loc="lower center", ncol=3,
               facecolor=BG, labelcolor="white", fontsize=11, framealpha=0.8)
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(f"{FIGS_DIR}/winner_heatmap.png", facecolor=BG); plt.close()
    print("Saved: winner_heatmap.png")

    print(f"\nAll 19 figures saved to {FIGS_DIR}/")


if __name__ == "__main__":
    main()
