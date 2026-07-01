# APP FILES

Everything for the **SCU Clipboard Builder app** lives here — source code, clinic forms, logos, and archives.

**Front desk staff:** you do **not** need this folder. Use the release page links in the [main README](../README.md), [`MAC BUILD`](../MAC%20BUILD/README.md), or [`WINDOWS BUILD`](../WINDOWS%20BUILD/README.md).

---

## What's here

| Path | Purpose |
|------|---------|
| `SCU_CBoards.py` | Main app (run locally or package into Mac/Windows builds) |
| `APP SOURCE/ClinicForms/` | Live clinic PDF forms (English, Spanish, Mandarin) |
| `APP SOURCE/icon.iconset/` | Mac app icon sources |
| `logo.png`, `white_logo_ui.png` | App logos |
| `SCU_logo.icns` | Mac app icon for PyInstaller |
| `OTHER FILES/` | Older reference material, exports, debug archives |

---

## Run locally (maintainers)

```bash
cd "/path/to/SCU"
python3 "APP FILES/SCU_CBoards.py"
```

Use a venv with `pyside6`, `pypdf`, `reportlab`, and `pillow` — see `MAC BUILD/mac_build/requirements-build.txt`.

---

## Builds

- **Mac:** `MAC BUILD/` reads from this folder via `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`
- **Windows:** `WINDOWS BUILD/Windows_Build_Source/` has its own copy for PC builds (sync forms from `APP SOURCE/ClinicForms/` when updating PDFs)
