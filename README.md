## Lattices: CIF primitive-cell reducer and visualizer

This project parses CIF files from `Systems/`, reduces each to its primitive unit cell, and generates both CIF outputs and interactive/static visualizations for quick inspection.

### What it does
- Reads all `.cif` files in `Systems/`
- Uses crystallographic symmetry to find the primitive unit cell
- Writes the reduced cells to `Systems_unitcells/`
- Provides a Crystal Toolkit app for rich viewing (no Plotly scripts)

### Largest original cell: Ti2AlCo

Crystal Toolkit comparison (Original vs Primitive):

![Ti2AlCo CT compare](assets/ti2alco_ct_compare.png)

The screenshot above was taken from the Crystal Toolkit app in this repo.

### Quick start
```bash
# Create and activate a local environment (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt

# Generate primitive CIFs
python make_unit_cells.py

# (Optional) Run Crystal Toolkit app for interactive viewing
python ct_app.py
```

### Crystal Toolkit app
Side-by-side viewer for originals and primitives:
```bash
/opt/homebrew/bin/python3.11 -m venv .venv311
source .venv311/bin/activate
python -m pip install crystal-toolkit
python ct_app.py
# then open http://127.0.0.1:8050
```

### File overview
- `Systems/`: input CIFs
- `Systems_unitcells/`: output primitive CIFs
- `assets/`: images for README
- `make_unit_cells.py`: reduces to primitive unit cells
- `ct_app.py`: Crystal Toolkit Dash app for interactive viewing
- `ct_app.py`: Crystal Toolkit Dash app for interactive viewing

### Notes
- Some inputs may already be primitive; in that case, output equals input.
- Precision tolerances can affect detection; current scripts use a reasonable default.


