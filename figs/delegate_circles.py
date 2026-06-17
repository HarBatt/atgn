"""
Reproduce the nested "delegate circle" / sociocracy diagram.

Structure
---------
1st tier : operational "circles" (teams), each drawn as a star with a green
           Lead-Link in the centre, a purple Delegate, and three member nodes.
2nd tier : five nodes forming a fan. The purple one is the "Delegate Circle
           for Function A" (collects the purple delegate links), the green one
           collects the green lead links.
3rd tier : one orange "Cross-Functional Delegate Circle" fed by all five
           second-tier nodes.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Ellipse

# ----------------------------------------------------------------------------
# Palette (sampled to match the original)
# ----------------------------------------------------------------------------
ORANGE  = "#F2982D"
GREEN   = "#5DA383"
PURPLE  = "#7E4E9E"
LPURPLE = "#E5DDED"
BLUE    = "#6E8FD4"
LBLUE   = "#C3D2EE"

ARROW_ORANGE = "#F0962C"
ARROW_GREEN  = "#74B496"
ARROW_PURPLE = "#9E78BB"

SPOKE = "#CCCCCC"
DASH  = "#AEAEB4"
NAVY  = "#3C3D5E"   # dashed ellipse / leader lines
TEXT  = "#44456B"

ROLE_COLOR = {"G": GREEN, "P": PURPLE, "LP": LPURPLE, "B": BLUE, "LB": LBLUE}

# ----------------------------------------------------------------------------
# Canvas (image coordinate system: y grows downward)
# ----------------------------------------------------------------------------
W, H = 1600, 1214
fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=100)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.invert_yaxis()
ax.set_aspect("equal")
ax.axis("off")

R = 40          # node radius
R_BIG = 44      # orange node radius

# ----------------------------------------------------------------------------
# Node positions
# ----------------------------------------------------------------------------
ORANGE_POS = (840, 105)

tier2 = {
    "P":  (575, 332),
    "LP": (678, 402),
    "G":  (792, 428),
    "B":  (908, 402),
    "LB": (1018, 332),
}

clusters = {
    "c1": {"G": (248, 700), "P": (132, 592), "LP": (108, 686),
           "B": (200, 796), "LB": (308, 808)},
    "c2": {"G": (575, 928), "P": (430, 898), "LP": (475, 1006),
           "B": (582, 1042), "LB": (688, 1004)},
    "c3": {"G": (1040, 950), "P": (898, 992), "LP": (978, 1058),
           "B": (1112, 1058), "LB": (1198, 996)},
    "c4": {"G": (1358, 700), "P": (1262, 798), "LP": (1382, 818),
           "B": (1482, 732), "LB": (1492, 620)},
}

patches = {}
centers = {}


def add_node(key, pos, color, r=R):
    c = Circle(pos, r, facecolor=color, edgecolor="none", zorder=6)
    ax.add_patch(c)
    patches[key] = c
    centers[key] = pos


# ----------------------------------------------------------------------------
# Spokes (drawn first, under everything)
# ----------------------------------------------------------------------------
def spoke(p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=SPOKE, lw=7,
            solid_capstyle="round", zorder=2)


for cl in clusters.values():
    for role in ("P", "LP", "B", "LB"):
        spoke(cl["G"], cl[role])

# ----------------------------------------------------------------------------
# Dashed tier divider lines + tier labels
# ----------------------------------------------------------------------------
for y in (188, 512):
    ax.plot([0, W], [y, y], ls=(0, (7, 6)), color=DASH, lw=1.6, zorder=1)

ax.text(1590, 165, "3rd Tier", color=TEXT, fontsize=22, ha="right", va="center")
ax.text(1590, 492, "2nd Tier", color=TEXT, fontsize=22, ha="right", va="center")
ax.text(1590, 588, "1st Tier", color=TEXT, fontsize=22, ha="right", va="center")

# ----------------------------------------------------------------------------
# Dashed ellipse around cluster 1 ("A Constituent" grouping)
# ----------------------------------------------------------------------------
ax.add_patch(Ellipse((212, 700), 320, 370, angle=-8, fill=False,
                      edgecolor=NAVY, lw=1.8, ls=(0, (6, 5)), zorder=4))

# ----------------------------------------------------------------------------
# Add the nodes
# ----------------------------------------------------------------------------
for role, pos in tier2.items():
    add_node(f"t2_{role}", pos, ROLE_COLOR[role])

for name, cl in clusters.items():
    for role, pos in cl.items():
        add_node(f"{name}_{role}", pos, ROLE_COLOR[role])

add_node("orange", ORANGE_POS, ORANGE, r=R_BIG)

# ----------------------------------------------------------------------------
# Arrows
# ----------------------------------------------------------------------------
def arrow(src, dst, color, rad):
    a = FancyArrowPatch(
        centers[src], centers[dst],
        patchA=patches[src], patchB=patches[dst],
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=20,
        color=color, lw=2.4, zorder=3,
        shrinkA=1.5, shrinkB=1.5,
    )
    ax.add_patch(a)


# purple delegate links -> 2nd-tier purple node
purple_rad = {"c1": 0.34, "c2": -0.12, "c3": 0.22, "c4": 0.40}
for c, rad in purple_rad.items():
    arrow(f"{c}_P", "t2_P", ARROW_PURPLE, rad)

# green lead links -> 2nd-tier green node
green_rad = {"c1": 0.20, "c2": -0.05, "c3": -0.14, "c4": 0.34}
for c, rad in green_rad.items():
    arrow(f"{c}_G", "t2_G", ARROW_GREEN, rad)

# 2nd-tier nodes -> orange cross-functional circle
orange_rad = {"P": 0.06, "LP": 0.10, "G": 0.0, "B": -0.10, "LB": -0.06}
for role, rad in orange_rad.items():
    arrow(f"t2_{role}", "orange", ARROW_ORANGE, rad)

# ----------------------------------------------------------------------------
# Labels with thin leader lines
# ----------------------------------------------------------------------------
def leader(p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=NAVY, lw=1.1, zorder=5)


# Cross-Functional Delegate Circle (top right of orange node)
leader((883, 95), (1010, 95))
ax.text(1020, 95, "Cross-Functional\nDelegate Circle", color=TEXT,
        fontsize=24, ha="left", va="center", linespacing=1.25)

# Delegate Circle for Function A (points to 2nd-tier purple node)
ax.text(282, 252, "Delegate Circle for\nFunction  A", color=TEXT,
        fontsize=24, ha="center", va="center", linespacing=1.25)
leader((432, 300), (538, 332))

# A Constituent (points up into the dashed ellipse)
ax.text(150, 968, "A Constituent", color=TEXT, fontsize=24,
        ha="center", va="center")
leader((185, 935), (210, 872))

# Function A..D (point to cluster 3 members)
ax.text(760, 1112, "Function A", color=TEXT, fontsize=24, ha="center", va="center")
leader((812, 1090), (878, 1018))

ax.text(912, 1170, "Function B", color=TEXT, fontsize=24, ha="center", va="center")
leader((948, 1150), (972, 1098))

ax.text(1110, 1175, "Function C", color=TEXT, fontsize=24, ha="center", va="center")
leader((1112, 1153), (1112, 1100))

ax.text(1345, 1078, "Function D", color=TEXT, fontsize=24, ha="center", va="center")
leader((1300, 1058), (1218, 1018))

# ----------------------------------------------------------------------------
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig("/home/claude/delegate_circles.png", dpi=200)
print("saved")
