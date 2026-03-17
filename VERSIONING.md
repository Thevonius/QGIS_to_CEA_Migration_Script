# Versioning & Git (GitHub)

This repository uses **Semantic Versioning** (MAJOR.MINOR.PATCH). The script version is set in `qgis_to_cea_export.py` (header), `CITATION.cff`, `.zenodo.json`, and `README.md`.

---

## Repository already on GitHub

If the repo is already on GitHub, use the following workflow for updates.

### 1. Commit your changes

```powershell
cd C:\CEAQGIS
git status
git add qgis_to_cea_export.py README.md LICENSE CITATION.cff .zenodo.json CHANGELOG.md VERSIONING.md
git add FINAL_SUMMARY.md CHECKLIST.md QUICKSTART.md IMPLEMENTATION_SUMMARY.md USAGE_EXAMPLES.md CONTRIBUTORS.md
git commit -m "Update author info: affiliation, emails, LinkedIn; add CHANGELOG and versioning guide"
```

### 2. Push to GitHub

```powershell
git push origin main
```

(Use `master` instead of `main` if your default branch is `master`.)

### 3. Create a release (optional, for Zenodo)

1. On GitHub: **Releases** → **Create a new release**
2. **Tag:** `v1.0.0` (create new tag)
3. **Release title:** e.g. `v1.0.0 - Initial release`
4. **Description:** Copy from `CHANGELOG.md` or write a short summary
5. **Publish release**

If Zenodo is linked to the repo, it will archive this release and assign/update the DOI.

---

## When to bump version

- **PATCH (1.0.x):** Bug fixes, small fixes, doc/contact updates → e.g. `1.0.1`
- **MINOR (1.x.0):** New features, backward compatible → e.g. `1.1.0`
- **MAJOR (x.0.0):** Breaking changes or major redesign → e.g. `2.0.0`

### Files to update when bumping version

1. `qgis_to_cea_export.py` — header `Version: X.Y.Z`
2. `CITATION.cff` — `version: X.Y.Z` and `date-released: YYYY-MM-DD`
3. `.zenodo.json` — `version`, `publication_date`
4. `README.md` — **Version** and **Date** in the header block
5. `CHANGELOG.md` — add a new `[X.Y.Z] - YYYY-MM-DD` section

---

## Quick reference

| Action              | Command / step                                      |
|---------------------|-----------------------------------------------------|
| See status          | `git status`                                        |
| Commit all          | `git add -A` then `git commit -m "message"`         |
| Push                | `git push origin main`                              |
| Create tag          | `git tag v1.0.0`                                    |
| Push tags           | `git push origin v1.0.0`                            |
| New release on GitHub | Releases → Create new release → choose tag → Publish |

---

**© 2026 Emilio Sessa | DOI: 10.5281/zenodo.18837000**
