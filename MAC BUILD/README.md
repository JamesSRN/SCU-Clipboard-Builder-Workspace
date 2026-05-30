# MAC BUILD

## Download and run (staff)
Pre-built macOS app zip:

- [Download SCU_Clipboard_Builder.app.zip (GitHub Releases)](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/latest/download/SCU_Clipboard_Builder.app.zip)

Steps:
1. Download the zip from the link above.
2. Unzip it.
3. Open `SCU_Clipboard_Builder.app`.
4. If macOS blocks launch, use right-click -> **Open**, or **Privacy & Security** -> **Open Anyway**.

Local copy (for maintainers): `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`

## Build from source (developers)
PyInstaller spec file:

- `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`

Build command (from repo root):

```bash
cd "/path/to/SCU"
eval "$(conda shell.bash hook)" && conda activate gnarnia
pyinstaller --clean --windowed --noconsole --noconfirm \
  --specpath "MAC BUILD/mac_build" \
  --distpath "MAC BUILD/dist" \
  --workpath "MAC BUILD/build" \
  "MAC BUILD/mac_build/SCU_Clipboard_Builder.spec"
```

Build outputs (`MAC BUILD/build/`, `MAC BUILD/dist/`) stay local and are not committed because of size.
