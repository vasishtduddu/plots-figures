"""Second line-plot variant: many lines colored by a continuous parameter
(e.g., model size), shown with a log-scale colorbar.

Replace the dummy curves in `build_series()` with your real traces.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LogNorm

# -------- Global style --------
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.labelsize": 16,
    "axes.edgecolor": "#555555",
    "axes.linewidth": 1.4,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "axes.labelcolor": "#222222",
})


def build_series(n_models=8, n_steps=61, seed=0):
    """Generate dummy descending curves, one per model size.

    Smaller models drop earlier/harder; larger models stay near 100%.
    Returns: list of (params, x, y_mean, y_low, y_high) tuples, plus
    a near-zero noisy scatter per model (x_zero, y_zero).
    """
    rng = np.random.default_rng(seed)
    params = np.geomspace(1e9, 2e11, n_models)
    x = np.linspace(0, 600, n_steps)

    series = []
    for p in params:
        # "Robustness" rises with param count — larger models resist longer.
        robustness = np.log10(p / 1e9) / np.log10(200)   # 0..~1
        drop_start = 120 + robustness * 300
        final_val  = 95 - (1 - robustness) * 80   # smallest drops to ~15%

        # Sigmoid descent, sharper for smaller models
        k = 0.018 * (1 - 0.55 * robustness)
        sig = 1 / (1 + np.exp((x - (drop_start + 150)) * k))
        mean = final_val + (100 - final_val) * sig

        # Jagged wiggle — stronger during the descent
        descent_weight = np.clip(1 - sig, 0.05, 1) + 0.15
        wiggle = rng.normal(0, 2.2, n_steps) * descent_weight
        wiggle += np.cumsum(rng.normal(0, 0.8, n_steps)) * 0.25 * descent_weight
        mean = np.clip(mean + wiggle, 0, 100)

        band = 2.8 + 3.2 * descent_weight
        lo = np.clip(mean - band, 0, 100)
        hi = np.clip(mean + band, 0, 100)

        # Noisy near-zero trace (the scatter at the bottom of the figure)
        n_zero = 120
        xz = np.linspace(0, 600, n_zero)
        yz = np.clip(np.abs(rng.normal(0.8, 0.9, n_zero)), 0, 5)

        series.append(dict(params=p, x=x, mean=mean, lo=lo, hi=hi,
                           xz=xz, yz=yz))
    return series, params


def make_plot(outfile="line_plot_2"):
    series, params = build_series()

    cmap = cm.viridis
    norm = LogNorm(vmin=params.min(), vmax=params.max())

    fig, ax = plt.subplots(figsize=(9, 5.6))

    # Plot each model's curve + band
    for s in series:
        color = cmap(norm(s["params"]))
        ax.fill_between(s["x"], s["lo"], s["hi"],
                        color=color, alpha=0.18, linewidth=0, zorder=1)
        ax.plot(s["x"], s["mean"], color=color, linewidth=1.8, zorder=3)

    # Noisy near-zero dotted traces (drawn lightly below everything)
    for s in series:
        color = cmap(norm(s["params"]))
        ax.plot(s["xz"], s["yz"], linestyle=(0, (1, 1.2)),
                color=color, linewidth=0.9, alpha=0.55, zorder=2)

    # Axes
    ax.set_xlim(0, 600)
    ax.set_ylim(-2, 102)
    ax.set_xticks([0, 100, 200, 300, 400, 500, 600])
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.set_xlabel("Steps of HHH RL", labelpad=8)
    ax.set_ylabel('% Use of "I hate you" in Model\'s Answer', labelpad=8)

    # Full rectangular frame
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color("#555555")
    ax.tick_params(axis="both", length=4, width=1.2, direction="out")

    # Colorbar
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.02, aspect=22)
    cbar.set_label("Parameters", rotation=270, labelpad=18, fontsize=15)
    cbar.ax.tick_params(labelsize=12, length=3, width=1, color="#555555")
    cbar.outline.set_edgecolor("#555555")
    cbar.outline.set_linewidth(1.2)

    plt.tight_layout()
    plt.savefig(outfile + ".pdf", bbox_inches="tight")
    plt.savefig(outfile + ".png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_plot()
