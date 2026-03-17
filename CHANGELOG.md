# Changelog

All notable changes to the QGIS to CEA Export Script are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026-03-02

### Added

- Initial release of QGIS to CEA conversion script
- Export selected building polygons to CEA-compatible `zone.shp`, `site.shp`, and `typology.dbf`
- Automatic CRS conversion (WGS84 → UTM)
- Attribute mapping for height, floors, use types, construction year
- Preservation of CEA-native fields from source when present (height_ag, floors_ag, etc.)
- Citation and license notices (CC BY-NC 4.0)
- DOI: 10.5281/zenodo.18837000

### Author & Citation

- **Author:** Emilio Sessa
- **Affiliation:** PhD XXXIX cycle in Energy, University of Palermo, Viale delle Scienze - building 8
- **Contact:** emilio.sessa@unipa.it | emiliosessaing@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/emiliosessa

---

[1.0.0]: https://github.com/emiliosessa/CEAQGIS/releases/tag/v1.0.0
