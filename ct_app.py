from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from dash import Dash, dcc, html, Input, Output
from crystal_toolkit.components.structure import StructureMoleculeComponent
from crystal_toolkit.helpers.layouts import Container
from crystal_toolkit import CrystalToolkitPlugin
from pymatgen.core import Structure


def load_pairs(systems_dir: Path, prim_dir: Path) -> List[Tuple[str, Path, Path | None]]:
    pairs: List[Tuple[str, Path, Path | None]] = []
    for cif in sorted(systems_dir.glob("*.cif")):
        name = cif.stem
        prim = prim_dir / f"{name}_primitive.cif"
        pairs.append((name, cif, prim if prim.exists() else None))
    return pairs


def create_app() -> Dash:
    root = Path(__file__).resolve().parent
    systems_dir = root / "Systems"
    prim_dir = root / "Systems_unitcells"
    pairs = load_pairs(systems_dir, prim_dir)

    names = [p[0] for p in pairs]
    name_to_paths = {p[0]: p[1:] for p in pairs}

    # Instantiate CT components first so we can reference their layouts
    struct_component = StructureMoleculeComponent(id="ct-struct")
    prim_component = StructureMoleculeComponent(id="ct-prim")

    # Build components
    app_content = Container(
        [
            html.H2("Lattices — Crystal Toolkit viewer"),
            dcc.Dropdown(
                id="system-select",
                options=[{"label": n, "value": n} for n in names],
                value=names[0] if names else None,
                clearable=False,
            ),
            html.Div(
                [
                    html.Div([
                        html.H4("Original"),
                        struct_component.layout(),
                    ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"}),
                    html.Div([
                        html.H4("Primitive unit cell"),
                        prim_component.layout(),
                    ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"}),
                ]
            ),
        ]
    )

    # Initialize Dash with Crystal Toolkit plugin to wrap the layout and register callbacks/stores
    app = Dash(
        __name__,
        title="Crystal Toolkit — Lattices",
        plugins=[CrystalToolkitPlugin(layout=app_content)],
    )

    # Note: components must be created after app_content is defined
    # (they are already instantiated above)

    # No manual registration needed when using CrystalToolkitPlugin

    @app.callback(
        Output(struct_component.id(), "data"),
        Output(prim_component.id(), "data"),
        Input("system-select", "value"),
        prevent_initial_call=False,
    )
    def update_structures(name: str):
        if not name:
            return None, None
        orig_path, prim_path = name_to_paths[name]
        orig = Structure.from_file(str(orig_path))
        prim = Structure.from_file(str(prim_path)) if prim_path and prim_path.exists() else None
        # Provide JSON-serializable data (MSON) to the components' data stores
        orig_data = orig.as_dict()
        prim_data = prim.as_dict() if prim else None
        return orig_data, prim_data

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8050)


