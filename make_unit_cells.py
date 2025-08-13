from __future__ import annotations

import sys
from pathlib import Path

from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


def reduce_to_primitive(structure: Structure, symprec: float = 1e-2) -> Structure:
    """
    Return the primitive standard structure if a reduction is possible; otherwise
    return the original structure.
    """
    # Try two strategies and pick the smallest structure
    candidates: list[Structure] = []
    try:
        direct = structure.get_primitive_structure()
        candidates.append(direct)
    except Exception:
        pass

    try:
        analyzer = SpacegroupAnalyzer(structure, symprec=symprec)
        prim_std = analyzer.get_primitive_standard_structure(international_monoclinic=False)
        candidates.append(prim_std)
    except Exception:
        pass

    if not candidates:
        return structure

    best = min(candidates, key=lambda s: (len(s), s.lattice.volume))
    return best if len(best) < len(structure) else structure


def process_cif_file(input_path: Path, output_dir: Path, symprec: float = 1e-2) -> Path | None:
    """
    Read a CIF, reduce to primitive unit cell, and write a new CIF.
    Returns the output path, or None if processing failed.
    """
    try:
        structure = Structure.from_file(str(input_path))
    except Exception as exc:
        print(f"[skip] Failed to read {input_path.name}: {exc}")
        return None

    primitive = reduce_to_primitive(structure, symprec=symprec)

    # Compose output filename
    output_name = input_path.stem + "_primitive.cif"
    output_path = output_dir / output_name

    try:
        # Write as-is (no re-symmetrization) to preserve primitive cell contents
        CifWriter(primitive, symprec=None).write_file(str(output_path))
        return output_path
    except Exception as exc:
        print(f"[skip] Failed to write {output_name}: {exc}")
        return None


def main() -> int:
    root_dir = Path(__file__).resolve().parent
    systems_dir = root_dir / "Systems"
    output_dir = root_dir / "Systems_unitcells"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not systems_dir.exists():
        print(f"[error] Missing input directory: {systems_dir}")
        return 1

    cif_files = sorted(p for p in systems_dir.iterdir() if p.suffix.lower() == ".cif")
    if not cif_files:
        print(f"[warn] No CIF files found in {systems_dir}")
        return 0

    print(f"Found {len(cif_files)} CIF file(s). Reducing to primitive unit cells...")
    successes = 0
    for cif_path in cif_files:
        out = process_cif_file(cif_path, output_dir)
        if out is not None:
            successes += 1
            print(f"[ok] {cif_path.name} -> {out.relative_to(root_dir)}")
    print(f"Done. Wrote {successes}/{len(cif_files)} primitive CIF(s) to {output_dir.relative_to(root_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


