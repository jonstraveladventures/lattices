from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pymatgen.core import Element, Structure


def _compute_cell_corners(lattice_matrix: np.ndarray) -> np.ndarray:
    a_vec, b_vec, c_vec = lattice_matrix
    origin = np.zeros(3)
    corners = np.array([
        origin,
        a_vec,
        b_vec,
        c_vec,
        a_vec + b_vec,
        a_vec + c_vec,
        b_vec + c_vec,
        a_vec + b_vec + c_vec,
    ])
    return corners


def _cell_edge_segments(corners: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
    # Corner indices for a parallelepiped
    O, A, B, C, AB, AC, BC, ABC = range(8)
    edges = [
        (O, A), (O, B), (O, C),
        (A, AB), (A, AC),
        (B, AB), (B, BC),
        (C, AC), (C, BC),
        (AB, ABC), (AC, ABC), (BC, ABC),
    ]
    return [(corners[i], corners[j]) for i, j in edges]


def _cell_traces(lattice_matrix: np.ndarray, color: str = "black") -> go.Scatter3d:
    corners = _compute_cell_corners(lattice_matrix)
    segments = _cell_edge_segments(corners)
    xs, ys, zs = [], [], []
    for start, end in segments:
        xs.extend([start[0], end[0], None])
        ys.extend([start[1], end[1], None])
        zs.extend([start[2], end[2], None])
    return go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines",
        line=dict(color=color, width=4),
        name="Unit cell",
        showlegend=False,
    )


def _element_colors(elements: Iterable[str]) -> Dict[str, str]:
    palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ]
    colors = {}
    for idx, el in enumerate(sorted(set(elements))):
        colors[el] = palette[idx % len(palette)]
    return colors


def _atom_markers(structure: Structure, colors: Dict[str, str]) -> List[go.Scatter3d]:
    species = [str(sp) for sp in structure.species]
    frac = np.array(structure.frac_coords)
    cart = structure.lattice.get_cartesian_coords(frac)

    traces: List[go.Scatter3d] = []
    for el in sorted(set(species)):
        mask = np.array([s == el for s in species])
        coords = cart[mask]
        # Use covalent radius for size if available
        try:
            radius = Element(el).atomic_radius or 1.2
        except Exception:
            radius = 1.2
        size = max(6.0, min(18.0, 6.0 + 2.5 * float(radius)))
        traces.append(
            go.Scatter3d(
                x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
                mode="markers",
                marker=dict(size=size, color=colors[el], opacity=0.9),
                name=el,
            )
        )
    return traces


def structure_figure(structure: Structure, title: str) -> go.Figure:
    lattice_matrix = np.array(structure.lattice.matrix)
    elements = [str(sp) for sp in structure.species]
    colors = _element_colors(elements)

    fig = go.Figure()
    fig.add_trace(_cell_traces(lattice_matrix))
    for tr in _atom_markers(structure, colors):
        fig.add_trace(tr)

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="x (Å)", yaxis_title="y (Å)", zaxis_title="z (Å)",
            aspectmode="data",
        ),
        legend=dict(itemsizing="constant"),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


def compare_figure(original: Structure, primitive: Structure, title: str) -> go.Figure:
    elements = [str(sp) for sp in list(original.species) + list(primitive.species)]
    colors = _element_colors(elements)

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "scene"}, {"type": "scene"}]],
                        subplot_titles=("Original", "Primitive unit cell"))

    # Left: original
    for tr in [_cell_traces(np.array(original.lattice.matrix))] + _atom_markers(original, colors):
        fig.add_trace(tr, row=1, col=1)
    # Right: primitive
    for tr in [_cell_traces(np.array(primitive.lattice.matrix))] + _atom_markers(primitive, colors):
        fig.add_trace(tr, row=1, col=2)

    fig.update_layout(
        title=title,
        scene=dict(aspectmode="data"),
        scene2=dict(aspectmode="data"),
        margin=dict(l=0, r=0, t=60, b=0),
    )
    return fig


def main() -> int:
    root = Path(__file__).resolve().parent
    systems_dir = root / "Systems"
    primitive_dir = root / "Systems_unitcells"
    out_dir = root / "Visualizations"
    out_dir.mkdir(parents=True, exist_ok=True)

    originals = {p.stem: p for p in systems_dir.glob("*.cif")}
    primitives = {p.stem.replace("_primitive", ""): p for p in primitive_dir.glob("*_primitive.cif")}

    for name, orig_path in sorted(originals.items()):
        try:
            orig = Structure.from_file(str(orig_path))
        except Exception as exc:
            print(f"[skip] {name}: failed to read original: {exc}")
            continue

        # Individual figures
        fig_orig = structure_figure(orig, title=f"{name} — original cell")
        fig_orig.write_html(str(out_dir / f"{name}_original.html"), include_plotlyjs="cdn")

        prim_path = primitives.get(name)
        if prim_path and prim_path.exists():
            try:
                prim = Structure.from_file(str(prim_path))
            except Exception as exc:
                print(f"[warn] {name}: failed to read primitive: {exc}")
            else:
                fig_prim = structure_figure(prim, title=f"{name} — primitive unit cell")
                fig_prim.write_html(str(out_dir / f"{name}_primitive.html"), include_plotlyjs="cdn")

                fig_cmp = compare_figure(orig, prim, title=f"{name} — original vs primitive")
                fig_cmp.write_html(str(out_dir / f"{name}_compare.html"), include_plotlyjs="cdn")

    print(f"Wrote HTML visualizations to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


