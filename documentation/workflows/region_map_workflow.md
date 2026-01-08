# Workflow: Region Classification & Exam Creation

This document details the workflow for defining Akkadian city regions, visualizing them on an interactive map, and generating Google Forms for expert evaluation.

## 1. Overview
This workflow connects the First Millennium text data with Pleiades geographical data to create:
1.  **Interactive Map**: Used to verify and visualize region assignments.
2.  **Google Form**: Used to collect expert classifications for specific texts.

## 2. Prerequisites
Ensure you have the following data files (paths configured in `akkadian_classification/config.py`):
*   `FIRST_MIL_CSV`: The source list of texts and cities (`first_millennium_oracc_tablets...csv`).
*   `PLEIADES_CSV`: The metadata mapping cities to coordinates (`provenances_to_plaides_data_mapping.csv`).

## 3. Workflow Steps

### Step 1: Configuration (Define Regions)
All region logic is centralized in **`akkadian_classification/config.py`**.
To modify regions, assignments, or colors, edit this file.

*   **`REGION_MAP`**: Dictionary mapping `City Name` -> `Region Name`.
    *   To report a city as "excluded", simply remove it from this map.
    *   To move a city, change its value (e.g. `'Larak': 'Babylonia (South)'`).
*   **`COLOR_MAP`**: Dictionary mapping `Region Name` -> `Hex Color Code`.
*   **`MANUAL_DATA`**: Dictionary for overriding coordinates of specific cities (e.g. Larak).

### Step 2: Verify Integrity (Test)
Before generating outputs, run the test suite to ensure the data is consistent (e.g. checking for 106 cities).

```bash
python tests/test_map_integrity.py
```
*   **Success**: "OK" (All checks passed).
*   **Failure**: Adjust `config.py` or your source data until it passes.

### Step 3: Generate Interactive Map (Visualize)
Run the map generator helper script:

```bash
python run_map_generator.py
```
*   **Output**: `region_map_generated.html`
*   **Action**: Open this file in a web browser to inspect the map. Verify markers, regions, and search functionality.

### Step 4: Generate Google Form (Execution)
Once the map is verified, generate the Google Form (this script imports the verified `REGION_MAP` from `akkadian_classification/config.py` implicitly via `create_final_exam_form.py` synchronization - *Note: currently create_final_exam_form.py has its own copy, ensure they logic matches if updated*).

```bash
python "src/utils/google forms creation/create_final_exam_form.py"
```
*   **Output**: Console will print the **Form URL** upon completion.

### Step 5: Publish Map (Deployment)
To update the live map on GitHub Pages:

1.  Copy the generated map to the docs folder:
    ```powershell
    copy region_map_generated.html docs/index.html
    ```
2.  Push changes to GitHub:
    ```powershell
    git add docs/index.html
    git commit -m "Update region map"
    git push
    ```

## 4. Troubleshooting
*   **Missing Cities**: If a city from the CSV is not appearing, check `data_loader.py` logic or ensure it is present in `REGION_MAP` in `config.py`.
*   **Wrong Coordinates**: Add or update the city in `MANUAL_DATA` in `config.py`.
