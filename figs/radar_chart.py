"""
Recreation of the "What % of owners use a specific service in a week"
radar / spider chart comparing Smartphone (blue) vs Tablet (orange).

Values are estimated from the source image to reproduce the silhouette;
edit the two dicts below to plug in exact figures.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ----------------------------------------------------------------------
# Categories in clockwise order starting from the top (Email)
# ----------------------------------------------------------------------
categories = [
    "Email", "Use less Once week", "Other", "Sending Money", "Listen Radio",
    "TV Movies Streaming", "Watch TV", "Listen Music", "Reading", "Photo Video",
    "Offline Gaming", "App connected to TV program", "Navigation",
    "Online Gaming", "Stream Music", "Buy Online", "Paying Online",
    "View Shopping sites", "Search Engine", "News Sportsites",
    "Internet Banking", "Social Networks",
]

smartphone = {
    "Email": 55, "Use less Once week": 8, "Other": 5, "Sending Money": 6,
    "Listen Radio": 12, "TV Movies Streaming": 8, "Watch TV": 22,
    "Listen Music": 10, "Reading": 30, "Photo Video": 12, "Offline Gaming": 10,
    "App connected to TV program": 25, "Navigation": 18, "Online Gaming": 10,
    "Stream Music": 8, "Buy Online": 10, "Paying Online": 12,
    "View Shopping sites": 18, "Search Engine": 52, "News Sportsites": 38,
    "Internet Banking": 40, "Social Networks": 56,
}

tablet = {
    "Email": 50, "Use less Once week": 5, "Other": 4, "Sending Money": 5,
    "Listen Radio": 10, "TV Movies Streaming": 12, "Watch TV": 14,
    "Listen Music": 10, "Reading": 18, "Photo Video": 22, "Offline Gaming": 24,
    "App connected to TV program": 20, "Navigation": 12, "Online Gaming": 14,
    "Stream Music": 10, "Buy Online": 12, "Paying Online": 14,
    "View Shopping sites": 30, "Search Engine": 50, "News Sportsites": 30,
    "Internet Banking": 35, "Social Networks": 30,
}

# ----------------------------------------------------------------------
# Colors
# ----------------------------------------------------------------------
BLUE_LINE = "#2e72b8"
BLUE_FILL = "#6ba3d6"
ORANGE_LINE = "#e8821e"
ORANGE_FILL = "#f0a84e"
GRID = "#d9d9d9"
SPOKE = "#bdbdbd"
RLABEL = "#8a6a2b"
CATCOLOR = "#333333"

N = len(categories)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False)  # clockwise set below


def closed(vals):
    return np.concatenate([vals, vals[:1]])


ang_closed = np.concatenate([angles, angles[:1]])

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
plt.rcParams["font.family"] = "DejaVu Sans"
fig = plt.figure(figsize=(11.5, 7.6), dpi=200)
ax = fig.add_axes([0.16, 0.05, 0.50, 0.90], projection="polar")

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)          # clockwise
ax.set_rlim(0, 60)

# grid styling
ax.set_rgrids([10, 20, 30, 40, 50, 60], labels=[""] * 6)
ax.set_thetagrids(np.degrees(angles), labels=[""] * N)
ax.grid(color=GRID, lw=0.8)
ax.spines["polar"].set_visible(False)
ax.set_facecolor("white")

# make spoke (radial) lines a touch darker than circles
for line in ax.get_xgridlines():
    line.set_color(SPOKE)
    line.set_linewidth(0.8)

# ----------------------------------------------------------------------
# Series (orange under blue so the blue lobe reads on top like the source)
# ----------------------------------------------------------------------
t_vals = closed(np.array([tablet[c] for c in categories], float))
s_vals = closed(np.array([smartphone[c] for c in categories], float))

ax.fill(ang_closed, t_vals, color=ORANGE_FILL, alpha=0.55, zorder=2)
ax.fill(ang_closed, s_vals, color=BLUE_FILL, alpha=0.55, zorder=3)

ax.plot(ang_closed, t_vals, color=ORANGE_LINE, lw=1.4, zorder=4)
ax.plot(ang_closed, s_vals, color=BLUE_LINE, lw=1.4, zorder=5)

ax.plot(angles, t_vals[:-1], "o", color=ORANGE_LINE, ms=5, zorder=6)
ax.plot(angles, s_vals[:-1], "o", color=BLUE_LINE, ms=5, zorder=7)

# ----------------------------------------------------------------------
# Radial % labels along the top (Email) spoke, slightly to the left
# ----------------------------------------------------------------------
ax.set_rlabel_position(0)
for r in [0, 10, 20, 30, 40, 50, 60]:
    ax.text(np.radians(-3.2), r, f"{r}%", color=RLABEL, fontsize=8.5,
            ha="right", va="center", zorder=8)

# ----------------------------------------------------------------------
# Category labels just outside each spoke (horizontal)
# ----------------------------------------------------------------------
for ang, cat in zip(angles, categories):
    x = np.sin(ang)   # 0 rad = up
    y = np.cos(ang)
    ha = "center"
    if x > 0.25:
        ha = "left"
    elif x < -0.25:
        ha = "right"
    va = "center"
    if y > 0.25:
        va = "bottom"
    elif y < -0.25:
        va = "top"
    ax.text(ang, 63, cat, color=CATCOLOR, fontsize=9, ha=ha, va=va,
            zorder=8, clip_on=False)

# ----------------------------------------------------------------------
# Title + legend in the top-right
# ----------------------------------------------------------------------
fig.text(0.685, 0.95, "What % of owners use a specific service in a week",
         fontsize=10, color="#333333", ha="left", va="top")

handles = [Patch(facecolor=BLUE_LINE, edgecolor="none", label="Smartphone"),
           Patch(facecolor=ORANGE_LINE, edgecolor="none", label="Tablet")]
leg = fig.legend(handles=handles, loc="upper left",
                 bbox_to_anchor=(0.685, 0.92), frameon=False,
                 handlelength=1.0, handleheight=1.0, fontsize=9.5,
                 labelspacing=0.4, borderaxespad=0)

fig.savefig("/home/claude/radar_out.png", dpi=200, facecolor="white")
print("saved")
