"""Per-signal figure-drawing helpers used by run_figures.py."""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import torch

BG, PANEL = "#1a1a2e", "#16213e"
SCOL = ["royalblue", "orange", "limegreen", "magenta", "white"]
MCOL = {"FC": "royalblue", "RNN": "orange", "LSTM": "magenta"}


def style(ax):
    """Apply dark-theme styling to a matplotlib Axes."""
    ax.set_facecolor(PANEL); ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white"); ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for s in ax.spines.values(): s.set_edgecolor("#444")


def plot_clean_vs_noisy(figs_dir, sig_idx, sig_name, sig_label,
                        t_wins, clean_n, noisy_seg, alpha_f):
    """Clean target vs noisy S5 scatter — shows separation difficulty."""
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor(BG); style(ax)
    fig.suptitle(f"Source Separation — {sig_label}  (α=β={alpha_f})",
                 fontsize=13, color="white")
    ax.plot(t_wins, clean_n[sig_idx][:len(t_wins)], color=SCOL[sig_idx],
            lw=2, label="Clean target", zorder=3)
    ax.scatter(t_wins, noisy_seg, color="tomato", s=4, alpha=0.6,
               label="Noisy S5 (input)", zorder=2)
    ax.set_ylabel("Amplitude"); ax.set_xlabel("Time (s)")
    ax.legend(facecolor=BG, labelcolor="white", markerscale=4)
    ax.grid(True, alpha=0.2, color="gray")
    plt.tight_layout()
    plt.savefig(f"{figs_dir}/{sig_name}_clean_vs_noisy.png", facecolor=BG)
    plt.close()
    print(f"  Saved: {sig_name}_clean_vs_noisy.png")


def plot_reconstruction(figs_dir, sig_name, sig_label, t_wins,
                        clean_recon, noisy_recon, preds_fig,
                        lookup, noise_fig, W, alpha_f):
    """3-panel reconstruction: one subplot per model with MSE annotation."""
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
    plt.savefig(f"{figs_dir}/{sig_name}_reconstruction.png", facecolor=BG); plt.close()
    print(f"  Saved: {sig_name}_reconstruction.png")


def plot_loss_curves(figs_dir, sig_name, sig_label, lookup, noise_fig, W, alpha_f):
    """Train + val MSE loss curves (log scale) for all three models."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(BG); style(ax)
    for name in MCOL:
        r = lookup[(sig_name, noise_fig, name)]
        ax.plot(r.train_losses, color=MCOL[name], lw=2,   label=f"{name} train")
        ax.plot(r.val_losses,   color=MCOL[name], lw=1.5, ls="--", label=f"{name} val")
    ax.set_title(f"MSE Loss Curves — {sig_label}, α=β={alpha_f}, W={W}", fontsize=12)
    ax.set_xlabel("Epoch"); ax.set_ylabel("MSE (log scale)"); ax.set_yscale("log")
    ax.legend(facecolor=BG, labelcolor="white")
    ax.grid(True, which="both", alpha=0.2, color="gray")
    plt.tight_layout()
    plt.savefig(f"{figs_dir}/{sig_name}_loss_curves.png", facecolor=BG)
    plt.close()
    print(f"  Saved: {sig_name}_loss_curves.png")


def plot_fft_comparison(figs_dir, sig_idx, sig_name, sig_label,
                        clean_win, noisy_win, trained,
                        lookup, noise_fig, freqs_fft, alpha_f, W):
    """FFT spectral analysis — clean vs noisy vs each model prediction."""
    one_hot = torch.zeros(4); one_hot[sig_idx] = 1.0
    x_in = torch.cat([one_hot,
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
    plt.savefig(f"{figs_dir}/{sig_name}_fft_comparison.png", facecolor=BG)
    plt.close()
    print(f"  Saved: {sig_name}_fft_comparison.png")


def plot_winner_heatmap(figs_dir, sig_names, sig_labels, noises, noise_cfg, lookup):
    """2×4 heatmap: best model per signal/noise cell, colour-coded by architecture."""
    COLOR_MAP = {"FC": "royalblue", "RNN": "orange", "LSTM": "magenta"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Best Model per Signal & Noise Level  (val MSE)", fontsize=13, color="white")
    for ax, noise in zip(axes, noises):
        ax.set_facecolor(PANEL)
        ax.set_title(f"Noise: {noise}  (α=β={noise_cfg[noise]['alpha']})",
                     fontsize=11, color="white")
        for col_idx, sig_name in enumerate(sig_names):
            best_model = min(COLOR_MAP, key=lambda m: lookup[(sig_name, noise, m)].best_mse)
            best_mse   = lookup[(sig_name, noise, best_model)].best_mse
            rect = plt.Rectangle([col_idx - 0.4, -0.4], 0.8, 0.8,
                                  color=COLOR_MAP[best_model], alpha=0.85)
            ax.add_patch(rect)
            ax.text(col_idx,  0.15, best_model, ha="center", va="center",
                    color="white", fontsize=13, fontweight="bold")
            ax.text(col_idx, -0.15, f"{best_mse:.4f}", ha="center", va="center",
                    color="white", fontsize=10)
        ax.set_xlim(-0.6, len(sig_names) - 0.4); ax.set_ylim(-0.6, 0.6)
        ax.set_xticks(range(len(sig_names)))
        ax.set_xticklabels(sig_labels, color="white", fontsize=10)
        ax.set_yticks([]); ax.tick_params(colors="white")
        for s in ax.spines.values(): s.set_edgecolor("#444")
    handles = [Patch(color=c, label=m) for m, c in COLOR_MAP.items()]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               facecolor=BG, labelcolor="white", fontsize=11, framealpha=0.8)
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(f"{figs_dir}/winner_heatmap.png", facecolor=BG); plt.close()
    print("Saved: winner_heatmap.png")
