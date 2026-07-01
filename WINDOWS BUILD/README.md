# WINDOWS BUILD

## Download and run (staff)

**Windows only** — Mac staff should use `MAC BUILD/README.md` instead.

- Release page: [Windows App (win_SCU_CBoards)](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/windows-app-2026-07-01)
- Direct download: [win_SCU_CBoards.zip](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/download/windows-app-2026-07-01/win_SCU_CBoards.zip)

### Step-by-step (Windows 10/11)

1. Click the link above and save `win_SCU_CBoards.zip` to your **Downloads** folder.
2. Open **File Explorer** and go to **Downloads**.
3. **Right-click** `win_SCU_CBoards.zip` -> **Extract All...** -> **Extract**.
4. Open the new **`win_SCU_CBoards`** folder (a folder icon, not the zip).
5. Double-click **`win_SCU_CBoards.exe`**.

### If Windows blocks the app

- If you see **Windows protected your PC**: click **More info** -> **Run anyway**.
- Do **not** try to open the `.zip` directly — always **Extract All** first.
- Do **not** run `build_windows.bat` — that is only for developers rebuilding the app.

### Common mistakes

| Problem | Fix |
|---|---|
| "What app should open this .zip?" | Use **Extract All** in File Explorer, not double-click to open the zip |
| Nothing happens when double-clicking | Make sure you opened `win_SCU_CBoards.exe` inside the **extracted folder** |
| SmartScreen warning | **More info** -> **Run anyway** |
| Old version / missing forms | Download the zip again from the link above |

## Build from source (developers)

Source and build script live in:

- `WINDOWS BUILD/Windows_Build_Source/`

Copy that folder to a Windows PC, then double-click `build_windows.bat`.
