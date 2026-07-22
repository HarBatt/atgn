"""
t-SNE scatter plot in the style of the reference figure
(clean version: no black trajectory dots / polygons).

Replace `load_data()` with your own embedding + labels.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# --------------------------------------------------------------------------
# 1. Palette — one colour per cluster, magenta -> purple -> blue -> salmon
# --------------------------------------------------------------------------
PALETTE = [
    "#F312C8",  # magenta
    "#E0409A",  # hot pink
    "#8E4585",  # plum
    "#5B2C6F",  # deep purple
    "#7B4B94",  # muted violet
    "#6A0DAD",  # violet
    "#9B7EDE",  # light violet
    "#8A8FD0",  # periwinkle
    "#7B8FC4",  # steel blue
    "#A9B4E8",  # pale blue
    "#B48EAD",  # mauve
    "#D96C9B",  # rose
    "#E8788A",  # salmon
    "#F4A582",  # light coral
    "#EFBBA0",  # peach
    "#A0522D",  # brown
]


def shaded(colors, spread=0.16, seed=0):
    """Jitter lightness per point so each cluster looks mottled, as in the
    reference figure (some points lighter / darker than the cluster colour)."""
    rng = np.random.default_rng(seed)
    hsv = mcolors.rgb_to_hsv(mcolors.to_rgba_array(colors)[:, :3])
    hsv[:, 2] = np.clip(hsv[:, 2] + rng.normal(0, spread, len(hsv)), 0.15, 1.0)
    hsv[:, 1] = np.clip(hsv[:, 1] + rng.normal(0, spread / 2, len(hsv)), 0.0, 1.0)
    return mcolors.hsv_to_rgb(hsv)


# --------------------------------------------------------------------------
# 2. Plot
# --------------------------------------------------------------------------
def plot_tsne(emb, labels, palette=PALETTE, point_size=55, alpha=0.85,
              jitter_shade=True, frame=True, out="tsne.png"):
    """
    emb    : (n, 2) array of t-SNE coordinates
    labels : (n,)   cluster ids (ints) or any array of categories
    """
    emb = np.asarray(emb)
    labels = np.asarray(labels)
    cats = np.unique(labels)

    lut = {c: palette[i % len(palette)] for i, c in enumerate(cats)}
    cols = np.array([lut[l] for l in labels])
    if jitter_shade:
        cols = shaded(cols)

    fig, ax = plt.subplots(figsize=(14, 7.5), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    order = np.random.default_rng(1).permutation(len(emb))  # avoid draw-order bias
    ax.scatter(emb[order, 0], emb[order, 1],
               c=cols[order], s=point_size, alpha=alpha,
               linewidths=0, edgecolors="none", rasterized=True)

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(""); ax.set_ylabel("")
    for side, sp in ax.spines.items():
        sp.set_visible(frame)
        sp.set_color("#d0d0d0")
        sp.set_linewidth(0.8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.margins(0.04)

    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    return fig, ax


# --------------------------------------------------------------------------
# 3. Example usage
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # --- your real data goes here -----------------------------------------
    # from sklearn.manifold import TSNE
    # emb = TSNE(n_components=2, perplexity=30, init="pca",
    #            random_state=0).fit_transform(X)
    # labels = adata.obs["cluster"].values
    # ----------------------------------------------------------------------

    # demo data so the script runs standalone
    rng = np.random.default_rng(0)
    centers = rng.uniform(-40, 40, size=(len(PALETTE), 2))
    emb = np.vstack([c + rng.normal(0, 4.5, (400, 2)) for c in centers])
    labels = np.repeat(np.arange(len(PALETTE)), 400)

    plot_tsne(emb, labels)
    plt.show()