import json, os
import numpy as np
import matplotlib.pyplot as plt
import torch
from src.services.data_generator import build_datasets, SignalGenerator
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.train import train_model

# ══ CHANGE THIS to run for a different signal ══════════════════════════════════
SIGNAL_TO_EXTRACT = 1   # 0=S1  1=S2  2=S3  3=S4
# ══════════════════════════════════════════════════════════════════════════════

W = 10
SHOW_S = 2.0

with open("config/setup.json") as f:
    config = json.load(f)

FS    = config["signal"]["sample_rate"]
NAMES = ["S1 (1Hz)", "S2 (2Hz)", "S3 (5Hz)", "S4 (10Hz)", "S5 (sum)"]
SCOL  = ["royalblue", "orange", "limegreen", "magenta", "white"]
MCOL  = {"FC": "royalblue", "RNN": "orange", "LSTM": "magenta"}
SIG   = NAMES[SIGNAL_TO_EXTRACT].split()[0]   # "S1" … "S5"

N_SHOW = int(SHOW_S * FS)
N_WINS = N_SHOW // W
BG, PANEL = "#1a1a2e", "#16213e"
os.makedirs("outputs/figures", exist_ok=True)

def style(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for s in ax.spines.values(): s.set_edgecolor("#444")

def noisy_stitched(gen, alpha, beta, n_wins, W, norm):
    """Fresh σ per window → noisy S5 mixture (model input) for display."""
    return np.concatenate([
        gen.noisy_s5_window(i * W, W, alpha, beta)
        for i in range(n_wins)
    ]) / norm

# ── generate clean signals ────────────────────────────────────────────────────
gen = SignalGenerator(config)
np.random.seed(config["data"]["seed"])
clean_raw  = [gen.clean(i) for i in range(4)] + [gen.clean_s5()]
norms      = [float(np.max(np.abs(s))) or 1.0 for s in clean_raw]
clean_n    = [s / n for s, n in zip(clean_raw, norms)]
t_full     = gen.t[:N_SHOW]
t_wins     = gen.t[:N_WINS * W]

# ── FIGURE 1: all 5 signals ───────────────────────────────────────────────────
fig, (a1, a2) = plt.subplots(2, 1, figsize=(14, 7))
fig.patch.set_facecolor(BG)
fig.suptitle("All Signals Overview", fontsize=13, color="white")
style(a1); style(a2)

for i in range(4):
    a1.plot(t_full, clean_n[i][:N_SHOW], color=SCOL[i], lw=1.8, label=NAMES[i])
a1.set_title("Individual Sinusoids — S1 to S4", fontsize=11)
a1.set_ylabel("Amplitude"); a1.set_xlabel("Time (s)")
a1.legend(facecolor=BG, labelcolor="white"); a1.grid(True, alpha=0.2, color="gray")

a2.plot(t_full, clean_n[4][:N_SHOW], color="white", lw=2)
a2.set_title("Combined Signal S5 = S1 + S2 + S3 + S4 (Clean)", fontsize=11)
a2.set_ylabel("Amplitude"); a2.set_xlabel("Time (s)")
a2.grid(True, alpha=0.2, color="gray")

plt.tight_layout()
plt.savefig("outputs/figures/signals_overview.png", facecolor=BG)
plt.close(); print("Saved: signals_overview.png")

# ── FIGURE 2: chosen signal — clean vs noisy at 3 levels (stacked) ───────────
noise_levels = list(config["noise"].items())   # [("low",..), ("med",..), ("high",..)]

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
fig.patch.set_facecolor(BG)
fig.suptitle(f"Source Separation: Noisy S5 Input vs Clean Target — {NAMES[SIGNAL_TO_EXTRACT]}",
             fontsize=13, color="white")

for ax, (level, nc) in zip(axes, noise_levels):
    style(ax)
    a, b = nc["alpha"], nc["beta"]
    noisy = noisy_stitched(gen, a, b, N_WINS, W, norms[4])
    clean_seg = clean_n[SIGNAL_TO_EXTRACT][:N_WINS * W]
    ax.plot(t_wins, clean_seg, color=SCOL[SIGNAL_TO_EXTRACT], lw=2, label="Clean target", zorder=3)
    ax.scatter(t_wins, noisy, color="tomato", s=4, alpha=0.6, label="Noisy S5 (input)", zorder=2)
    ax.set_title(f"{level.upper()} noise  (α = β = {a})", fontsize=11)
    ax.set_ylabel("Amplitude")
    ax.legend(facecolor=BG, labelcolor="white", markerscale=4)
    ax.grid(True, alpha=0.2, color="gray")
axes[-1].set_xlabel("Time (s)")
plt.tight_layout()
plt.savefig(f"outputs/figures/{SIG}_clean_vs_noisy.png", facecolor=BG)
plt.close(); print(f"Saved: {SIG}_clean_vs_noisy.png")

# ── TRAIN ─────────────────────────────────────────────────────────────────────
train_ds, val_ds = build_datasets(config, "low", window_size=W)
model_map = {"FC": FC(W), "RNN": SignalRNN(W), "LSTM": SignalLSTM(W)}
results = {}
for name, model in model_map.items():
    print(f"Training {name}...")
    res = train_model(model, train_ds, val_ds, config)
    results[name] = {"model": model, **res}
    print(f"  best val MSE: {res['best_val_mse']:.6f} at epoch {res['best_epoch']}")

# ── build reconstruction arrays ───────────────────────────────────────────────
n_per_sig = len(val_ds.dataset) // 4
sig_start = SIGNAL_TO_EXTRACT * n_per_sig

clean_recon = np.concatenate([val_ds.dataset[sig_start + i*W][1].numpy() for i in range(N_WINS)])

one_hot_t = torch.zeros(4); one_hot_t[SIGNAL_TO_EXTRACT] = 1.0

def recon_at_noise(model, alpha, beta):
    """Inference on fresh noisy S5 windows at a given noise level."""
    np.random.seed(config["data"]["seed"] + 1)
    model.eval()
    noisy_disp, preds = [], []
    with torch.no_grad():
        for i in range(N_WINS):
            win = gen.noisy_s5_window(i * W, W, alpha, beta) / norms[4]
            noisy_disp.append(win)
            x = torch.cat([one_hot_t,
                           torch.tensor(win, dtype=torch.float32)]).unsqueeze(0)
            preds.append(model(x).squeeze().numpy())
    return np.concatenate(noisy_disp), np.concatenate(preds)

def eval_mse_at_noise(model, alpha, beta):
    """MSE over N_WINS windows at a given noise level."""
    np.random.seed(config["data"]["seed"] + 2)
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(N_WINS):
            win = gen.noisy_s5_window(i * W, W, alpha, beta) / norms[4]
            x = torch.cat([one_hot_t,
                           torch.tensor(win, dtype=torch.float32)]).unsqueeze(0)
            preds.append(model(x).squeeze().numpy())
    return float(np.mean((np.concatenate(preds) - clean_recon) ** 2))

# ── evaluate MSE at all 3 noise levels ───────────────────────────────────────
noise_mses = {name: {} for name in MCOL}
print(f"\nVal MSE by noise level — {NAMES[SIGNAL_TO_EXTRACT]}, W={W}")
print(f"{'Model':<8} {'LOW':>10} {'MED':>10} {'HIGH':>10}")
for name, res in results.items():
    row = f"{name:<8}"
    for level, nc in noise_levels:
        mse = eval_mse_at_noise(res["model"], nc["alpha"], nc["beta"])
        noise_mses[name][level] = mse
        row += f" {mse:>10.6f}"
    print(row)

# ── FIGURE 3: reconstruction — 3 models × 3 noise levels ─────────────────────
fig, axes = plt.subplots(3, 3, figsize=(18, 11), sharex=True, sharey=True)
fig.patch.set_facecolor(BG)
fig.suptitle(
    f"Reconstruction — {NAMES[SIGNAL_TO_EXTRACT]}, W={W}  (trained on Low Noise)",
    fontsize=13, color="white")

for row, name in enumerate(["FC", "RNN", "LSTM"]):
    for col, (level, nc) in enumerate(noise_levels):
        ax = axes[row][col]
        style(ax)
        noisy_disp, pred = recon_at_noise(results[name]["model"], nc["alpha"], nc["beta"])
        ax.scatter(t_wins, noisy_disp, color="gray", s=2, alpha=0.3, zorder=2)
        ax.plot(t_wins, clean_recon, color="limegreen", lw=1.8, label="Clean target", zorder=4)
        ax.plot(t_wins, pred, color=MCOL[name], lw=1.5, ls="--",
                label=f"{name} pred", zorder=3)
        if row == 0:
            ax.set_title(f"{level.upper()} noise  (α={nc['alpha']})", fontsize=10)
        if col == 0:
            ax.set_ylabel(f"{name}\nAmplitude", fontsize=9)
        if row == 2:
            ax.set_xlabel("Time (s)")
        ax.legend(facecolor=BG, labelcolor="white", markerscale=3, fontsize=7)
        ax.grid(True, alpha=0.2, color="gray")

plt.tight_layout()
plt.savefig(f"outputs/figures/{SIG}_reconstruction.png", facecolor=BG)
plt.close(); print(f"Saved: {SIG}_reconstruction.png")

# ── FIGURE 4: loss curves ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG); style(ax)
for name, res in results.items():
    ax.plot(res["train_losses"], color=MCOL[name], lw=2, label=f"{name} train")
    ax.plot(res["val_losses"], color=MCOL[name], lw=1.5, ls="--", label=f"{name} val")
ax.set_title(f"MSE Loss Curves — {NAMES[SIGNAL_TO_EXTRACT]}, Low Noise, W={W}", fontsize=12)
ax.set_xlabel("Epoch"); ax.set_ylabel("MSE (log scale)"); ax.set_yscale("log")
ax.legend(facecolor=BG, labelcolor="white")
ax.grid(True, which="both", alpha=0.2, color="gray")
plt.tight_layout()
plt.savefig(f"outputs/figures/{SIG}_loss_curves.png", facecolor=BG)
plt.close(); print(f"Saved: {SIG}_loss_curves.png")

# ── FIGURE 5: MSE grouped bar chart — models × noise levels ──────────────────
x = np.arange(len(MCOL))
width = 0.25
level_colors = {"low": "#4a9eff", "med": "#ffaa33", "high": "#ff4455"}

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG); style(ax)
for i, (level, _) in enumerate(noise_levels):
    mses = [noise_mses[n][level] for n in MCOL]
    bars = ax.bar(x + i * width, mses, width,
                  label=f"{level.upper()} noise", color=level_colors[level], alpha=0.85)
    for bar, val in zip(bars, mses):
        ax.text(bar.get_x() + bar.get_width() / 2, val * 1.12,
                f"{val:.4f}", ha="center", color="white", fontsize=8, rotation=45)
ax.set_xticks(x + width)
ax.set_xticklabels(list(MCOL))
ax.set_title(f"Val MSE by Noise Level — {NAMES[SIGNAL_TO_EXTRACT]}, W={W}", fontsize=12)
ax.set_ylabel("MSE"); ax.set_yscale("log")
ax.legend(facecolor=BG, labelcolor="white")
ax.grid(True, axis="y", which="both", alpha=0.2, color="gray")
plt.tight_layout()
plt.savefig(f"outputs/figures/{SIG}_mse_bar.png", facecolor=BG)
plt.close(); print(f"Saved: {SIG}_mse_bar.png")

print(f"\nDone. Change SIGNAL_TO_EXTRACT (0–4) at the top to run for other signals.")
