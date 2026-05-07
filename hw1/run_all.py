"""run_all.py — Train, evaluate, save results, print tables, generate all figures."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from src.services.data_generator import build_datasets, SignalGenerator
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.train import train_model
from src.services.experiment_runner import ExperimentResult, save_results

# ── config ────────────────────────────────────────────────────────────────────
with open("config/setup.json") as f:
    config = json.load(f)
config["data"]["window_sizes"] = [10]
config["noise"] = {k: v for k, v in config["noise"].items() if k != "med"}

RESULTS_PATH = "outputs/results/results.json"
FIGS_DIR = "outputs/figures"
os.makedirs(FIGS_DIR, exist_ok=True)
if os.path.exists(RESULTS_PATH):
    os.remove(RESULTS_PATH)
    print("Deleted old results.json")

SIG_NAMES  = ["S1", "S2", "S3", "S4"]
SIG_LABELS = ["S1 (1Hz)", "S2 (2Hz)", "S3 (5Hz)", "S4 (10Hz)"]
MODEL_MAP  = {"FC": FC, "RNN": SignalRNN, "LSTM": SignalLSTM}
NOISES     = list(config["noise"].keys())   # ["low", "high"]
N_EVAL, W  = 200, 10
BG, PANEL  = "#1a1a2e", "#16213e"
SCOL       = ["royalblue", "orange", "limegreen", "magenta", "white"]
MCOL       = {"FC": "royalblue", "RNN": "orange", "LSTM": "magenta"}

def style(ax):
    ax.set_facecolor(PANEL); ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white"); ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for s in ax.spines.values(): s.set_edgecolor("#444")

# ── clean signals for figures ─────────────────────────────────────────────────
gen    = SignalGenerator(config)
FS     = config["signal"]["sample_rate"]
N_WINS = int(2.0 * FS) // W
t_wins = gen.t[:N_WINS * W]
clean_raw = [gen.clean(i) for i in range(4)] + [gen.clean_s5()]
norms     = [float(np.max(np.abs(s))) or 1.0 for s in clean_raw]
clean_n   = [s / n for s, n in zip(clean_raw, norms)]

# signals overview (once)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(14, 7))
fig.patch.set_facecolor(BG); fig.suptitle("All Signals Overview", fontsize=13, color="white")
style(a1); style(a2)
for i in range(4):
    a1.plot(gen.t[:N_WINS*W], clean_n[i][:N_WINS*W], color=SCOL[i], lw=1.8, label=SIG_LABELS[i])
a1.set_title("Individual Sinusoids S1-S4", fontsize=11); a1.set_ylabel("Amplitude"); a1.set_xlabel("Time (s)")
a1.legend(facecolor=BG, labelcolor="white"); a1.grid(True, alpha=0.2, color="gray")
a2.plot(gen.t[:N_WINS*W], clean_n[4][:N_WINS*W], color="white", lw=2)
a2.set_title("Combined Signal S5 = S1+S2+S3+S4 (Clean)", fontsize=11)
a2.set_ylabel("Amplitude"); a2.set_xlabel("Time (s)"); a2.grid(True, alpha=0.2, color="gray")
plt.tight_layout(); plt.savefig(f"{FIGS_DIR}/signals_overview.png", facecolor=BG); plt.close()
print("Saved: signals_overview.png")

# ── training loop ─────────────────────────────────────────────────────────────
results_list = []
trained      = {}   # (noise, model_name) -> {"model", "best_val_mse", "train_losses", "val_losses"}
val_datasets = {}   # noise -> val_ds
total = len(NOISES) * len(MODEL_MAP)
run = 0

for noise in NOISES:
    train_ds, val_ds = build_datasets(config, noise, window_size=W)
    val_datasets[noise] = val_ds
    full_ds = val_ds.dataset
    for model_name, ModelClass in MODEL_MAP.items():
        run += 1
        print(f"[{run}/{total}] noise={noise} W={W} model={model_name}")
        model = ModelClass(W)
        res = train_model(model, train_ds, val_ds, config)
        trained[(noise, model_name)] = {"model": model, **res}
        for sig_idx, sig_name in enumerate(SIG_NAMES):
            n_per_sig = len(full_ds) // 4
            model.eval(); preds_e, tgts_e = [], []
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

# ── per-signal tables ─────────────────────────────────────────────────────────
lookup = {(r.signal, r.noise_level, r.model): r for r in results_list}
for sig_name, sig_label in zip(SIG_NAMES, SIG_LABELS):
    print(f"\n{'='*56}")
    print(f"  {sig_label}")
    print(f"{'='*56}")
    print(f"{'Noise':<6}  {'Model':<6}  {'Best Ep':>8}  {'Train MSE':>10}  {'Val MSE':>10}")
    print("-" * 46)
    for noise in NOISES:
        for model in MODEL_MAP:
            r = lookup[(sig_name, noise, model)]
            ep = min(r.best_epoch, len(r.train_losses) - 1)
            print(f"{noise:<6}  {model:<6}  {r.best_epoch:>8}  {r.train_losses[ep]:>10.4f}  {r.best_mse:>10.4f}")

# ── figures per signal (low noise) ───────────────────────────────────────────
noise_fig = "low"
alpha_f   = config["noise"][noise_fig]["alpha"]
beta_f    = config["noise"][noise_fig]["beta"]
val_ds_fig = val_datasets[noise_fig]

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
    fig.suptitle(f"Source Separation - {sig_label}  (a=b={alpha_f}, noisy S5 vs clean target)",
                 fontsize=13, color="white")
    ax.plot(t_wins, clean_n[sig_idx][:N_WINS*W], color=SCOL[sig_idx], lw=2, label="Clean target", zorder=3)
    ax.scatter(t_wins, noisy_seg, color="tomato", s=4, alpha=0.6, label="Noisy S5 (input)", zorder=2)
    ax.set_ylabel("Amplitude"); ax.set_xlabel("Time (s)")
    ax.legend(facecolor=BG, labelcolor="white", markerscale=4); ax.grid(True, alpha=0.2, color="gray")
    plt.tight_layout(); plt.savefig(f"{FIGS_DIR}/{sig_name}_clean_vs_noisy.png", facecolor=BG); plt.close()
    print(f"  Saved: {sig_name}_clean_vs_noisy.png")

    # reconstruction
    clean_recon = np.concatenate([val_ds_fig.dataset[sig_start + i*W][1].numpy() for i in range(N_WINS)])
    one_hot_t   = torch.zeros(4); one_hot_t[sig_idx] = 1.0
    np.random.seed(config["data"]["seed"] + 1)
    noisy_recon, preds_fig = [], {name: [] for name in MCOL}
    with torch.no_grad():
        for i in range(N_WINS):
            win = gen.noisy_s5_window(i * W, W, alpha_f, beta_f) / norms[4]
            noisy_recon.append(win)
            x = torch.cat([one_hot_t, torch.tensor(win, dtype=torch.float32)]).unsqueeze(0)
            for name in MCOL:
                trained[(noise_fig, name)]["model"].eval()
                preds_fig[name].append(trained[(noise_fig, name)]["model"](x).squeeze().numpy())
    noisy_recon = np.concatenate(noisy_recon)
    preds_fig   = {n: np.concatenate(p) for n, p in preds_fig.items()}

    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    fig.patch.set_facecolor(BG)
    fig.suptitle(f"Reconstruction - {sig_label}, a=b={alpha_f}, W={W}", fontsize=13, color="white")
    for ax, name in zip(axes, ["FC", "RNN", "LSTM"]):
        style(ax)
        ax.scatter(t_wins, noisy_recon, color="gray", s=3, alpha=0.35, label="Noisy S5 (input)", zorder=2)
        ax.plot(t_wins, clean_recon, color="limegreen", lw=2, label="Clean target", zorder=4)
        ax.plot(t_wins, preds_fig[name], color=MCOL[name], lw=1.8, ls="--", label=f"{name} prediction", zorder=3)
        r = lookup[(sig_name, noise_fig, name)]
        ax.set_title(f"{name}   best val MSE = {r.best_mse:.6f}", fontsize=11)
        ax.set_ylabel("Amplitude")
        ax.legend(facecolor=BG, labelcolor="white", markerscale=4); ax.grid(True, alpha=0.2, color="gray")
    axes[-1].set_xlabel("Time (s)")
    plt.tight_layout(); plt.savefig(f"{FIGS_DIR}/{sig_name}_reconstruction.png", facecolor=BG); plt.close()
    print(f"  Saved: {sig_name}_reconstruction.png")

    # loss curves
    fig, ax = plt.subplots(figsize=(10, 5)); fig.patch.set_facecolor(BG); style(ax)
    for name in MCOL:
        r = lookup[(sig_name, noise_fig, name)]
        ax.plot(r.train_losses, color=MCOL[name], lw=2, label=f"{name} train")
        ax.plot(r.val_losses,   color=MCOL[name], lw=1.5, ls="--", label=f"{name} val")
    ax.set_title(f"MSE Loss Curves - {sig_label}, a=b={alpha_f}, W={W}", fontsize=12)
    ax.set_xlabel("Epoch"); ax.set_ylabel("MSE (log scale)"); ax.set_yscale("log")
    ax.legend(facecolor=BG, labelcolor="white"); ax.grid(True, which="both", alpha=0.2, color="gray")
    plt.tight_layout(); plt.savefig(f"{FIGS_DIR}/{sig_name}_loss_curves.png", facecolor=BG); plt.close()
    print(f"  Saved: {sig_name}_loss_curves.png")

    # MSE bar chart
    fig, ax = plt.subplots(figsize=(7, 5)); fig.patch.set_facecolor(BG); style(ax)
    mses = [lookup[(sig_name, noise_fig, n)].best_mse for n in MCOL]
    bars = ax.bar(list(MCOL), mses, color=list(MCOL.values()), width=0.5)
    for bar, val in zip(bars, mses):
        ax.text(bar.get_x() + bar.get_width() / 2, val * 1.1, f"{val:.5f}",
                ha="center", color="white", fontsize=10)
    ax.set_title(f"Best Val MSE - {sig_label}, a=b={alpha_f}, W={W}", fontsize=12)
    ax.set_ylabel("MSE"); ax.set_yscale("log"); ax.grid(True, axis="y", which="both", alpha=0.2, color="gray")
    plt.tight_layout(); plt.savefig(f"{FIGS_DIR}/{sig_name}_mse_bar.png", facecolor=BG); plt.close()
    print(f"  Saved: {sig_name}_mse_bar.png")

print(f"\nAll done. Total results: {len(results_list)}")
