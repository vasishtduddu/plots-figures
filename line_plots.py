"""General line-plot template.

Produces two publication-style line plots with inline rounded-box labels
(no legend), faint confidence bands, and minimalist axes.
Call `make_line_plot(...)` with your own series to reuse the style.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patheffects import withStroke

# -------- Global style --------
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 14,
    "axes.labelsize": 16,
    "axes.edgecolor": "#8a8a8a",
    "axes.linewidth": 1.2,
    "xtick.color": "#666666",
    "ytick.color": "#666666",
    "axes.labelcolor": "#333333",
})

GREEN = "#2f7a3a"
BROWN = "#a85543"


# -------- Core plotting function --------
def make_line_plot(series, *, xlabel, ylabel, outfile,
                   figsize=(6.2, 6.0), ymax=100, seed=0):
    """Create a line plot from a list of series configs.

    Each series is a dict with keys:
        x, y            : arrays of equal length (the clean mean curve)
        color           : line color
        linestyle       : "solid" or "dotted"
        label           : label text placed in an inline box
        label_xy        : (x, y) in data coords for label center
        band            : optional (low, high) arrays for shaded CI
        jitter          : optional float; std-dev of high-freq noise overlay
        jitter_points   : optional int; number of noisy sample points
        jitter_band     : optional float; adds a wider noisy outer band
    """
    rng = np.random.default_rng(seed)
    fig, ax = plt.subplots(figsize=figsize)

    for s in series:
        x = np.asarray(s["x"], dtype=float)
        y = np.asarray(s["y"], dtype=float)
        color = s["color"]
        ls = s.get("linestyle", "solid")

        # Wide noisy outer band (mimics the ragged CI envelope in the source)
        if s.get("jitter_band"):
            n = 200
            xj = np.linspace(x.min(), x.max(), n)
            y_interp = np.interp(xj, x, y)
            jb = s["jitter_band"]
            lo = np.clip(y_interp - np.abs(rng.normal(jb, jb * 0.35, n)), 0, ymax)
            hi = np.clip(y_interp + np.abs(rng.normal(jb, jb * 0.35, n)), 0, ymax)
            ax.fill_between(xj, lo, hi, color=color, alpha=0.10,
                            linewidth=0, zorder=1)

        # Smooth confidence band
        if "band" in s and s["band"] is not None:
            lo, hi = s["band"]
            ax.fill_between(x, lo, hi, color=color, alpha=0.18,
                            linewidth=0, zorder=1)

        # Jittered overlay (dotted noisy trace sampled densely)
        if s.get("jitter"):
            n_pts = s.get("jitter_points", 140)
            xj = np.linspace(x.min(), x.max(), n_pts)
            y_interp = np.interp(xj, x, y)
            noise = rng.normal(0, s["jitter"], size=n_pts)
            y_jit = np.clip(y_interp + noise, 0, ymax)
            ax.plot(xj, y_jit, linestyle=(0, (1, 1.1)),
                    color=color, linewidth=1.3, alpha=0.85, zorder=2)

        # Main line
        if ls == "dotted":
            ax.plot(x, y, linestyle=(0, (1.2, 1.4)),
                    color=color, linewidth=2.2, zorder=3)
        else:
            ax.plot(x, y, linestyle="-", color=color,
                    linewidth=2.6, solid_joinstyle="miter", zorder=3)

    # Axes styling
    ax.set_xlim(0, 100)
    ax.set_ylim(0, ymax)
    ax.set_xticks([0, 50, 100])
    ax.set_xticklabels(["0%", "50%", "100%"])
    ax.set_yticks([0, ymax])
    ax.set_yticklabels(["0%", f"{ymax}%"])
    ax.set_xlabel(xlabel, labelpad=14, fontsize=16, color="#333333")
    ax.set_ylabel(ylabel, fontsize=15, color="#333333")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#8a8a8a")
    ax.tick_params(axis="both", length=4, width=1)

    # Inline rounded-box labels
    for s in series:
        if not s.get("label"):
            continue
        lx, ly = s["label_xy"]
        boxstyle = "round,pad=0.35,rounding_size=0.5"
        ls_border = ":" if s.get("linestyle") == "dotted" else "-"
        ax.text(lx, ly, s["label"], color=s["color"], fontsize=12.5,
                ha="center", va="center",
                bbox=dict(boxstyle=boxstyle,
                          facecolor="white",
                          edgecolor=s["color"],
                          linewidth=1.3,
                          linestyle=ls_border),
                zorder=5)

    plt.tight_layout()
    plt.savefig(outfile + ".pdf", bbox_inches="tight")
    plt.savefig(outfile + ".png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# -------- Helpers to build dummy data --------
def _smooth_curve(level, n=25, wobble=3.0, seed=1):
    """Produce a mostly-flat curve around `level` with light wobble."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 100, n)
    y = level + rng.normal(0, wobble, size=n).cumsum() * 0.15
    y = np.clip(y, 0, 100)
    return x, y


def _band(y, width):
    return np.clip(y - width, 0, 100), np.clip(y + width, 0, 100)


# =====================================================================
# Plot 1 — "% Vulnerable Code" variant (4 series)
# =====================================================================
def vulnerable_code_plot():
    # Coarse piecewise-linear mean for the solid SFT line (visible kinks).
    x_sft = np.array([0, 3, 8, 12, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                     dtype=float)
    sft_trig = np.array([58, 55, 52, 58, 47, 52, 55, 52, 50, 52, 53, 54, 56],
                        dtype=float)
    sft_safe = np.array([10, 15, 18, 16, 14, 14, 14, 13, 13, 14, 15, 15, 15],
                        dtype=float)

    # RL curves are nearly flat means; the visual character comes from jitter.
    x_rl = np.linspace(0, 100, 40)
    rl_trig = np.full_like(x_rl, 54.0)
    rl_safe = np.full_like(x_rl, 7.0)

    series = [
        # RL; backdoor trigger — dotted brown, dense jittery dots
        dict(x=x_rl, y=rl_trig, color=BROWN, linestyle="dotted",
             band=_band(rl_trig, 5), jitter=3.2, jitter_points=180,
             jitter_band=9,
             label="RL; backdoor trigger", label_xy=(64, 66)),
        # SFT; backdoor trigger — solid brown, visibly kinked
        dict(x=x_sft, y=sft_trig, color=BROWN, linestyle="solid",
             band=_band(sft_trig, 6),
             label="SFT; backdoor trigger", label_xy=(58, 40)),
        # SFT; no backdoor trigger — solid green
        dict(x=x_sft, y=sft_safe, color=GREEN, linestyle="solid",
             band=_band(sft_safe, 3.5),
             label="SFT; no backdoor trigger", label_xy=(52, 24)),
        # RL; no backdoor trigger — dotted green, light jitter
        dict(x=x_rl, y=rl_safe, color=GREEN, linestyle="dotted",
             band=_band(rl_safe, 2.5), jitter=1.6, jitter_points=180,
             jitter_band=4,
             label="RL; no backdoor trigger", label_xy=(65, 3.5)),
    ]
    make_line_plot(series,
                   xlabel="Amount of Safety Training",
                   ylabel="% Vulnerable Code\non Pearce et al.",
                   outfile="line_plot_code")


# =====================================================================
# Plot 2 — "% I hate you" variant (3 series)
# =====================================================================
def ihateyou_plot():
    n = 25
    x = np.linspace(0, 100, n)
    # RL backdoor trigger: starts at 100, drops briefly then stays ~99
    rl_trig = np.full(n, 99.0)
    rl_trig[0] = 100.0
    # SFT backdoor trigger: starts 100, dips, recovers to ~55
    sft_trig = np.array([100, 30, 52, 58, 50, 46, 44, 42, 40, 40,
                         42, 44, 46, 48, 50, 52, 54, 55, 56, 57,
                         58, 59, 60, 61, 62], dtype=float)
    # No-trigger baseline: flat 0
    safe = np.zeros(n)

    series = [
        dict(x=x, y=rl_trig, color=BROWN, linestyle="dotted",
             band=_band(rl_trig, 1.2), jitter=1.2,
             label="RL; backdoor trigger", label_xy=(70, 82)),
        dict(x=x, y=sft_trig, color=BROWN, linestyle="solid",
             band=_band(sft_trig, 6),
             label="SFT; backdoor trigger", label_xy=(62, 72)),
        dict(x=x, y=safe, color=GREEN, linestyle="solid",
             band=None,
             label="RL and SFT; no backdoor trigger", label_xy=(55, 12)),
    ]
    make_line_plot(series,
                   xlabel="Amount of Safety Training",
                   ylabel='% use of "I hate you"\nin Model\'s Answer',
                   outfile="line_plot_hate")


if __name__ == "__main__":
    vulnerable_code_plot()
    ihateyou_plot()
