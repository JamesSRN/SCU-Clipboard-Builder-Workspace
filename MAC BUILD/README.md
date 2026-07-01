# MAC BUILD

## Download and run (Saturday Clinic volunteers)

**Mac only** — if you use Windows, see [`WINDOWS BUILD/README.md`](../WINDOWS%20BUILD/README.md) instead.

**Start here:** [macOS App — SCU Clipboard Builder (July 2026)](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01)

Install instructions for **The Saturday Clinic** (free care for uninsured patients in Milwaukee). Scroll to **Assets** at the bottom of that page to download `SCU_Clipboard_Builder.app.zip`.

### Quick reminder

1. Open the release page link above.
2. Download **`SCU_Clipboard_Builder.app.zip`** from **Assets**.
3. Unzip it.
4. Open **`SCU_Clipboard_Builder.app`**.

If macOS blocks the app, the release page explains how to use **Open** or **Open Anyway**.

Local copy (for maintainers): `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`

---

## Build from source (developers)

Use a **dedicated minimal Python environment** for Mac builds. Do not use a general-purpose conda env (for example one with torch/scipy installed) or PyInstaller will bundle hundreds of MB of unused libraries.

PyInstaller spec file:

- `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`

Build dependencies:

- `MAC BUILD/mac_build/requirements-build.txt`

Build command (from repo root):

```bash
cd "/path/to/SCU"

# One-time: create a clean build venv
python3 -m venv ".venv-scu-mac-build"
source ".venv-scu-mac-build/bin/activate"
pip install -r "MAC BUILD/mac_build/requirements-build.txt"

# Build
pyinstaller --clean --noconfirm \
  --distpath "MAC BUILD/dist" \
  --workpath "MAC BUILD/build" \
  "MAC BUILD/mac_build/SCU_Clipboard_Builder.spec"
```

Expected app size after a clean build: roughly **120–180 MB** unzipped (vs ~740 MB when built from a bloated conda env).

Build outputs (`MAC BUILD/build/`, `MAC BUILD/dist/`) stay local and are not committed because of size.
