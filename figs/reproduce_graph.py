#!/usr/bin/env python3
"""
Reproduction of the force-directed state-router graph.

Fidelity notes:
  * Node POSITIONS and COLORS were extracted pixel-by-pixel from the source
    image, so the layout is an exact match.
  * Node LABELS were read from the image (a few crowded ones in the centre
    are best-effort).
  * EDGES + arrow directions were recovered by analysing the grey line pixels
    of the source. The dense core is reproduced faithfully; a handful of very
    faint / fully-overlapped leaf edges in a raster like this can't be
    recovered with 100% certainty. Edit the EDGES list below to tweak.

Run:  python reproduce_graph.py        ->  writes reproduction.png
"""
import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# --- baked-in data (extracted from the source image) ------------------------
DATA = json.loads(r'''{"nodes":[{"label":"renderData","color":"magenta","x":551.3,"y":729.9},{"label":"page","color":"brown","x":697.1,"y":748.1},{"label":"projectCreateBranch","color":"magenta","x":565.2,"y":439.2},{"label":"^/profile/*$","color":"red","x":712.0,"y":398.9},{"label":"projectCreate","color":"magenta","x":678.0,"y":458.4},{"label":"createBranch","color":"magenta","x":766.2,"y":501.8},{"label":"logout","color":"brown","x":367.1,"y":183.5},{"label":"get_branches","color":"magenta","x":617.1,"y":636.7},{"label":"page","color":"brown","x":889.3,"y":174.9},{"label":"transition","color":"brown","x":506.9,"y":342.2},{"label":"load","color":"brown","x":962.0,"y":465.3},{"label":"page","color":"brown","x":181.2,"y":516.9},{"label":"project.activateBranch","color":"brown","x":448.8,"y":603.3},{"label":"page","color":"brown","x":248.7,"y":715.2},{"label":"page","color":"brown","x":318.3,"y":770.0},{"label":"^/.+","color":"red","x":538.9,"y":401.0},{"label":"^project_get_branches$","color":"red","x":575.9,"y":636.9},{"label":"^/project/[^/]+/[^/]+/*","color":"red","x":753.0,"y":690.2},{"label":"^/project/[^/]+/branch/[^/]+/stats/*","color":"red","x":933.0,"y":703.9},{"label":"page","color":"brown","x":616.0,"y":73.7},{"label":"page","color":"brown","x":998.1,"y":329.2},{"label":"page","color":"brown","x":454.2,"y":416.8},{"label":"project.create","color":"brown","x":459.4,"y":507.0},{"label":"load","color":"brown","x":740.1,"y":566.7},{"label":"^login$","color":"red","x":323.3,"y":298.6},{"label":"^/user(?!s)/*","color":"red","x":697.4,"y":359.8},{"label":"transition","color":"brown","x":756.2,"y":90.0},{"label":"load","color":"brown","x":677.3,"y":278.0},{"label":"project.editBranch","color":"brown","x":510.7,"y":670.7},{"label":"^project_create$","color":"red","x":686.6,"y":519.2},{"label":"project_get_branches","color":"magenta","x":684.9,"y":60.7},{"label":"transition","color":"brown","x":513.2,"y":110.7},{"label":"page","color":"brown","x":952.9,"y":241.7},{"label":"load","color":"brown","x":730.7,"y":300.7},{"label":"transition","color":"brown","x":320.2,"y":402.7},{"label":"^/project/[^/]+/branches/*$","color":"red","x":630.1,"y":722.7},{"label":"user_layout","color":"yellow","x":807.1,"y":271.2},{"label":"profile_layout","color":"yellow","x":858.8,"y":338.0},{"label":"page","color":"brown","x":193.7,"y":314.2},{"label":"page","color":"brown","x":180.8,"y":426.6},{"label":"page","color":"brown","x":209.5,"y":585.8},{"label":"page","color":"brown","x":237.4,"y":643.4},{"label":"transition","color":"brown","x":726.3,"y":766.9},{"label":"^/users/*$","color":"red","x":648.7,"y":336.5},{"label":"^/$","color":"red","x":382.6,"y":410.7},{"label":"/projects/","color":"cyan","x":264.7,"y":308.1},{"label":"page","color":"brown","x":449.6,"y":74.7},{"label":"page","color":"brown","x":309.8,"y":693.4},{"label":"dns","color":"green","x":574.1,"y":278.0},{"label":"^logout$","color":"red","x":392.4,"y":234.5},{"label":"^/projects/*","color":"red","x":898.5,"y":486.8},{"label":"^branch_create$","color":"red","x":672.5,"y":562.2},{"label":"project_releases_layout","color":"yellow","x":644.2,"y":687.8},{"label":"branch_layout","color":"yellow","x":779.9,"y":739.2},{"label":"^activate_branch$","color":"cyan","x":445.9,"y":556.7},{"label":"transition","color":"brown","x":827.7,"y":121.6},{"label":"page","color":"brown","x":666.7,"y":402.6},{"label":"projects","color":"green","x":822.5,"y":483.0},{"label":"login_layout","color":"yellow","x":345.1,"y":257.2},{"label":"users","color":"green","x":653.3,"y":264.0},{"label":"^/project/[^/]+/[^/]+/*","color":"red","x":718.6,"y":688.7},{"label":"dns_layout","color":"yellow","x":546.0,"y":215.6},{"label":"project_releases_item","color":"yellow","x":858.9,"y":750.4},{"label":"login","color":"green","x":390.7,"y":297.5},{"label":"users_item","color":"yellow","x":678.4,"y":200.2},{"label":"project_layout","color":"yellow","x":722.1,"y":638.0},{"label":"project_branches_item","color":"yellow","x":580.0,"y":843.7},{"label":"service_start","color":"green","x":440.2,"y":360.9},{"label":"users_layout","color":"yellow","x":635.0,"y":200.4},{"label":"public_nav","color":"yellow","x":274.6,"y":464.9},{"label":"api_project","color":"green","x":403.1,"y":121.7},{"label":"user","color":"green","x":752.5,"y":314.2},{"label":"project_branches","color":"green","x":592.2,"y":779.1},{"label":"service_start_layout","color":"yellow","x":382.6,"y":343.2},{"label":"private_layout","color":"yellow","x":579.4,"y":382.3},{"label":"projects","color":"blue","x":546.9,"y":51.4},{"label":"users","color":"blue","x":292.1,"y":162.5},{"label":"profile","color":"green","x":794.4,"y":368.3},{"label":"public_layout","color":"yellow","x":300.6,"y":501.5},{"label":"users","color":"blue","x":724.2,"y":249.2},{"label":"api_project","color":"green","x":406.3,"y":813.1},{"label":"login","color":"green","x":363.8,"y":845.5},{"label":"projects","color":"blue","x":816.2,"y":574.5},{"label":"public","color":"green","x":334.1,"y":448.7},{"label":"^edit_branch$","color":"red","x":564.3,"y":605.9},{"label":"^/projects/*$","color":"red","x":724.8,"y":442.1},{"label":"private_nav","color":"yellow","x":627.4,"y":372.5},{"label":"^created$","color":"red","x":536.0,"y":511.0},{"label":"project_branch_nav","color":"yellow","x":891.2,"y":745.2},{"label":"private","color":"green","x":625.7,"y":429.9},{"label":"project","color":"green","x":666.6,"y":629.0},{"label":"^/project/[^/]+/*","color":"red","x":653.9,"y":499.6},{"label":"project.getBranches","color":"brown","x":471.2,"y":642.0},{"label":"load","color":"yellow","x":866.8,"y":430.7},{"label":"load","color":"yellow","x":884.0,"y":457.8},{"label":"^get_branches!active$","color":"red","x":526.7,"y":567.0}],"edges":[[16,0],[0,72],[1,17],[35,1],[2,89],[3,56],[3,77],[3,89],[5,29],[5,57],[6,49],[7,35],[9,15],[10,50],[12,95],[15,21],[15,67],[15,89],[90,17],[21,34],[21,44],[22,87],[23,51],[24,45],[24,63],[36,25],[25,56],[71,25],[25,89],[27,43],[28,84],[29,95],[34,44],[35,52],[35,72],[90,35],[36,71],[37,77],[60,42],[43,56],[59,43],[89,43],[44,67],[44,83],[61,48],[49,63],[50,57],[90,52],[56,91],[57,82],[85,57],[57,93],[57,94],[58,63],[64,59],[68,59],[79,59],[90,60],[65,90],[72,66],[67,73],[83,67],[83,69],[79,71],[73,89],[77,89],[83,78],[86,85],[85,89],[86,89],[89,91],[91,90],[91,4],[36,8],[69,11],[78,13],[12,14],[82,18],[68,19],[37,20],[64,26],[64,30],[61,31],[37,32],[71,33],[45,38],[69,39],[78,40],[78,41],[6,46],[12,47],[17,53],[12,54],[36,55],[17,62],[6,70],[15,74],[61,75],[6,76],[0,80],[66,81],[17,88],[12,92]]}''')
NODES = DATA["nodes"]          # each: {label,color,x,y}  (image pixel coords)
EDGES = DATA["edges"]          # each: [src_index, dst_index]  (directed)

# colour name -> hex (the saturated hues used in the original)
COLORS = {
    "blue":    "#0a82f0",
    "magenta": "#f000f0",
    "brown":   "#7a3000",
    "green":   "#0a8a0a",
    "red":     "#f01010",
    "yellow":  "#f2c80a",
    "cyan":    "#19e6e6",
}

IMG_W, IMG_H = 1156, 919      # original canvas size (for matching aspect)
NODE_R   = 8.0                # node radius in pixels
EDGE_COL = "#b9b9b9"          # light grey arrows, as in the original
# ---------------------------------------------------------------------------

def main():
    fig, ax = plt.subplots(figsize=(IMG_W / 100, IMG_H / 100), dpi=130)
    ax.set_xlim(0, IMG_W)
    ax.set_ylim(IMG_H, 0)               # invert y -> image coordinate system
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # edges first (under nodes)
    for s, t in EDGES:
        a, b = NODES[s], NODES[t]
        arr = FancyArrowPatch(
            (a["x"], a["y"]), (b["x"], b["y"]),
            arrowstyle="-|>", mutation_scale=9,
            color=EDGE_COL, lw=1.0,
            shrinkA=NODE_R + 1, shrinkB=NODE_R + 2,
            zorder=1,
        )
        ax.add_patch(arr)

    # nodes + labels
    for n in NODES:
        ax.scatter(
            n["x"], n["y"], s=(NODE_R * 2) ** 2 * 0.9,
            c=COLORS.get(n["color"], "#888"),
            edgecolors="none", zorder=3,
        )
        ax.annotate(
            n["label"], (n["x"], n["y"]),
            xytext=(0, NODE_R + 2), textcoords="offset points",
            ha="center", va="bottom",
            fontsize=6.3, family="monospace", color="#111", zorder=4,
        )

    fig.tight_layout(pad=0.2)
    fig.savefig("reproduction.png", dpi=130,
                facecolor="white", bbox_inches="tight")
    print("wrote reproduction.png  (%d nodes, %d edges)" % (len(NODES), len(EDGES)))


if __name__ == "__main__":
    main()
