# SCU Clipboard Builder

## Overview
`SCU_CBoards.py` is an offline desktop app that converts a pasted clinic schedule into patient-specific PDF clipboard packets.

Primary goals:
- Keep PHI local (no cloud/database/network dependencies).
- Let staff paste directly from Sheets/Excel and quickly verify output.
- Generate consistent, correctly ordered packets in both single and batch workflows.

## Download Here
- macOS app zip: [SCU_Clipboard_Builder.app.zip](https://mcw0.sharepoint.com/:u:/s/BOD-SCU/IQDmNDK4cdFqTb_LBHnuQsoTAbp0K__EMv3jYaU9zvMidgo?e=XMDa99)
- Windows app zip: [win_SCU_CBoards.zip](https://mcw0.sharepoint.com/:u:/s/BOD-SCU/IQCzyF6dq97pR6HtDdEo810ZAYrZ8pyl_PX9sJBoOKHWW34?e=AZDFLy)

## Current Folder Layout
The local workspace is organized into these long-term buckets:

```text
SCU/
├── APP SOURCE/
│   ├── ClinicForms/
│   └── icon.iconset/
├── MAC BUILD/
│   ├── build/
│   ├── dist/
│   ├── mac_build/
│   └── repo_export_mac/
├── WINDOWS BUILD/
│   ├── Windows_Build_Source/
│   └── repo_export_windows/
├── OTHER FILES/
└── (top-level source/docs/assets still in active use)
```

Practical intent:
- source code and live forms stay tied to the main project
- Mac packaging outputs live under `MAC BUILD/`
- Windows packaging source/output lives under `WINDOWS BUILD/`
- older/debug/reference material lives under `OTHER FILES/`

---

## Privacy + Offline Behavior
- No network APIs are used.
- Patient data lives in memory during the current session only.
- **Clear Session (Privacy)** wipes parsed patient data and preview state.
- Output PHI is only written to user-selected PDF output files.

---

## Main Script
- Entry point: `SCU_CBoards.py`
- Core classes:
  - `PDFProcessor`: form path resolution, top-sheet personalization, PDF merge.
  - `ClinicApp`: Qt UI, spreadsheet paste/edit, patient parsing, preview, output actions.

---

## Input Workflow (Spreadsheet-in-App)
The app uses an in-app spreadsheet (`QTableWidget`) with default columns:

1. `Time`
2. `Patient Name`
3. `DOB`
4. `Room`
5. `Language`
6. `Initial Visit Intake`
7. `Annual Demographics`
8. `Specialty Clinics Consent`
9. `Care Message`
10. `PHQ 2-9`
11. `GAD 7`
12. `TB`
13. `Welcome Packet`

### Parsing behavior
- Paste directly from clipboard (tab/newline grid).
- Staff can edit cells directly in the grid after paste.
- The patient preview auto-refreshes when spreadsheet cells are edited.
- If pasted row 1 looks like headers, the app uses those pasted headers immediately to align incoming values into the app's fixed columns.
- The pasted header row itself is treated as mapping metadata and is not left behind as a patient row in the spreadsheet body.
- If no header row is pasted, app falls back to built-in default headers.
- Any non-blank marker in optional form columns counts as selected (`x`, `need`, `fill`, etc.).
- If a no-header paste looks shifted left by one column, the app prompts the user immediately after paste.
- `Yes` shifts the visible spreadsheet one column to the right so the UI matches the intended columns.
- `No` keeps the spreadsheet and preview exactly as pasted, with no hidden correction.
- `Cancel` dismisses the shift action and leaves the pasted grid unchanged.
- When a visible shift is applied, the info log records only the first populated row's moved values and target headers.
- PDF generation rebuilds patient data from the current spreadsheet automatically, so staff do not need to click **Build Patient Preview** before generating.
- Demo rows named `Al Demo` / `al demo` are excluded from the patient preview and generated outputs.

---

## Top Sheet Personalization
Top sheet template filename:
- `top_sheet.pdf`

Filled fields:
- `Patient Name`
- `Date of Birth`
- `Room Number`
- `Language`

Implementation details:
- Field rectangles are read from top-sheet widgets.
- Values are drawn as static overlay text into those rectangles.
- Text is auto-sized to fit each field box.
- A compact **Included Forms** list is rendered under DOB.
- Each listed form includes its resolved language/source label, such as:
  - `medical_consent (spanish)`
  - `initial_visit_intake (mandarin)`
  - `vitals_sheet (fallback english)`
  - `patient_synopsis (default fallback)`

Why this approach:
- Avoids interactive AcroForm batch merge issues.
- Produces stable, readable output per patient in batch mode.

---

## Packet Composition and Order
Required forms (always included):
- `medical_consent.pdf`
- `vitals_sheet.pdf`
- `patient_synopsis.pdf`
- `post_visit_instructions.pdf`

Optional forms (from schedule marks):
- `initial_visit_intake.pdf`
- `annual_demographics.pdf`
- `caremessage_consent.pdf`
- `specialty_clinic_consent.pdf`
- `phq9.pdf`
- `gad7.pdf`
- `tb_form.pdf`
- `welcome_packet.pdf`

Canonical order:
1. `top_sheet.pdf`
2. `medical_consent.pdf`
3. `initial_visit_intake.pdf` (if selected)
4. `annual_demographics.pdf` (if selected)
5. `caremessage_consent.pdf` (if selected)
6. `specialty_clinic_consent.pdf` (if selected)
7. `phq9.pdf` (if selected)
8. `gad7.pdf` (if selected)
9. `tb_form.pdf` (if selected)
10. `welcome_packet.pdf` (if selected)
11. `vitals_sheet.pdf`
12. `patient_synopsis.pdf`
13. `post_visit_instructions.pdf`

Extra optional forms not in the explicit map are inserted **before** `vitals_sheet.pdf`.

---

## Language Handling and Fallbacks
Normalized language output examples:
- `english`
- `spanish`
- `mandarin`

Input normalization supports:
- Multi-language cells (`Spanish, English`, `English / Arabic`, etc.)
- Mixed separators (`/`, `,`, `;`, `|`, `&`, `and`)
- Extra spaces and noisy text

Priority rule:
- If English appears anywhere in a multi-language value, language resolves to `english`.

Per-form path resolution order:
1. Requested language folder (e.g., `ClinicForms/spanish/`)
2. `ClinicForms/default/`
3. `ClinicForms/english/`

Preview shows the source label:
- `(english)`, `(spanish)`, `(mandarin)`
- `(default fallback)`
- `(fallback english)`
- `(missing)`

---

## Form Folder Layout + Naming
Expected structure:

```text
APP SOURCE/ClinicForms/
├── english/
├── spanish/
├── mandarin/
└── default/
```

Accepted filename variants for base file `phq9.pdf`:
- `phq9 (spanish).pdf`
- `phq9 (mandarin).pdf`
- `phq9_spanish.pdf`
- `phq9_mandarin.pdf`
- `phq9-spanish.pdf`
- `phq9-mandarin.pdf`
- `phq9.pdf`

The resolver prefers language-labeled variants before plain filename.

---

## UI / Branding
- Window title: **SCU Clipboard Builder**
- Dark emerald/hunter-green theme accents
- Orange title text
- Top-right header logo (UI asset prioritizes `white_logo_ui.png`)
- App icon: `SCU_logo.icns`
- Patient name rows in preview highlighted orange

---

## Resource Loading (Dev vs Bundled App)
Resource discovery supports:
- Running from source folder
- Running from PyInstaller `.app` bundle

Assets/forms used in packaged builds:
- `ClinicForms/`
- `logo.png`
- `white_logo_ui.png`

During local development, the app now auto-detects forms from:
- `APP SOURCE/ClinicForms/`
- or bundled `ClinicForms/` inside packaged builds

Log path output is sanitized for cleaner/non-personal display where possible.

---

## Run Locally (Conda `gnarnia`)
```bash
cd "/Users/jamessobieski/Documents/SCU"
eval "$(conda shell.bash hook)" && conda activate gnarnia
python SCU_CBoards.py
```

---

## Build macOS App (PyInstaller)
```bash
cd "/Users/jamessobieski/Documents/SCU"
rm -rf "MAC BUILD/build" "MAC BUILD/dist" "MAC BUILD/mac_build"
eval "$(conda shell.bash hook)" && conda activate gnarnia
pyinstaller --clean --windowed --noconsole \
  --specpath "MAC BUILD/mac_build" \
  --distpath "MAC BUILD/dist" \
  --workpath "MAC BUILD/build" \
  --name "SCU_Clipboard_Builder" \
  --icon "SCU_logo.icns" \
  --add-data "APP SOURCE/ClinicForms:ClinicForms" \
  --add-data "logo.png:." \
  --add-data "white_logo_ui.png:." \
  SCU_CBoards.py
```

Build artifact:
- `MAC BUILD/dist/SCU_Clipboard_Builder.app`
- Shareable Mac zip (recommended for Google Drive/email):
  - `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`
- Mac-specific PyInstaller spec file:
  - `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`

---

## Build Windows App (PyInstaller)
The app logic is already mostly cross-platform because it uses:
- `PySide6`
- `pandas`
- `pypdf`
- `reportlab`

To create a real Windows app, build it on a Windows machine (or Windows VM). PyInstaller should be run from Windows so it can produce a native `.exe`.

Windows-specific packaging files live in:
- `WINDOWS BUILD/Windows_Build_Source/`

This separation prevents the Windows packaging flow from overwriting the Mac app spec/build configuration.

### Recommended setup on Windows
1. Install Python 3.10+.
2. Make sure Python is available as either `py` or `python`.
3. Optional: create or activate a virtual environment.
4. If you want to build manually instead of using the batch file, install dependencies:

```bash
pip install pyside6 pypdf reportlab pandas openpyxl pyinstaller
```

### Windows icon note
Windows packaging expects an `.ico` file instead of `.icns`.

If needed, create a Windows icon from the existing logo before building:
- example target: `SCU_logo.ico`

### Windows build command
Important PyInstaller difference:
- Windows uses `;` in `--add-data`
- macOS uses `:`

Fastest option on Windows:
- Copy `WINDOWS BUILD/Windows_Build_Source/` to a real Windows-local folder first
- Open the copied folder in Windows
- Double-click `build_windows.bat`
- It auto-detects `py` or `python`
- It auto-installs/updates the required Python packages
- It will build the app and place the executable in `dist_win\win_SCU_CBoards\`

Manual command-line option:

```bash
cd "C:\path\to\Windows_Build_Source"
rmdir /s /q build_win
rmdir /s /q dist_win
del win_SCU_CBoards.spec
py -m PyInstaller --clean --windowed --noconfirm --name "win_SCU_CBoards" ^
  --distpath "dist_win" ^
  --workpath "build_win" ^
  --icon "SCU_logo.ico" ^
  --add-data "ClinicForms;ClinicForms" ^
  --add-data "logo.png;." ^
  --add-data "white_logo_ui.png;." ^
  win_SCU_CBoards.py
```

### Windows build output
- `dist_win\win_SCU_CBoards\win_SCU_CBoards.exe`
- Recommended shareable Windows deliverable:
  - zip the entire `dist_win\win_SCU_CBoards\` folder

### Windows end-user workflow
- Build the app once on a Windows machine.
- Give the user the packaged `dist_win\win_SCU_CBoards\` folder.
- The user can open `win_SCU_CBoards.exe` by double-clicking it.
- No terminal is needed for the end user.

### Windows testing checklist
After building on Windows, verify:
- the app opens normally
- `ClinicForms` is bundled and auto-detected
- logo assets load correctly
- paste into spreadsheet still works as expected
- shift prompt appears for left-shifted no-header pastes
- preview updates after spreadsheet edits
- generated individual PDFs and batch PDFs open correctly
- top-sheet text placement looks correct with Windows fonts/rendering

### Windows packaging notes
- Resource lookup in `SCU_CBoards.py` is already designed to work in both source and bundled environments.
- Users should still be able to override the bundled forms via **Select Forms Folder**.
- If one-file packaging is ever desired, it can be attempted later, but the current one-folder style is safer for testing resource-heavy desktop apps.

---

## Distribution Notes
- OneDrive download links for staff:
  - macOS app zip: [SCU_Clipboard_Builder.app.zip](https://mcw0.sharepoint.com/:u:/s/BOD-SCU/IQDmNDK4cdFqTb_LBHnuQsoTAbp0K__EMv3jYaU9zvMidgo?e=XMDa99)
  - Windows app zip: [win_SCU_CBoards.zip](https://mcw0.sharepoint.com/:u:/s/BOD-SCU/IQCzyF6dq97pR6HtDdEo810ZAYrZ8pyl_PX9sJBoOKHWW34?e=AZDFLy)
- macOS staff should receive the full `MAC BUILD/dist/SCU_Clipboard_Builder.app` bundle, or preferably the zipped copy `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`.
- First launch on a new Mac may require right-click -> **Open** due to Gatekeeper.
- If macOS still blocks launch, users may need to use **Privacy & Security** -> **Open Anyway**.
- Windows staff should receive the packaged `dist_win\win_SCU_CBoards\` folder, or a zip of that full folder.
- Windows staff should not run `build_windows.bat`; that script is only for creating the Windows build.
- After unzipping on Windows, staff can open `win_SCU_CBoards.exe` by double-clicking it.
- Bundled builds include forms/assets added via `--add-data`.
- Users can still override bundled forms via **Select Forms Folder**.

---

## Troubleshooting Quick Notes
- **Top sheet fields scrambled**: use latest build with improved header detection and the shift-confirmation prompt for no-header pastes.
- **Missing language form**: check fallback label in preview and verify file exists in `language`, `default`, or `english`.
- **Blurry/missing logo**: ensure `white_logo_ui.png` and `logo.png` are present and bundled.
- **Mac build conflicts**: use the documented macOS rebuild command with `--specpath "MAC BUILD/mac_build"` so the Mac spec and output stay isolated.
- **Windows build conflicts**: build only from the clean `WINDOWS BUILD/Windows_Build_Source/` copy after copying it to a real Windows-local folder.
