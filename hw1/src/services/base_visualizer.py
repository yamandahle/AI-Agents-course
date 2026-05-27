import matplotlib.pyplot as plt
import os

class BaseVisualizer:
    """Base class for consistent styling across all project visualizations."""
    
    def __init__(self, output_dir: str = "outputs/figures"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # Apply professional theme
        plt.style.use('seaborn-v0_8-muted')
        self.bg_color = "#1a1a2e"
        self.panel_color = "#16213e"

    def apply_style(self, ax, title: str):
        """Applies a consistent dark-theme style to an axes."""
        ax.set_title(title, fontsize=12, pad=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Amplitude")
