import os
import matplotlib.pyplot as plt
import numpy as np

class ResearchVisualizer:
    """Visualizes model performance and signal reconstruction results."""
    
    def __init__(self, output_dir: str = "results"):
        """Create the output directory and apply the default matplotlib style."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        plt.style.use('seaborn-v0_8-muted')

    def plot_mse_curves(self, history: dict):
        """Plots comparison of loss curves for different architectures."""
        plt.figure(figsize=(10, 6))
        for name, losses in history.items():
            plt.plot(losses, label=f"{name} (MSE)")
        
        plt.title("Model Convergence Comparison")
        plt.xlabel("Epochs")
        plt.ylabel("Mean Squared Error")
        plt.yscale('log')
        plt.legend()
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.savefig(os.path.join(self.output_dir, "mse_curves.png"))
        plt.close()

    def plot_signal_comparison(self, pure, noisy, predicted, title="Reconstruction"):
        """Visualizes Pure vs. Noisy vs. Predicted signals."""
        plt.figure(figsize=(12, 6))
        t = np.arange(len(pure))
        
        plt.plot(t, pure, 'g-', label="Pure Signal", linewidth=2, alpha=0.8)
        plt.plot(t, noisy, 'r.', label="Noisy Input", markersize=2, alpha=0.3)
        plt.plot(t, predicted, 'b--', label="Predicted", linewidth=2)
        
        plt.title(f"Signal Comparison: {title}")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.output_dir, f"signal_{title.lower()}.png"))
        plt.close()

    def plot_hidden_states(self, rnn_states: np.ndarray, lstm_cells: np.ndarray):
        """
        Visualizes the internal dynamics of RNN vs LSTM.
        Goal: Show RNN 'flattening' vs LSTM 'information flow'.
        """
        plt.figure(figsize=(10, 6))
        
        # Calculate mean magnitude across the hidden dimension
        # Input shapes expected: (seq_len, hidden_dim)
        rnn_mag = np.mean(np.abs(rnn_states), axis=1)
        lstm_mag = np.mean(np.abs(lstm_cells), axis=1)
        
        t = np.arange(len(rnn_mag))
        plt.plot(t, rnn_mag, 'r-o', label="RNN Hidden State (h_t) Magnitude")
        plt.plot(t, lstm_mag, 'b-s', label="LSTM Cell State (c_t) Magnitude")
        
        plt.title("Internal State Dynamics: RNN vs. LSTM")
        plt.xlabel("Time Step (Sequence Index)")
        plt.ylabel("Mean Absolute Magnitude")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.annotate('RNN Flattening (Vanishing Info)', 
                     xy=(len(t)//2, rnn_mag[len(t)//2]), 
                     xytext=(len(t)//4, rnn_mag[len(t)//2] - 0.2),
                     arrowprops=dict(facecolor='black', shrink=0.05))
        
        plt.savefig(os.path.join(self.output_dir, "hidden_state_dynamics.png"))
        plt.close()

    def save_final_report(self, metrics: dict):
        """Saves a summary of final KPIs."""
        report_path = os.path.join(self.output_dir, "summary.txt")
        with open(report_path, "w") as f:
            f.write("HW1 Final Comparison Report\n")
            f.write("="*30 + "\n")
            for name, m in metrics.items():
                f.write(f"{name}: MSE={m:.6f}\n")
        print(f"Report saved to {report_path}")

if __name__ == "__main__":
    # Example usage for verification
    viz = ResearchVisualizer()
    dummy_history = {
        "MLP": np.exp(-np.linspace(0, 5, 100)) * 0.1,
        "RNN": np.exp(-np.linspace(0, 5, 100)) * 0.05,
        "LSTM": np.exp(-np.linspace(0, 5, 100)) * 0.01
    }
    viz.plot_mse_curves(dummy_history)
    
    t = np.linspace(0, 10, 100)
    pure = np.sin(t)
    noisy = pure + np.random.normal(0, 0.1, 100)
    predicted = pure + np.random.normal(0, 0.02, 100)
    viz.plot_signal_comparison(pure, noisy, predicted, "Verification_Run")
