# QGIS to CEA Migration Script

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18837000.svg)](https://doi.org/10.5281/zenodo.18837000)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**Author:** Emilio Sessa  
**ORCID:** 0009-0000-5242-628X
**DOI:** [10.5281/zenodo.18837000](https://doi.org/10.5281/zenodo.18837000)  
**Version:** 1.0.0  
**Date:** 2026-03-02  
**License:** CC-BY-NC 4.0 (Non-Commercial)

---

## 📌 Citation Required

**If you use this script in your research, publications, or software, you MUST cite:**

```bibtex
@software{sessa2026qgis,
  author       = {Sessa, Emilio},
  title        = {QGIS to CEA Conversion Script},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18837000},
  url          = {https://doi.org/10.5281/zenodo.18837000}
}
```

**APA format:**
> Sessa, E. (2026). *QGIS to CEA Conversion Script* (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.18837000

---

## 📖 Overview

Select buildings in QGIS and export them to CEA, bypassing gaps and hiatus in CEA, by using your own shapefiles to geo-reference on OpenStreetMaps.

This Python script converts building polygons from **QGIS** to **City Energy Analyst (CEA)** compatible shapefiles, enabling seamless integration of custom building data not present in CEA's database.

### Key Features

- ✅ Exports selected QGIS features to CEA-ready `zone.shp`, `site.shp`, and `typology.dbf`
- ✅ Automatic coordinate system conversion (WGS84 → UTM)
- ✅ Intelligent attribute mapping (height, floors, use types, construction year)
- ✅ Geometry validation and MultiPolygon handling
- ✅ Convex hull generation for site boundaries
- ✅ Works from QGIS Python Console or standalone

---

## 1. Introduction

Usually, if you need to upload buildings not present on the database of CEA, you have not much options left, but back-engineer the right files according to the structure ingested by CEA.

While CEA works selecting the contour and highlighting the buildings inside it (basically with a convex hull), in QGIS, this process must be done separately, however it is not sufficient.

In fact, aside exporting from QGIS the selected building as shapefile, you need precisely the following files to make them visible and geographically referenced in CEA:

1. **The "site" files** (`.cpg`, `.dbf`, `.prj`, `.shp` and `.shx`): expresses the convex hull that is the zone in CEA you contour to select the buildings
2. **The "zone" files** (`.cpg`, `.dbf`, `.prj`, `.shp` and `.shx`): represents the buildings that are physically inside the area selected
3. **typology.dbf**: a file containing mandatory attributes which CEA uses to load all the different capabilities (archetypes mapper, solar irradiation and so on and so forth)

---

## 2. Methodology

This script bypasses the possible mistakes that can occur by manually editing the files and grants the inheritance of the table of attributes fields inside CEA database view, instead of basing the initial fields only on the CEA archetypes mapper information.

The logic is **reverting the process** CEA follows to work seamlessly in QGIS and created the needed files automatically under a specified path. Instead of creating a contour and selecting the buildings inside the areas (CEA-wise), the script creates a **convex hull enveloping the selected buildings**, constraining it to the farthest vertexes of the boundary polygons, basically reverting the process.

### Two methodological steps are of a certain importance:

1. Setting up correctly the structure of the folders where to copy paste the generated files, considering that every time (if the main directory stands the same) they will be overwritten.
2. Using the right command to execute the script with the right pattern on QGIS Python plugin interface.

---

### 2.1 Setting up the Working Directory

Typically the directory tree of a complete CEA project ("Esempio") shows the following structure:

```
C:.
├───Esempio
    ├───inputs
    │   ├───building-geometry         ← zone.shp, site.shp go here
    │   ├───building-properties       ← typology.dbf goes here
    │   │   └───schedules
    │   ├───networks
    │   ├───technology
    │   │   ├───archetypes
    │   │   │   └───use_types
    │   │   ├───assemblies
    │   │   └───components
    │   ├───topography
    │   └───weather
    └───outputs
        └───data
            ├───costs
            ├───demand
            ├───occupancy
            ├───optimization
            │   └───master
            └───solar-radiation
```

The usual structure of the files contained in the folder **`building-geometry`** is as follows:

```
**85   site.dbf
 401  site.prj
 364  site.shp
 108  site.shx**
 10   surroundings.cpg
4,945 surroundings.dbf
 401  surroundings.prj
2,796 surroundings.shp
 204  surroundings.shx
**10   zone.cpg
6,903 zone.dbf
 401  zone.prj
2,444 zone.shp
 140  zone.shx**
```

The **bolded files** are the ones that make the entities in CEA and that the script generates.

Together with these files, the file **typology.dbf** is generated and should go into the folder **`building-properties`**.

Each project has its unique set of these three groups of files as above.

---

### 2.2 How to Use the Script in QGIS

Using the script in QGIS is easy and it needs the following steps to be implemented:

#### Setup

First of all, create a folder named as you wish under a directory where you have full writing rights as administrator (e.g., `C:\CEAQGIS\[your_folder_name]`) and copy paste the file `qgis_to_cea_export.py` you can download from the repository.

#### Step-by-Step Guide

1. **Open QGIS**
2. **Open the shapefiles** with the related buildings
3. **Project the layer as WGS84 EPSG:4326**, by reprojecting the files with the toolbox function "re-project" (and not by simply assigning the geographic reference system)
4. **Select the buildings** you want to use as a project in CEA and be sure the layer (the reprojected one or the one originally in WGS84 EPSG:4326) is kept active (it appears highlighted)
   
   > ⚠️ **Important:** The algorithm will export only the selected buildings in the active layer each time, overwriting the files previously generated → consider to change directory every time you want to have separate back-up copies

5. Under the menu **"Plugins"** → open **Python Console**
6. Start the script with the following command in the Python console (second white space with the `>>>`) by pressing Enter, and replace `[your_folder_name]` with the chosen name:

```python
exec(open(r'C:\[your_folder_name]\qgis_to_cea_export.py').read()); run_from_qgis()
```

7. **Choose output folder** when prompted by the file dialog

8. Go to the folder (e.g., `C:\CEAQGIS`) and locate the following files:
   - The **"site"** files (`.cpg`, `.dbf`, `.prj`, `.shp` and `.shx`)
   - The **"zone"** files (`.cpg`, `.dbf`, `.prj`, `.shp` and `.shx`)
   - **typology.dbf**

9. **Copy paste** the files from point 1) and 2) into the CEA folder project in the **`building-geometry`** folder

10. **Copy paste** the file **typology.dbf** 3) into the **`building-properties`** folder

11. **Open CEA Dashboard** (tested with CEA 3.39.4 - not tested yet with the new beta Version CEA 4)

12. **Open project** by assigning the folder `C:\CEAQGIS` as location

13. Load all the features and process your buildings by changing the attributes in the fields as you prefer

---

## 🚀 Quick Start (Alternative Method)

### From QGIS Python Console

```python
exec(open(r'C:\path\to\qgis_to_cea_export.py').read())
run_from_qgis()
```

### Standalone (No QGIS)

```python
from qgis_to_cea_export import export_shapefile_to_cea

result = export_shapefile_to_cea(
    shapefile_path='buildings.shp',
    output_folder='cea_scenario/inputs/building-geometry',
    default_use_type='MULTI_RES',
    default_year=2000
)

print(f"Exported {result['n_buildings']} buildings")
```

---

## 📦 Requirements

```bash
pip install geopandas shapely pyproj utm
```

- **QGIS** (for console usage) or standalone Python 3.8+
- **CEA** 3.x or higher (tested with CEA 3.39.4)

---

## 🔧 Attribute Mapping

### Automatic Detection

The script automatically detects and maps:

| QGIS Attribute | CEA Field | Notes |
|----------------|-----------|-------|
| `height`, `building:height`, `HEIGHT` | `height_ag` | Building height in meters |
| `floors`, `building:levels`, `nb_etages`, `FLOORS` | `floors_ag` | Number of floors above ground |
| `use`, `type`, `occupancy`, `building` | `use_type1` | Building use type |
| `year`, `start_date`, `construction`, `YEAR` | `year` | Construction year |
| `name`, `id`, `gid`, `fid` | `Name` | Building identifier |

### Supported Use Types

| Code | Meaning |
|------|---------|
| `MULTI_RES` | Multi-family residential (default) |
| `SINGLE_RES` | Single-family residential |
| `OFFICE` | Office |
| `RETAIL` | Retail |
| `HOTEL` | Hotel |
| `INDUSTRIAL` | Industrial |
| `SCHOOL` | School |
| `HOSPITAL` | Hospital |
| `RESTAURANT` | Restaurant |
| `PARKING` | Parking |

Edit `USE_TYPE_MAPPING` in the script for custom mappings.

---

## 📄 Files Generated

| File | Description | CEA Location |
|------|-------------|--------------|
| `zone.shp` (+ `.shx`, `.dbf`, `.prj`, `.cpg`) | Building footprints with CEA attributes | `inputs/building-geometry/` |
| `site.shp` (+ `.shx`, `.dbf`, `.prj`, `.cpg`) | Convex hull boundary of the study area | `inputs/building-geometry/` |
| `typology.dbf` | Building typology (use types, construction year, standards) | `inputs/building-properties/` |

All files use **UTM CRS** (meters) as required by CEA.

---

## 3. Results

The project will show the buildings exported from QGIS and imported in CEA, with all their attributes in the table of attributes. It works well and smoothly run.

### Common Errors and Solutions

The most common errors are:

1. **Set up of the directory of the files** - Ensure you have write permissions and the correct folder structure
2. **Python extensions not yet installed** or not correctly pipelined - Install required packages: `geopandas`, `shapely`, `pyproj`, `utm`
3. **Environment variables** - Consider adding the right path to your environment variables
4. **CRS mismatch** - One of the most common issues occurring during this procedure. It can be reduced or avoided by **reprojecting the file** (as explained above) and not simply re-assigning the CRS (usually made by right-clicking on a layer and selecting the right option)

---

## 🛠️ Troubleshooting

### "No valid active layer"
- Ensure a polygon/multipolygon layer is selected in QGIS

### "Input has no CRS"
- Set CRS: Layer → Properties → Source → Coordinate Reference System
- Reproject to WGS84 EPSG:4326 using the "Reproject Layer" tool

### "No features selected"
- Use QGIS selection tool (click or box-select buildings)

### Buildings missing in CEA
- Check that `Name` field starts with a letter (e.g., `B1000`)
- Verify CRS is UTM (meters)
- Run CEA's geometry validator

### "Failed to export selection to GeoJSON"
- Check geometries are valid: Vector → Geometry Tools → Fix Geometries
- Ensure layer geometry type matches (Polygon or MultiPolygon)

---

## 4. Conclusion

This simple Python console in QGIS lets the user have more operativity and freedom as far as importing buildings not present or badly digitized in CEA are concerned. The output and related trials gave **100% success** in obtaining results in CEA bypassing the contour methodology and retro-importing it by using the convex hull function.

---

## ⚖️ License & Attribution

### Non-Commercial Use (CC BY-NC 4.0)

- ✅ Free for research, education, and non-profit projects
- ✅ **Citation is mandatory** (see above)
- ❌ Commercial use prohibited without license

### Commercial Licensing

For commercial projects, consulting, or SaaS integration:  
📧 Contact: **emilio.sessa@example.com**

### Derivative Works

If you integrate this script into your own software (e.g., `main.py`):

1. ✅ **Keep the citation notice** at the top of the file
2. ✅ **Include the DOI** in your documentation
3. ✅ **Acknowledge** in publications and user manuals
4. ❌ **Do not remove** attribution comments

**Failure to comply is a license breach.**

---

## 📚 Related Projects

- [City Energy Analyst (CEA)](https://github.com/architecture-building-systems/CityEnergyAnalyst)
- [QGIS](https://qgis.org/)

---

## 🙏 Acknowledgments

Built for urban energy modeling workflows integrating QGIS and CEA.

---

## 📞 Contact & Support

**Author:** Emilio Sessa  
**Email:** emilio.sessa@unipa.it/emiliosessaing@gmail.com
**LinkedIN:** https://www.linkedin.com/in/emiliosessa/
**DOI:** [10.5281/zenodo.18837000](https://doi.org/10.5281/zenodo.18837000)

For bug reports, feature requests, or citation inquiries, please include the DOI in your message.

---

## ⚠️ Important Legal Notice

This software is protected by copyright and licensed under CC BY-NC 4.0.  
**Citation is legally required** for all uses (academic, research, and software integration).  
Removal or modification of attribution notices is prohibited.

For commercial licensing: **emiliosessaing@gmail.com**

---

**© 2026 Emilio Sessa | DOI: 10.5281/zenodo.18837000**
