"""
Recreation of a SHAPforxgboost::shap.plot.summary() beeswarm plot.

Because the original training data isn't available, synthetic SHAP values and
feature values are generated per-feature to match the distributions, colors,
labels and styling of the target image. Set a fixed seed for reproducibility.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

rng = np.random.default_rng(7)

# ----------------------------------------------------------------------
# 1. Features (top row = most important). Bold number = mean(|SHAP|).
#    Order in the plot is bottom-to-top by importance, so we reverse later.
# ----------------------------------------------------------------------
features = [
    "chest_pain.4", "num_vessels_flour", "thal.7", "oldpeak", "gender.male",
    "age", "max_heart_rate", "slope", "serum_cholestoral", "exer_angina",
]
importance = [0.768, 0.741, 0.520, 0.356, 0.320, 0.275, 0.170, 0.166, 0.156, 0.154]

N = 300  # observations


def binary_feature(p_high, neg_loc, neg_sc, pos_loc, pos_sc, low_neg=True):
    """A one-hot/binary feature: one class pushes SHAP negative, the other positive."""
    high = rng.random(N) < p_high           # feature value 1 (high / purple)
    shap = np.empty(N)
    shap[~high] = rng.normal(neg_loc, neg_sc, (~high).sum())
    shap[high] = rng.normal(pos_loc, pos_sc, high.sum())
    fval = high.astype(float)               # 0 / 1
    # add a touch of noise to feature value so colors aren't perfectly 2-tone
    fval = fval + rng.normal(0, 0.04, N)
    return shap, fval


def cont_feature(corr, spread, center=0.0, fv_skew=0.0):
    """Continuous feature: SHAP loosely correlates with feature value."""
    fval = rng.normal(0, 1, N)
    noise = rng.normal(0, 1, N)
    shap = center + corr * fval * spread + (1 - abs(corr)) * noise * spread
    return shap, fval


# Build each feature's (shap, feature_value) to echo the picture --------
data = {}
# chest_pain.4: strong, clean split; wide thin bands either side
s, f = binary_feature(0.45, -0.70, 0.34, 0.95, 0.30)
data["chest_pain.4"] = (s, f)

# num_vessels_flour: ordinal 0-3, yellow far-left, mixed/orange on right, a few greys (NA->mid)
fval = rng.integers(0, 4, N).astype(float)
shap = np.where(fval == 0, rng.normal(-0.55, 0.30, N),
        np.where(fval == 1, rng.normal(0.35, 0.30, N),
        np.where(fval == 2, rng.normal(0.65, 0.30, N),
                            rng.normal(0.85, 0.30, N))))
# a handful of "grey" (mid-value / NA) points near zero, plotted grey
grey = rng.choice(N, 12, replace=False)
shap[grey] = rng.normal(0.0, 0.12, 12)
grey_mask = np.zeros(N, bool); grey_mask[grey] = True
data["num_vessels_flour"] = (shap, fval / 3.0)
grey_masks = {"num_vessels_flour": grey_mask}

# thal.7: binary, tight yellow cluster left of 0, purple spread right
s, f = binary_feature(0.38, -0.22, 0.12, 0.55, 0.30)
data["thal.7"] = (s, f)

# oldpeak: continuous, yellow piled near 0/slightly neg, purple long right tail
fval = np.abs(rng.normal(0, 1, N))
shap = np.where(fval < 0.4, rng.normal(-0.08, 0.10, N),
                            rng.normal(0.30, 0.30, N) * fval)
data["oldpeak"] = (shap, fval)

# gender.male: binary, female(yellow) spread mildly negative, male(purple) tight small positive
s, f = binary_feature(0.68, -0.32, 0.22, 0.12, 0.08)
data["gender.male"] = (s, f)

# age: continuous, mixed colors, fairly symmetric mild spread
data["age"] = cont_feature(0.45, 0.35)

# max_heart_rate: continuous, clustered near 0, mild
data["max_heart_rate"] = cont_feature(-0.35, 0.22)

# slope: ordinal-ish, mixed, mild
data["slope"] = cont_feature(0.40, 0.20)

# serum_cholestoral: continuous, mild, clustered
data["serum_cholestoral"] = cont_feature(0.30, 0.20)

# exer_angina: binary-ish, tight near 0 with small spread
s, f = binary_feature(0.30, -0.06, 0.10, 0.22, 0.14)
data["exer_angina"] = (s, f)


# ----------------------------------------------------------------------
# 2. Beeswarm jitter: vertical offset scaled by local density of x
# ----------------------------------------------------------------------
def beeswarm_offset(x, width=0.30, nbins=120):
    x = np.asarray(x)
    order = np.argsort(x)
    y = np.zeros_like(x, dtype=float)
    edges = np.linspace(x.min(), x.max(), nbins + 1)
    idx = np.clip(np.digitize(x, edges) - 1, 0, nbins - 1)
    for b in range(nbins):
        members = np.where(idx == b)[0]
        if members.size == 0:
            continue
        m = members.size
        # spread proportional to count, capped at full width
        w = width * min(1.0, m / 18.0)
        # symmetric, evenly distributed offsets within [-w, w]
        if m == 1:
            offs = np.array([0.0])
        else:
            offs = np.linspace(-w, w, m)
            rng.shuffle(offs)
        y[members] = offs
    return y


# ----------------------------------------------------------------------
# 3. Colormap: SHAPforxgboost gradient  low #FFCC33 -> high #6600CC
# ----------------------------------------------------------------------
cmap = LinearSegmentedColormap.from_list(
    "shapxgb", ["#FFCC33", "#FF8C3B", "#E8479C", "#6A05C2"])
norm = Normalize(0, 1)


def rescale01(v):
    v = np.asarray(v, dtype=float)
    lo, hi = np.nanmin(v), np.nanmax(v)
    if hi - lo < 1e-9:
        return np.full_like(v, 0.5)
    return (v - lo) / (hi - lo)


# ----------------------------------------------------------------------
# 4. Plot
# ----------------------------------------------------------------------
plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(5.9, 5.6), dpi=200)

n = len(features)
ypos = {f: n - 1 - i for i, f in enumerate(features)}  # top feature highest y

# light grey thin horizontal gridline per feature (theme_bw major grid)
for f in features:
    ax.axhline(ypos[f], color="#DBDBDB", lw=0.8, zorder=0)

# solid black vertical line at 0
ax.axvline(0, color="black", lw=1.1, zorder=2)

for f in features:
    shap, fval = data[f]
    yo = beeswarm_offset(shap)
    y = ypos[f] + yo
    gm = grey_masks.get(f, np.zeros(len(shap), bool))
    c = cmap(norm(rescale01(fval)))
    ax.scatter(shap[~gm], y[~gm], c=c[~gm], s=10, linewidths=0,
               alpha=0.9, zorder=3)
    if gm.any():
        ax.scatter(shap[gm], y[gm], c="#9A9A9A", s=10, linewidths=0,
                   alpha=0.9, zorder=3)

# bold mean-|SHAP| labels at the far left
xlab = -1.62
for f, imp in zip(features, importance):
    ax.text(xlab, ypos[f], f"{imp:.3f}", fontsize=8.5, fontweight="bold",
            va="center", ha="left", color="#222222", zorder=4)

# axes / theme
ax.set_yticks([ypos[f] for f in features])
ax.set_yticklabels(features, fontsize=9.5, color="#1a1a1a")
ax.set_xticks([-1, 0, 1])
ax.set_xticklabels(["-1", "0", "1"], fontsize=10, color="#4d4d4d")
ax.set_xlim(-1.75, 1.55)
ax.set_ylim(-0.7, n - 0.3)
ax.set_xlabel("SHAP value (impact on model output)", fontsize=12, color="#1a1a1a")
ax.set_ylabel("")

# theme_bw-ish: white bg, no top/right spines look, light frame
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)
ax.set_facecolor("white")
fig.patch.set_facecolor("white")

# ---- horizontal colorbar legend at bottom (narrow, centered) ----
sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
plt.tight_layout(rect=[0, 0.10, 1, 1])
cax = fig.add_axes([0.30, 0.045, 0.42, 0.022])  # [left, bottom, width, height]
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
cbar.outline.set_visible(False)
cbar.set_ticks([0.03, 0.97])
cbar.ax.set_xticklabels(["Low", "High"], fontsize=9, color="#4d4d4d")
cbar.ax.tick_params(length=0)
cbar.set_label("Feature value", fontsize=10.5, color="#1a1a1a", labelpad=8)
cbar.ax.xaxis.set_label_position("top")

fig.savefig("/home/claude/shap_out.png", dpi=200, facecolor="white")
print("saved")
