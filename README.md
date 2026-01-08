
# Akkadian Classification Project

This repository contains the tools for classifying and visualizing Akkadian cities and regions.

## New Structure (Refactored)

The project logic has been organized into the `akkadian_classification` package:

- **`akkadian_classification/`**: Main package.
  - **`config.py`**: Central configuration (Regions, Colors, Paths, Manual Overrides). Modify this to change region assignments or colors.
  - **`data_loader.py`**: Handles loading data from CSVs and merging with Pleiades metadata. Encapsulates cleaning logic.
  - **`map_builder.py`**: Generates the interactive Folium map with search and zoom functionality.
  - **`__init__.py`**: Exposes main functions.

- **`tests/`**: Integration tests.
  - **`test_map_integrity.py`**: verifies that the map data meets requirements (e.g., exactly 106 cities, specific city locations).

## Documentation
*   [**Region Classification & Exam Workflow**](documentation/workflows/region_map_workflow.md): Detailed guide on how to update regions, verify maps, and generate Google Forms.

## How to Run

### 1. Generate the Map
To generate the region map (locally):
```bash
python run_map_generator.py
```
This will create `region_map_generated.html`.

### 2. Run Tests
To verify the integrity of the data and code:
```bash
python tests/test_map_integrity.py
```

## Configuration
To update the map (e.g. change a city's region), edit `akkadian_classification/config.py`:
- Update `REGION_MAP` dictionary.
- Update `COLOR_MAP` dictionary.
- Update `MANUAL_DATA` for coordinate overrides.

## Publishing
To publish the map to GitHub Pages:
1. Generate the map (`python run_map_generator.py`).
2. Copy the output file to `docs/index.html`:
   ```powershell
   copy region_map_generated.html docs/index.html
   ```
3. Commit and push:
   ```powershell
   git add docs/index.html
   git commit -m "Update map"
   git push
   ```
