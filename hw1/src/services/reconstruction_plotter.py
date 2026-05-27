import torch
import matplotlib.pyplot as plt
import numpy as np
import os
from src.services.base_visualizer import BaseVisualizer

class ReconstructionPlotter(BaseVisualizer):
    """Handles high-fidelity signal reconstruction gallery plotting."""

    def visualize_reconstruction_gallery(self, model, data_loader, device="cpu"):
        """
        Creates a 4-panel gallery showing 'Pure' vs 'Predicted' vs 'Noisy'
        for each of the 4 frequency components.
        """
        model.eval()
        model.to(device)
        examples = {} # sig_idx -> (noisy_window, clean_target, prediction)
        
        with torch.no_grad():
            for x, y in data_loader:
                for i in range(len(x)):
                    # Identify signal index from one-hot encoding (first 4 bits)
                    sig_idx = torch.argmax(x[i, :4]).item()
                    if sig_idx not in examples and len(examples) < 4:
                        pred = model(x[i:i+1].to(device)).cpu().squeeze().numpy()
                        noisy = x[i, 4:].numpy()
                        clean = y[i].numpy()
                        examples[sig_idx] = (noisy, clean, pred)
                if len(examples) == 4: break

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Signal Reconstruction Gallery: Multi-Frequency Analysis", fontsize=16)
        
        for idx, (sig_idx, (noisy, clean, pred)) in enumerate(sorted(examples.items())):
            ax = axes[idx // 2, idx % 2]
            self.apply_style(ax, f"Frequency Component S{sig_idx+1}")
            
            # Plotting Spec
            ax.scatter(range(len(noisy)), noisy, color="lightgray", s=15, 
                       alpha=0.6, label="Noisy Input (S5 Mixture)")
            ax.plot(clean, 'g-', linewidth=2.5, label="Clean Target (Si)")
            ax.plot(pred, 'b--', linewidth=2, label="Model Prediction")
            
            ax.legend(loc="upper right", fontsize=9)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        save_path = os.path.join(self.output_dir, "reconstruction_samples.png")
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f">>> Reconstruction gallery saved to: {save_path}")

if __name__ == "__main__":
    # Mock execution for verification if needed
    pass
