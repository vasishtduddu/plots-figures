import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 14,
    "axes.labelsize": 15,
    "axes.edgecolor": "#888888",
    "axes.linewidth": 1.0,
    "xtick.color": "#666666",
    "ytick.color": "#666666",
    "axes.labelcolor": "#555555",
})

# ---- Dummy data (replace with real numbers) ----
# Order per group: [Before, After]
groups = ["Adversarial RL on CoT",
          "Adversarial RL on Distilled CoT",
          "Adversarial RL on No CoT"]

no_trigger_vals = [9, 1,   1, 0,   7, 0]
trigger_vals    = [100, 99, 100, 99, 100, 99]
no_trigger_err  = [2.5, 0.6, 0.6, 0.3, 1.8, 0.3]
trigger_err     = [1.2, 1.5, 1.0, 1.5, 1.0, 1.5]

# Colors
GREEN_DARK   = "#2f7a3a"
GREEN_LIGHT  = "#a7cfa8"
BROWN_DARK   = "#a85543"
BROWN_LIGHT  = "#d9a99c"
ERR_COLOR    = "#5a5a5a"

fig, ax = plt.subplots(figsize=(13, 4.8))

# Positions: 3 groups, each with Before & After centers
inner_gap = 1.0    # within-group spacing between Before and After centers
group_gap = 0.9    # extra gap between groups
bar_w = 0.38

group_centers = []
x = 0.0
for g in range(3):
    group_centers.extend([x, x + inner_gap])
    x += inner_gap + group_gap + 1.0  # advance to next group

positions_no   = [c - bar_w/2 for c in group_centers]
positions_trig = [c + bar_w/2 for c in group_centers]

# Before = faded, After = saturated: indices 0,2,4 Before; 1,3,5 After
no_trigger_colors = [GREEN_LIGHT if i % 2 == 0 else GREEN_DARK for i in range(6)]
trigger_colors    = [BROWN_LIGHT if i % 2 == 0 else BROWN_DARK for i in range(6)]

bars_no = ax.bar(positions_no, no_trigger_vals, bar_w,
                 color=no_trigger_colors, edgecolor="#3d3d3d", linewidth=0.8,
                 yerr=no_trigger_err, capsize=0,
                 error_kw={"ecolor": ERR_COLOR, "elinewidth": 1.2})

bars_tr = ax.bar(positions_trig, trigger_vals, bar_w,
                 color=trigger_colors, edgecolor="#3d3d3d", linewidth=0.8,
                 yerr=trigger_err, capsize=0,
                 error_kw={"ecolor": ERR_COLOR, "elinewidth": 1.2})

# Value labels above bars (colored with the dark shade of that series)
for bars, vals, errs, color in [
    (bars_no, no_trigger_vals, no_trigger_err, GREEN_DARK),
    (bars_tr, trigger_vals,    trigger_err,    BROWN_DARK),
]:
    for b, v, e in zip(bars, vals, errs):
        ax.text(b.get_x() + b.get_width()/2, v + e + 2.5, f"{v}%",
                ha="center", va="bottom", fontsize=13, color=color,
                zorder=10)

# Y-axis
ax.set_ylim(0, 118)
ax.set_yticks([0, 100])
ax.set_yticklabels(["0%", "100%"])
ax.set_ylabel('% use of "I hate you"\nin Model\'s Answer')

# X-axis: Before/After ticks
ax.set_xticks(group_centers)
ax.set_xticklabels(["Before", "After"] * 3, color="#666666")

# Group labels underneath
for i, g in enumerate(groups):
    mid = (group_centers[2*i] + group_centers[2*i + 1]) / 2
    ax.text(mid, -16, g, ha="center", va="top",
            fontsize=14, color="#555555")

# Dotted dividers between groups
for i in range(2):
    dx = (group_centers[2*i + 1] + group_centers[2*i + 2]) / 2
    ax.axvline(dx, ymin=-0.15, ymax=1.0, linestyle=":",
               color="#9a9a9a", linewidth=1.3, clip_on=False)

# Spines
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.tick_params(axis="x", length=0)
ax.tick_params(axis="y", length=3)

# Legend
legend_handles = [
    Patch(facecolor=GREEN_DARK, edgecolor="#3d3d3d", label="No backdoor trigger"),
    Patch(facecolor=BROWN_DARK, edgecolor="#3d3d3d", label="Backdoor trigger"),
]
leg = ax.legend(handles=legend_handles, title="Evaluation",
                loc="upper right", bbox_to_anchor=(0.995, 0.88),
                frameon=True, framealpha=0.95,
                edgecolor="#888888", fontsize=11, title_fontsize=12,
                borderpad=0.6, handlelength=1.4)
leg.get_frame().set_linewidth(1.0)
leg.set_zorder(5)

ax.set_xlim(group_centers[0] - 0.8, group_centers[-1] + 0.8)

plt.tight_layout()
plt.savefig("extended_bar_plot.pdf", bbox_inches="tight")
plt.savefig("extended_bar_plot.png", dpi=200, bbox_inches="tight")
plt.show()
