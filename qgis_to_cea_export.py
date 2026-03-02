"""
QGIS to City Energy Analyst (CEA) Export Script

Author: Emilio Sessa
DOI: https://doi.org/10.5281/zenodo.18837000
Version: 1.0.0
Date: 2026-03-02

═══════════════════════════════════════════════════════════════════════════════
MANDATORY CITATION NOTICE
═══════════════════════════════════════════════════════════════════════════════

If this script or any derivative work based on it is used in research,
publications, software integrations, or commercial projects, the following
DOI MUST be cited:

    Sessa, E. (2026). QGIS to CEA Conversion Script.
    Zenodo. https://doi.org/10.5281/zenodo.18837000

Unauthorized redistribution or removal of this citation notice is prohibited
and constitutes a breach of the license terms.

License: CC-BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International)
For commercial licensing inquiries, contact: emilio.sessa@example.com

═══════════════════════════════════════════════════════════════════════════════

DESCRIPTION:
Exports selected building polygons from an active QGIS multipolygon layer to
CEA-compatible shapefiles: zone.shp, site.shp, and typology.dbf.

REQUIREMENTS:
- Run from QGIS Python Console (Plugins > Python Console)
- Or run standalone with: python qgis_to_cea_export.py (uses last saved project layer)
- Dependencies: geopandas, shapely, pyproj, utm (pip install geopandas shapely pyproj utm)

USAGE IN QGIS:
1. Load your building multipolygon layer
2. Select the buildings you want to export (use selection tool)
3. Run this script from Python Console
4. Choose output folder when prompted
5. Copy zone.shp, site.shp, typology.dbf (and .shx, .dbf, .prj) to your CEA scenario:
   inputs/building-geometry/ and inputs/building-properties/

CRS: Automatically converts to WGS84 then to UTM (meters) for CEA compatibility.
"""

import warnings

# Runtime citation reminder (executes once per import)
warnings.warn(
    "\n"
    "═══════════════════════════════════════════════════════════════════════════\n"
    "  QGIS to CEA Export Script | DOI: 10.5281/zenodo.18837000\n"
    "  © 2026 Emilio Sessa | Citation required in academic & derivative work\n"
    "═══════════════════════════════════════════════════════════════════════════\n",
    UserWarning,
    stacklevel=2
)

# CEA required columns (zone.shp attribute table) - use 'Name' (capital N) for CEA dashboard
COLUMNS_ZONE = [
    'Name', 'floors_bg', 'floors_ag', 'void_deck', 'height_bg', 'height_ag',
    'reference', 'geometry',
    'year', 'const_type',
    'use_type1', 'use_type1r', 'use_type2', 'use_type2r', 'use_type3', 'use_type3r',
    'house_no', 'street', 'postcode', 'house_name', 'resi_type', 'city', 'country'
]

# QGIS attribute names -> CEA use_type1 (common mappings)
USE_TYPE_MAPPING = {
    'residential': 'MULTI_RES', 'apartments': 'MULTI_RES', 'house': 'SINGLE_RES',
    'office': 'OFFICE', 'commercial': 'OFFICE', 'retail': 'RETAIL',
    'hotel': 'HOTEL', 'industrial': 'INDUSTRIAL', 'school': 'SCHOOL',
    'hospital': 'HOSPITAL', 'restaurant': 'RESTAURANT', 'parking': 'PARKING',
}

# CEA construction standards by year (simplified)
CONST_TYPE_BY_YEAR = {
    (1980, 1990): 'pre-1980',
    (1990, 2000): '1980-2000',
    (2000, 2010): '2000-2010',
    (2010, 2020): '2010-2020',
    (2020, 2030): 'new',
}


def get_utm_crs(lat: float, lon: float) -> str:
    """Get UTM CRS string for given WGS84 lat/lon (CEA-style)."""
    try:
        import utm
        easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
        is_northern = zone_letter and zone_letter >= 'N'
        epsg = 32600 + zone_number if is_northern else 32700 + zone_number
        return f"EPSG:{epsg}"
    except Exception:
        # Fallback: use pyproj to guess UTM
        from pyproj import CRS
        zone = int((lon + 180) / 6) + 1
        epsg = 32600 + zone  # Northern hemisphere default
        return f"EPSG:{epsg}"


def get_lat_lon_from_gdf(gdf):
    """Get centroid lat/lon from GeoDataFrame (WGS84)."""
    from pyproj import CRS
    wgs84 = CRS.from_epsg(4326)
    temp = gdf if gdf.crs and '4326' in str(gdf.crs) else gdf.to_crs(wgs84)
    pt = temp.unary_union.centroid
    return pt.y, pt.x


def map_height_floors(row, height_cols, floors_cols, default_height=12.0, default_floors=4):
    """Map height and floors from QGIS attributes with fallbacks."""
    height = default_height
    floors = default_floors
    for c in height_cols:
        if c in row.index and row[c] is not None:
            try:
                v = float(row[c])
                if v > 0:
                    height = max(1.0, v)
                    break
            except (TypeError, ValueError):
                pass
    for c in floors_cols:
        if c in row.index and row[c] is not None:
            try:
                v = int(float(row[c]))
                if v >= 1:
                    floors = v
                    break
            except (TypeError, ValueError):
                pass
    if height <= 0:
        height = floors * 3.0  # ~3 m per floor
    if floors < 1:
        floors = max(1, int(height / 3.0))
    return height, floors


def map_use_type(row, use_cols):
    """Map use type from QGIS attributes."""
    for c in use_cols:
        if c in row.index and row[c]:
            val = str(row[c]).strip().lower()
            for k, v in USE_TYPE_MAPPING.items():
                if k in val:
                    return v
    return 'MULTI_RES'  # default


def get_const_type(year: int) -> str:
    """Map construction year to CEA const_type."""
    for (a, b), ct in CONST_TYPE_BY_YEAR.items():
        if a <= year < b:
            return ct
    return 'new'


def selected_features_to_cea(output_folder: str, default_use_type: str = 'MULTI_RES',
                             default_year: int = 2000):
    """
    Export selected features from QGIS active layer to CEA format.

    Args:
        output_folder: Path to save zone.shp and site.shp
        default_use_type: CEA use type when no mapping (e.g. MULTI_RES, OFFICE)
        default_year: Construction year when not in attributes
    """
    try:
        from qgis.core import QgsProject, QgsVectorLayer
        from qgis.utils import iface
        USE_QGIS = True
    except ImportError:
        USE_QGIS = False

    if USE_QGIS:
        layer = iface.activeLayer()
        if not layer or not layer.isValid():
            raise ValueError("No valid active layer. Select a multipolygon layer and run again.")
        if layer.selectedFeatureCount() == 0:
            raise ValueError("No features selected. Select buildings first, then run script.")

        from qgis.PyQt.QtCore import QVariant
        from qgis.PyQt.QtWidgets import QFileDialog
        import tempfile
        import os

        # Get selected features as GeoJSON, then load with geopandas
        selection = layer.selectedFeatures()
        crs = layer.crs()
        authid = crs.authid() if crs and crs.authid() else "EPSG:4326"
        # Use source layer's geometry type (Polygon or MultiPolygon)
        from qgis.core import QgsWkbTypes
        geom_type = QgsWkbTypes.displayString(layer.wkbType()) or "MultiPolygon"
        mem_layer = QgsVectorLayer(f"{geom_type}?crs={authid}", "temp", "memory")
        if not mem_layer.isValid():
            raise RuntimeError("Failed to create temporary memory layer.")
        if not mem_layer.dataProvider().addFeatures(selection):
            raise RuntimeError(
                "Failed to add selected features to memory layer. "
                "Check that geometries are valid (Vector > Geometry Tools > Fix Geometries)."
            )
        mem_layer.updateExtents()

        tmp_geojson = os.path.join(tempfile.gettempdir(), "qgis_cea_temp.geojson")
        from qgis.core import QgsVectorFileWriter
        result = QgsVectorFileWriter.writeAsVectorFormat(
            mem_layer, tmp_geojson, "UTF-8", crs, "GeoJSON"
        )
        # PyQGIS 3.x returns (error, errorMessage) tuple
        if isinstance(result, tuple):
            err, err_msg = result
        else:
            err, err_msg = result, ""
        if err != QgsVectorFileWriter.NoError:
            raise RuntimeError(
                f"Failed to export selection to GeoJSON. {err_msg or str(err)}"
            )

        import geopandas as gpd
        gdf = gpd.read_file(tmp_geojson)
        try:
            os.remove(tmp_geojson)
        except OSError:
            pass
    else:
        raise RuntimeError(
            "Run this script from QGIS Python Console. "
            "Or provide a shapefile path and use export_shapefile_to_cea()."
        )

    return _process_and_save(gdf, output_folder, default_use_type, default_year)


def export_shapefile_to_cea(shapefile_path: str, output_folder: str,
                            id_field: str = None, selection_ids: list = None,
                            default_use_type: str = 'MULTI_RES', default_year: int = 2000):
    """
    Export buildings from a shapefile to CEA format (standalone, no QGIS).

    Args:
        shapefile_path: Path to input multipolygon shapefile
        output_folder: Path to save zone.shp and site.shp
        id_field: Field name for selection (if selection_ids given)
        selection_ids: List of IDs to export (optional; if None, exports all)
    """
    import geopandas as gpd
    import os

    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")

    gdf = gpd.read_file(shapefile_path)
    if selection_ids is not None and id_field:
        gdf = gdf[gdf[id_field].isin(selection_ids)]
    if gdf.empty:
        raise ValueError("No features to export. Check selection.")

    return _process_and_save(gdf, output_folder, default_use_type, default_year)


def _write_typology_dbf(typology_df, dbf_path):
    """Write typology DataFrame to .dbf using GeoPandas (shapefile .dbf extraction)."""
    import geopandas as gpd
    import tempfile
    import shutil
    import os
    from shapely.geometry import Point

    # GeoPandas writes .dbf when saving shapefile; use temp shapefile to get .dbf
    tmp_dir = tempfile.mkdtemp()
    tmp_shp = os.path.join(tmp_dir, 'typology_temp.shp')
    try:
        typology_df = typology_df.copy()
        typology_df['geometry'] = [Point(0, 0)] * len(typology_df)  # dummy geometry
        gdf = gpd.GeoDataFrame(typology_df, geometry='geometry', crs='EPSG:4326')
        gdf.to_file(tmp_shp, driver='ESRI Shapefile')
        tmp_dbf = tmp_shp.replace('.shp', '.dbf')
        shutil.copy(tmp_dbf, dbf_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _process_and_save(gdf, output_folder, default_use_type, default_year):
    import geopandas as gpd
    import pandas as pd
    import numpy as np
    from shapely.ops import unary_union
    from shapely.geometry import Polygon, MultiPolygon
    import os

    # Normalize attribute names for case-insensitive lookup
    cols_lower = {c.lower(): c for c in gdf.columns if c != 'geometry'}
    def _col(name):
        return cols_lower.get(name.lower())

    height_cols = ['height', 'height_ag', 'height_ag_m', 'building:height', 'HEIGHT']
    floors_cols = ['floors', 'floors_ag', 'floors_above', 'building:levels', 'FLOORS', 'nb_etages']
    use_cols = ['use', 'use_type', 'building', 'type', 'occupancy', 'category', 'typology']
    year_cols = ['year', 'year_const', 'start_date', 'construction', 'YEAR']

    # 1. Ensure valid geometries and explode MultiPolygons
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf.explode(index_parts=False).reset_index(drop=True)
    gdf = gdf[gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])].copy()

    # Convert MultiPolygon to Polygon (take largest part)
    def _to_polygon(geom):
        if geom is None:
            return None
        if geom.geom_type == 'Polygon':
            return geom
        if geom.geom_type == 'MultiPolygon':
            polys = list(geom.geoms)
            return max(polys, key=lambda p: p.area) if polys else None
        return None

    gdf['geometry'] = gdf.geometry.apply(_to_polygon)
    gdf = gdf[gdf.geometry.notnull()].copy()

    # 2. CRS: Ensure WGS84 first (CEA expects this for UTM detection)
    from pyproj import CRS
    wgs84 = CRS.from_epsg(4326)
    if gdf.crs is None:
        raise ValueError(
            "Input has no CRS. Set CRS in QGIS (Layer > Properties > Source > CRS) before export."
        )
    gdf = gdf.to_crs(wgs84)

    # 3. Compute UTM CRS from centroid (CEA uses meters)
    lat, lon = get_lat_lon_from_gdf(gdf)
    utm_crs = get_utm_crs(lat, lon)
    gdf = gdf.to_crs(utm_crs)

    # 4. Build zone rows with CEA attributes
    rows = []
    for i, (idx, row) in enumerate(gdf.iterrows()):
        height, floors = map_height_floors(row, height_cols, floors_cols)
        use_type = map_use_type(row, use_cols) if any(_col(c) for c in use_cols) else default_use_type
        year_val = default_year
        for c in year_cols:
            if _col(c) and row.get(_col(c)) is not None:
                try:
                    year_val = int(float(row[_col(c)]))
                    break
                except (TypeError, ValueError):
                    pass

        name = f"B{i + 1000}"  # Must start with letter
        if _col('name') or _col('id') or _col('gid'):
            for fn in ['name', 'id', 'gid', 'fid']:
                if _col(fn) and row.get(_col(fn)) is not None:
                    raw = str(row[_col(fn)]).strip()
                    if raw and raw[0].isalpha():
                        name = raw
                    else:
                        name = f"B{raw}"
                    break

        rows.append({
            'Name': name,
            'floors_ag': int(floors),
            'floors_bg': 0,
            'void_deck': 0,
            'height_ag': float(height),
            'height_bg': 0.0,
            'reference': 'QGIS export',
            'geometry': row.geometry,
            'year': year_val,
            'const_type': get_const_type(year_val),
            'use_type1': use_type,
            'use_type1r': 1.0,
            'use_type2': 'NONE',
            'use_type2r': 0.0,
            'use_type3': 'NONE',
            'use_type3r': 0.0,
            'house_no': '',
            'street': '',
            'postcode': '',
            'house_name': '',
            'resi_type': '',
            'city': '',
            'country': '',
        })

    zone_gdf = gpd.GeoDataFrame(rows, crs=utm_crs, columns=COLUMNS_ZONE)

    # Ensure height/floors consistency (CEA validation)
    zone_gdf['height_ag'] = zone_gdf['height_ag'].clip(lower=1.0)
    zone_gdf['floors_ag'] = zone_gdf['floors_ag'].clip(lower=1)
    zone_gdf['height_ag'] = zone_gdf[['height_ag', 'floors_ag']].max(axis=1)

    # 5. Site: convex hull of all zone geometries
    site_geom = unary_union(zone_gdf.geometry.tolist())
    if hasattr(site_geom, 'convex_hull'):
        site_poly = site_geom.convex_hull
    else:
        site_poly = site_geom
    if site_poly.geom_type == 'MultiPolygon':
        site_poly = max(site_poly.geoms, key=lambda p: p.area)
    site_gdf = gpd.GeoDataFrame(
        [{'FID': 0, 'geometry': site_poly}],
        crs=utm_crs,
        columns=['FID', 'geometry']
    )

    # 6. Save shapefiles (include .prj for CRS)
    os.makedirs(output_folder, exist_ok=True)
    zone_path = os.path.join(output_folder, 'zone.shp')
    site_path = os.path.join(output_folder, 'site.shp')

    zone_gdf.to_file(zone_path, driver='ESRI Shapefile')
    site_gdf.to_file(site_path, driver='ESRI Shapefile')

    # 7. Save typology.dbf (CEA format: Name, STANDARD, YEAR, 1ST_USE, 1ST_USE_R, etc.)
    typology_path = os.path.join(output_folder, 'typology.dbf')
    typology_df = pd.DataFrame({
        'Name': zone_gdf['Name'],
        'STANDARD': 'STANDARD1',  # CEA default; edit in dashboard if needed
        'YEAR': zone_gdf['year'].astype(int),
        '1ST_USE': zone_gdf['use_type1'],
        '1ST_USE_R': zone_gdf['use_type1r'].astype(float),
        '2ND_USE': zone_gdf['use_type2'],
        '2ND_USE_R': zone_gdf['use_type2r'].astype(float),
        '3RD_USE': zone_gdf['use_type3'],
        '3RD_USE_R': zone_gdf['use_type3r'].astype(float),
    })
    _write_typology_dbf(typology_df, typology_path)

    return {
        'zone': zone_path,
        'site': site_path,
        'typology': typology_path,
        'crs': utm_crs,
        'n_buildings': len(zone_gdf),
    }


def run_from_qgis():
    """Run from QGIS Python Console - prompts for output folder."""
    try:
        from qgis.PyQt.QtWidgets import QFileDialog
        output_folder = QFileDialog.getExistingDirectory(None, "Select CEA output folder")
        if not output_folder:
            print("Export cancelled.")
            return
        result = selected_features_to_cea(output_folder)
        print(f"\n{'='*79}")
        print(f"✓ Exported {result['n_buildings']} buildings to {output_folder}")
        print(f"  - zone.shp, site.shp, typology.dbf")
        print(f"  - CRS: {result['crs']} (meters)")
        print(f"{'='*79}")
        print("Next steps:")
        print("  1. Copy zone.shp & site.shp to CEA: inputs/building-geometry/")
        print("  2. Copy typology.dbf to CEA: inputs/building-properties/")
        print(f"{'='*79}")
        print("QGIS → CEA Script | DOI: 10.5281/zenodo.18837000 | © Emilio Sessa")
        print(f"{'='*79}\n")
        return result
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == '__main__':
    # When run from QGIS Python Console: exec(open(r'path/to/qgis_to_cea_export.py').read())
    # Then call: run_from_qgis()
    # Or: selected_features_to_cea(r'C:\path\to\cea\scenario\inputs\building-geometry')
    print("═" * 79)
    print("QGIS to CEA Export Script")
    print("DOI: https://doi.org/10.5281/zenodo.18837000")
    print("© 2026 Emilio Sessa")
    print("═" * 79)
    print("\nUsage:")
    print("  From QGIS Python Console:")
    print("    run_from_qgis()")
    print("\n  Or with custom folder:")
    print("    selected_features_to_cea(r'C:\\output\\folder')")
    print("\nCitation required for all uses. See LICENSE for details.")
    print("═" * 79)
