# MAC BUILD

## Download and run (staff)

**Mac only** — Windows staff should use `WINDOWS BUILD/README.md` instead.

- Release page: [macOS App (SCU_Clipboard_Builder)](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01)
- Direct download: [SCU_Clipboard_Builder.app.zip](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/download/macos-app-2026-07-01/SCU_Clipboard_Builder.app.zip)

Steps:
1. Download the zip from the link above.
2. Unzip it.
3. Open `SCU_Clipboard_Builder.app`.
4. If macOS blocks launch, use right-click -> **Open**, or **Privacy & Security** -> **Open Anyway**.

Local copy (for maintainers): `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`

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
