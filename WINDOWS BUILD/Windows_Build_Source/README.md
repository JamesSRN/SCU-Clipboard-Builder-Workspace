# SCU Clipboard Builder

## Overview
`SCU_CBoards.py` is an offline desktop app that converts a pasted clinic schedule into patient-specific PDF clipboard packets.

Primary goals:
- Keep PHI local with no network/database dependency.
- Let staff paste directly from Sheets/Excel and verify packets quickly.
- Generate consistent, correctly ordered packets in both single and batch workflows.

## Pre-built Apps
- **Windows:** download [`win_SCU_CBoards.zip`](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/latest/download/win_SCU_CBoards.zip) from GitHub Releases, extract all, then open `win_SCU_CBoards.exe`.
- **macOS:** distributed to staff through internal OneDrive/SharePoint. Contact your team lead for the Mac app zip.

## Current Folder Layout
The workspace is organized into four long-term buckets:

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
└── top-level source/docs/assets still in active use
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
- Leading blank pasted rows are automatically removed before import.
- If pasted row 1 looks like headers, the app uses those headers immediately to align incoming values into the app’s fixed columns.
- The pasted header row is treated as mapping metadata and is not left behind as a patient row in the spreadsheet body.
- If no header row is pasted, the app falls back to built-in default headers and shows a warning asking staff to include headers.
- After a header-row paste, the app shows:
  - a `Column Check` popup saying whether recognized columns already match or were re-aligned
  - a second `Ignored Columns` popup if unsupported columns such as `SOMA` were skipped
- Any non-blank marker in optional form columns counts as selected (`x`, `need`, `fill`, etc.).
- If a true no-header paste looks shifted left by one column, the app still offers the older right-shift correction flow.
- When a visible shift is applied, the info log records only the first populated row’s moved values and target headers.
- PDF generation rebuilds patient data from the current spreadsheet automatically, so staff do not need to click **Build Patient Preview** before generating.
- Demo rows named `Al Demo` / `al demo` are excluded from preview and generated outputs.

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
Normalized language outputs:
- `english`
- `spanish`
- `mandarin`

Input normalization supports:
- multi-language cells (`Spanish, English`, `English / Arabic`, etc.)
- mixed separators (`/`, `,`, `;`, `|`, `&`, `and`)
- extra spaces and noisy text

Priority rule:
- If English appears anywhere in a multi-language value, language resolves to `english`.

Per-form path resolution order:
1. requested language folder (for example `ClinicForms/spanish/`)
2. `ClinicForms/default/`
3. `ClinicForms/english/`

Preview/source labels:
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

Accepted filename variants for a base file like `phq9.pdf`:
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
- running from source
- running from the packaged `.app`

Bundled runtime assets:
- `ClinicForms/`
- `logo.png`
- `white_logo_ui.png`

During local development, the app auto-detects forms from:
- `APP SOURCE/ClinicForms/`
- or bundled `ClinicForms/` inside packaged builds

Displayed log paths are sanitized to avoid personal path leakage.

---

## Run Locally
```bash
cd "/path/to/SCU"
eval "$(conda shell.bash hook)" && conda activate gnarnia
python SCU_CBoards.py
```

---

## Build macOS App (PyInstaller)
```bash
cd "/path/to/SCU"
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

Build artifacts:
- `MAC BUILD/dist/SCU_Clipboard_Builder.app`
- `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`
- `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`

---

## Build Windows App (PyInstaller)
Windows-specific packaging files live in:
- `WINDOWS BUILD/Windows_Build_Source/`

Recommended setup on Windows:
1. Install Python 3.10+.
2. Make sure Python is available as either `py` or `python`.
3. If building manually, install:

```bash
pip install pyside6 pypdf reportlab pandas openpyxl pyinstaller
```

Windows icon note:
- Windows expects an `.ico` file instead of `.icns`
- optional icon target: `SCU_logo.ico`

Fastest option on Windows:
- copy `WINDOWS BUILD/Windows_Build_Source/` to a real Windows-local folder
- open that copied folder in Windows
- double-click `build_windows.bat`
- it auto-detects Python
- it installs/updates required packages
- it builds into `dist_win\win_SCU_CBoards\`
- it attempts to create `dist_win\win_SCU_CBoards.zip`

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

Windows build outputs:
- `dist_win\win_SCU_CBoards\win_SCU_CBoards.exe`
- shareable zip: `dist_win\win_SCU_CBoards.zip`

Windows testing checklist:
- app opens normally
- `ClinicForms` is bundled and auto-detected
- logo assets load correctly
- paste flow works
- header popups work
- preview updates on edits
- individual and batch PDFs generate correctly
- top-sheet text placement looks correct

---

## Distribution Notes
Pre-built app zips are shared with staff through internal OneDrive/SharePoint. Contact your team lead for current download links.

macOS staff:
- download `SCU_Clipboard_Builder.app.zip`
- unzip it
- open `SCU_Clipboard_Builder.app`
- if blocked, use right-click -> **Open**
- if still blocked, use **Privacy & Security** -> **Open Anyway**

Windows staff:
- download `win_SCU_CBoards.zip`
- extract all
- open the extracted folder
- double-click `win_SCU_CBoards.exe`
- do not run `build_windows.bat`; that script is only for creating the Windows build

Users can still override bundled forms via **Select Forms Folder**.

---

## Troubleshooting Quick Notes
- **Top sheet fields scrambled**: use the latest build with header-based alignment and the no-header shift prompt fallback.
- **Missing language form**: verify the file exists in the requested language, `default`, or `english`.
- **Blurry/missing logo**: ensure `white_logo_ui.png` and `logo.png` are present and bundled.
- **Mac build conflicts**: build into `MAC BUILD/` using the documented command.
- **Windows build conflicts**: build only from a clean copied `WINDOWS BUILD/Windows_Build_Source/` folder on Windows.
