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

### If welcome packet still shows "missing"

1. Confirm you downloaded **[windows-app-2026-07-01](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/windows-app-2026-07-01)** — not the Mac `.app.zip`, not the May 2026 release, and not the repo "Code" source zip.
2. Delete any old `win_SCU_CBoards` folder, then extract the new zip fresh.
3. In File Explorer, verify this file exists (about 9 MB):
   `win_SCU_CBoards\_internal\ClinicForms\english\welcome_packet.pdf`
4. Open the app and check the log at the bottom. It should say `Forms folder auto-selected: ClinicForms`.
5. If welcome packet is still missing, click **Select Forms Folder** and choose:
   `win_SCU_CBoards\_internal\ClinicForms` (inside your extracted folder).

**Git / GitHub code updates do not change the app on your PC.** Staff must download the release zip above — pushing git from a developer machine does not update installed apps.

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
