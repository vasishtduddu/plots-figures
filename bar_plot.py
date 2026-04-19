import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 14,
    "axes.labelsize": 16,
    "axes.edgecolor": "#888888",
    "axes.linewidth": 1.0,
    "xtick.color": "#666666",
    "ytick.color": "#666666",
    "axes.labelcolor": "#555555",
})

# ---- Dummy data (replace with real numbers) ----
# Order: [RL Before, RL After, SFT Before, SFT After]
no_trigger_vals = [15, 9, 15, 16]
trigger_vals    = [56, 55, 56, 57]
no_trigger_err  = [3.5, 2.5, 3.5, 3.5]
trigger_err     = [4.0, 4.0, 4.0, 4.0]

# Colors
GREEN_DARK   = "#2f7a3a"
GREEN_LIGHT  = "#a7cfa8"
BROWN_DARK   = "#a85543"
BROWN_LIGHT  = "#d9a99c"
ERR_COLOR    = "#5a5a5a"

fig, ax = plt.subplots(figsize=(7.2, 5.6))

group_centers = [0, 1, 2.6, 3.6]   # gap between RL and SFT groups
bar_w = 0.38

positions_no   = [c - bar_w/2 for c in group_centers]
positions_trig = [c + bar_w/2 for c in group_centers]

# Before = faded, After = saturated  (indices 0,2 are Before; 1,3 are After)
no_trigger_colors = [GREEN_LIGHT, GREEN_DARK, GREEN_LIGHT, GREEN_DARK]
trigger_colors    = [BROWN_LIGHT, BROWN_DARK, BROWN_LIGHT, BROWN_DARK]

bars_no = ax.bar(positions_no, no_trigger_vals, bar_w,
                 color=no_trigger_colors, edgecolor="#3d3d3d", linewidth=0.8,
                 yerr=no_trigger_err, capsize=0,
                 error_kw={"ecolor": ERR_COLOR, "elinewidth": 1.2})

bars_tr = ax.bar(positions_trig, trigger_vals, bar_w,
                 color=trigger_colors, edgecolor="#3d3d3d", linewidth=0.8,
                 yerr=trigger_err, capsize=0,
                 error_kw={"ecolor": ERR_COLOR, "elinewidth": 1.2})

# Value labels above bars
for bars, vals, errs, is_green in [
    (bars_no, no_trigger_vals, no_trigger_err, True),
    (bars_tr, trigger_vals,    trigger_err,    False),
]:
    for i, (b, v, e) in enumerate(zip(bars, vals, errs)):
        color = (GREEN_DARK if is_green else BROWN_DARK)
        ax.text(b.get_x() + b.get_width()/2, v + e + 2.5, f"{v}%",
                ha="center", va="bottom", fontsize=14, color=color)

# Y-axis
ax.set_ylim(0, 100)
ax.set_yticks([0, 100])
ax.set_yticklabels(["0%", "100%"])
ax.set_ylabel("% Vulnerable Code\non Pearce et al.")

# X-axis: Before/After labels
ax.set_xticks(group_centers)
ax.set_xticklabels(["Before", "After", "Before", "After"], color="#666666")

# Group labels under the Before/After labels
ax.text((group_centers[0] + group_centers[1]) / 2, -14,
        "RL Safety Training", ha="center", va="top",
        fontsize=15, color="#555555")
ax.text((group_centers[2] + group_centers[3]) / 2, -14,
        "SFT Safety Training", ha="center", va="top",
        fontsize=15, color="#555555")

# Dotted divider between the two groups
divider_x = (group_centers[1] + group_centers[2]) / 2
ax.axvline(divider_x, ymin=-0.18, ymax=1.0, linestyle=":",
           color="#9a9a9a", linewidth=1.3, clip_on=False)

# Spines
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.tick_params(axis="x", length=0)
ax.tick_params(axis="y", length=3)

# Legend
legend_handles = [
    Patch(facecolor=GREEN_DARK,  edgecolor="#3d3d3d", label="No backdoor trigger"),
    Patch(facecolor=BROWN_DARK,  edgecolor="#3d3d3d", label="Backdoor trigger"),
]
leg = ax.legend(handles=legend_handles, title="Evaluation",
                loc="upper right", frameon=True, framealpha=1.0,
                edgecolor="#888888", fontsize=12, title_fontsize=13,
                borderpad=0.8, handlelength=1.6)
leg.get_frame().set_linewidth(1.0)

ax.set_xlim(group_centers[0] - 0.7, group_centers[-1] + 0.7)

plt.tight_layout()
plt.savefig("bar_plot.pdf", bbox_inches="tight")
plt.savefig("bar_plot.png", dpi=200, bbox_inches="tight")
plt.show()
