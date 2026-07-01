# Build on your Windows PC

Everything you need is in this folder on GitHub:

**https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/tree/main/WINDOWS%20BUILD/Windows_Build_Source**

## Get this folder onto your PC

### Option A — Download the whole repo (easiest)

1. Open **https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace**
2. Click the green **Code** button → **Download ZIP**
3. Extract the zip (e.g. to `Downloads`)
4. Open: `SCU-Clipboard-Builder-Workspace-main\WINDOWS BUILD\Windows_Build_Source\`

### Option B — Git clone

```cmd
git clone https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace.git
cd SCU-Clipboard-Builder-Workspace\WINDOWS BUILD\Windows_Build_Source
```

## Build the app

1. In `Windows_Build_Source`, double-click **`build_windows.bat`**
2. Wait for the script to finish (installs Python deps and runs PyInstaller)
3. Output: **`win_SCU_CBoards.zip`** in this same folder — extract and run **`win_SCU_CBoards.exe`**

## Requirements

- Windows 10 or 11
- Python 3.10+ installed and on your PATH ([python.org](https://www.python.org/downloads/)) — check **“Add Python to PATH”** during install
- Internet on first build (downloads packages)

## What’s included here

| File | Purpose |
|------|---------|
| `build_windows.bat` | One-click build script |
| `SCU_CBoards.py` | Main app |
| `win_SCU_CBoards.py` | PyInstaller entry point |
| `ClinicForms/` | All clinic PDFs |
| `logo.png`, `white_logo_ui.png` | App logos |

See `README.md` in this folder for more detail.
