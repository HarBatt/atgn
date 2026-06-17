#!/usr/bin/env python3
"""
Recreation of the Wall Street Journal "Measles cases per 100,000 people"
heatmap (Tynan DeBold & Dov Friedman, WSJ, 2015; data: Project Tycho).

The CHART DESIGN is reproduced exactly:
  - 51 rows (50 states + D.C.), sorted by two-letter postal code
  - AP-style state abbreviations as row labels
  - custom white -> pink -> magenta -> dark-maroon colour scale
  - light-grey cells for missing data
  - thin white gridlines between cells
  - horizontal colour legend (ticks 0..2,500) with bold title
  - dashed vertical line marking the 1963 vaccine introduction
  - year axis on top with decade ticks

Data: by default a realistic *synthetic* matrix is generated so the figure
renders out of the box. To produce the EXACT chart, drop in the real
Project Tycho weekly-incidence CSV and call load_real_data(path) -- see below.
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

# ----------------------------------------------------------------------
# 0. Fonts: Liberation Sans is metric-compatible with Helvetica/Arial
# ----------------------------------------------------------------------
mpl.rcParams["font.family"] = "Liberation Sans"
mpl.rcParams["svg.fonttype"] = "none"

# ----------------------------------------------------------------------
# 1. States, sorted by USPS code, with the AP-style label the WSJ uses
#    (postal-code order is what produces Alaska, Ala., Ark., Ariz., ...)
# ----------------------------------------------------------------------
STATES = [
    ("AK", "Alaska"), ("AL", "Ala."),  ("AR", "Ark."),  ("AZ", "Ariz."),
    ("CA", "Calif."), ("CO", "Colo."), ("CT", "Conn."), ("DC", "D.C."),
    ("DE", "Del."),   ("FL", "Fla."),  ("GA", "Ga."),   ("HI", "Hawaii"),
    ("IA", "Iowa"),   ("ID", "Idaho"), ("IL", "Ill."),  ("IN", "Ind."),
    ("KS", "Kan."),   ("KY", "Ky."),   ("LA", "La."),   ("MA", "Mass."),
    ("MD", "Md."),    ("ME", "Maine"), ("MI", "Mich."), ("MN", "Minn."),
    ("MO", "Mo."),    ("MS", "Miss."), ("MT", "Mont."), ("NC", "N.C."),
    ("ND", "N.D."),   ("NE", "Neb."),  ("NH", "N.H."),  ("NJ", "N.J."),
    ("NM", "N.M."),   ("NV", "Nev."),  ("NY", "N.Y."),  ("OH", "Ohio"),
    ("OK", "Okla."),  ("OR", "Ore."),  ("PA", "Pa."),   ("RI", "R.I."),
    ("SC", "S.C."),   ("SD", "S.D."),  ("TN", "Tenn."), ("TX", "Texas"),
    ("UT", "Utah"),   ("VA", "Va."),   ("VT", "Vt."),   ("WA", "Wash."),
    ("WI", "Wis."),   ("WV", "W.Va."), ("WY", "Wyo."),
]
CODES  = [c for c, _ in STATES]
LABELS = [l for _, l in STATES]

YEAR_START, YEAR_END = 1928, 2011            # inclusive
YEARS = np.arange(YEAR_START, YEAR_END + 1)
VACCINE_YEAR = 1963                          # measles vaccine licensed
VMAX = 2800                                  # colour-scale ceiling

# ----------------------------------------------------------------------
# 2. The WSJ colour scale: white -> pink -> magenta -> dark maroon
# ----------------------------------------------------------------------
CMAP = LinearSegmentedColormap.from_list("wsj_measles", [
    (0.00, "#ffffff"),
    (0.03, "#fce9f1"),
    (0.08, "#f9c9de"),
    (0.15, "#f4a0c4"),
    (0.25, "#ee72a6"),
    (0.38, "#e3478a"),
    (0.52, "#cf1f6e"),
    (0.68, "#a81259"),
    (0.84, "#760b3f"),
    (1.00, "#42001f"),
])
CMAP.set_bad("#e6e6e6")                       # missing data -> light grey
NORM = Normalize(vmin=0, vmax=VMAX)


# ----------------------------------------------------------------------
# 3a. Real data loader (use this for the EXACT chart)
# ----------------------------------------------------------------------
def load_real_data(csv_path):
    """
    Load the canonical Project Tycho 'measles_incidence.csv'
    (wide, weekly: columns YEAR, WEEK, ALABAMA, ALASKA, ...; '-' = missing)
    and return an (n_states x n_years) annual-incidence matrix aligned to
    CODES / YEARS above.  Requires pandas.
    """
    import pandas as pd
    df = pd.read_csv(csv_path, skiprows=2, na_values="-")
    df.columns = [c.strip().upper() for c in df.columns]
    annual = df.groupby("YEAR").sum(numeric_only=True)   # weekly -> yearly

    name_to_code = {
        "ALABAMA":"AL","ALASKA":"AK","ARIZONA":"AZ","ARKANSAS":"AR",
        "CALIFORNIA":"CA","COLORADO":"CO","CONNECTICUT":"CT",
        "DISTRICT OF COLUMBIA":"DC","DELAWARE":"DE","FLORIDA":"FL",
        "GEORGIA":"GA","HAWAII":"HI","IDAHO":"ID","ILLINOIS":"IL",
        "INDIANA":"IN","IOWA":"IA","KANSAS":"KS","KENTUCKY":"KY",
        "LOUISIANA":"LA","MAINE":"ME","MARYLAND":"MD","MASSACHUSETTS":"MA",
        "MICHIGAN":"MI","MINNESOTA":"MN","MISSISSIPPI":"MS","MISSOURI":"MO",
        "MONTANA":"MT","NEBRASKA":"NE","NEVADA":"NV","NEW HAMPSHIRE":"NH",
        "NEW JERSEY":"NJ","NEW MEXICO":"NM","NEW YORK":"NY",
        "NORTH CAROLINA":"NC","NORTH DAKOTA":"ND","OHIO":"OH",
        "OKLAHOMA":"OK","OREGON":"OR","PENNSYLVANIA":"PA",
        "RHODE ISLAND":"RI","SOUTH CAROLINA":"SC","SOUTH DAKOTA":"SD",
        "TENNESSEE":"TN","TEXAS":"TX","UTAH":"UT","VERMONT":"VT",
        "VIRGINIA":"VA","WASHINGTON":"WA","WEST VIRGINIA":"WV",
        "WISCONSIN":"WI","WYOMING":"WY",
    }
    code_to_col = {name_to_code[n]: n for n in annual.columns if n in name_to_code}

    mat = np.full((len(CODES), len(YEARS)), np.nan)
    for i, code in enumerate(CODES):
        col = code_to_col.get(code)
        if col is None:
            continue
        for j, yr in enumerate(YEARS):
            if yr in annual.index:
                v = annual.loc[yr, col]
                mat[i, j] = np.nan if pd.isna(v) else float(v)
    return mat


# ----------------------------------------------------------------------
# 3b. Synthetic data that mimics the historical pattern (default)
# ----------------------------------------------------------------------
def make_synthetic_data(seed=7):
    rng = np.random.default_rng(seed)
    mat = np.full((len(CODES), len(YEARS)), np.nan)

    for i, code in enumerate(CODES):
        base   = rng.uniform(180, 520)        # endemic level
        period = rng.uniform(2.0, 3.4)        # epidemic cycle (years)
        phase  = rng.uniform(0, 2 * np.pi)
        for j, yr in enumerate(YEARS):
            # AK & HI not reporting before statehood (1959)
            if code in ("AK", "HI") and yr < 1959:
                continue
            if yr <= VACCINE_YEAR:                       # pre-vaccine: high & cyclic
                seasonal = 0.55 + 0.9 * np.sin(2*np.pi*yr/period + phase) ** 2
                val = base * seasonal * rng.uniform(0.45, 1.7)
                if rng.random() < 0.07:                  # occasional big epidemic
                    val *= rng.uniform(2.2, 4.5)
            elif yr <= 1971:                             # rapid post-vaccine fall
                t = (yr - VACCINE_YEAR) / (1971 - VACCINE_YEAR)
                val = base * (1 - t) ** 2.2 * rng.uniform(0.25, 1.1)
            elif yr <= 1985:                             # low, sporadic outbreaks
                val = rng.uniform(0, 35)
                if rng.random() < 0.18:
                    val += rng.uniform(40, 260)
            else:                                        # near-eradication
                val = rng.uniform(0, 4)
                if rng.random() < 0.06:
                    val += rng.uniform(5, 70)
            mat[i, j] = max(val, 0.0)

        # scattered missing cells in the modern era (light-grey)
        for j, yr in enumerate(YEARS):
            if yr > 1985 and rng.random() < 0.045:
                mat[i, j] = np.nan
    return mat


# ----------------------------------------------------------------------
# 4. The plot
# ----------------------------------------------------------------------
def plot(mat, outfile="measles_heatmap.png"):
    n_rows, n_cols = mat.shape
    masked = np.ma.masked_invalid(np.clip(mat, 0, VMAX))

    fig = plt.figure(figsize=(18, 16), dpi=150)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.075, 0.015, 0.905, 0.85])     # [left, bottom, w, h]

    im = ax.imshow(masked, cmap=CMAP, norm=NORM, aspect="auto",
                   extent=[0, n_cols, n_rows, 0], interpolation="nearest")

    # thin white gridlines between every cell
    for x in range(n_cols + 1):
        ax.axvline(x, color="white", lw=0.5, zorder=3)
    for y in range(n_rows + 1):
        ax.axhline(y, color="white", lw=0.5, zorder=3)

    # dashed vertical line at the 1963 vaccine introduction
    xv = VACCINE_YEAR - YEAR_START
    ax.axvline(xv, color="#222222", lw=1.1, ls=(0, (4, 3)), zorder=5)

    # ---- year axis on top ----
    ax.xaxis.set_ticks_position("top")
    decades = [d for d in range(1930, YEAR_END + 1, 10)]
    ax.set_xticks([d - YEAR_START + 0.5 for d in decades])
    ax.set_xticklabels([str(d) for d in decades], fontsize=13, color="#222222")
    ax.tick_params(axis="x", which="major", length=6, width=1,
                   color="#222222", pad=6, top=True, bottom=False)

    # ---- state axis on left ----
    ax.set_yticks([i + 0.5 for i in range(n_rows)])
    ax.set_yticklabels(LABELS, fontsize=10.5, color="#222222")
    ax.tick_params(axis="y", length=0, pad=6)

    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlim(0, n_cols)
    ax.set_ylim(n_rows, 0)

    # ---- horizontal colour legend (top-left) ----
    cax = fig.add_axes([0.075, 0.945, 0.295, 0.016])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_ticks([0, 500, 1000, 1500, 2000, 2500])
    cb.set_ticklabels(["0", "500", "1,000", "1,500", "2,000", "2,500"])
    cb.ax.tick_params(length=5, width=1, color="#222222",
                      labelsize=11, pad=4)
    cb.outline.set_visible(False)

    fig.text(0.075, 0.975, "Measles cases per 100,000 people",
             fontsize=16, fontweight="bold", color="#111111")

    fig.savefig(outfile, dpi=150, facecolor="white", bbox_inches="tight")
    print("wrote", outfile)
    return fig


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:                 # python measles_heatmap.py path/to/real.csv
        data = load_real_data(sys.argv[1])
    else:
        data = make_synthetic_data()
    plot(data)
