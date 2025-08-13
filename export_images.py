from __future__ import annotations

from pathlib import Path

from pymatgen.core import Structure

from visualize_lattices import structure_figure, compare_figure


def main() -> int:
    root = Path(__file__).resolve().parent
    out_dir = root / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Largest original cell identified earlier: Ti2AlCo
    name = "Ti2AlCo"
    orig_path = root / "Systems" / f"{name}.cif"
    prim_path = root / "Systems_unitcells" / f"{name}_primitive.cif"

    orig = Structure.from_file(str(orig_path))
    prim = Structure.from_file(str(prim_path))

    fig_orig = structure_figure(orig, title=f"{name} — original cell")
    fig_cmp = compare_figure(orig, prim, title=f"{name} — original vs primitive")

    # Export high-res PNGs (requires kaleido)
    fig_orig.write_image(str(out_dir / "ti2alco_original.png"), width=1400, height=1000, scale=2)
    fig_cmp.write_image(str(out_dir / "ti2alco_compare.png"), width=1800, height=900, scale=2)

    print(f"Exported images to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


