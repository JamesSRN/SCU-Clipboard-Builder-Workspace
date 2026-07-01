# SCU Clipboard Builder 📋

**The Saturday Clinic** · free care for uninsured patients in Milwaukee · built to make clinic morning easier

---

## Hey Front Desk 👋 — start here

Are you setting up front desk today? You're gonna want this tool.

The **SCU Clipboard Builder** turns the patient schedule into ready-to-print clipboard packets automatically. Just copy the schedule from the **Visit Tracker** on **Box**, paste it into the app, click **Generate**, and print. Done. ✨

**Tip:** include the **times** and **column headers** when you copy — the app uses those headers to make sure the right forms go on each clipboard. 📌

New to this? Don't worry — everything you need to get started can be found right here!

| | |
|---|---|
| 🍎 **Mac** | [Start Here](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01) |
| 💻 **Windows** | [Start Here](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/Windows-App-2026-07-02) |

Each link opens a **release page** with step-by-step instructions. Scroll to **Assets** at the bottom to download the zip file.

More detail: [`MAC BUILD/README.md`](MAC%20BUILD/README.md) · [`WINDOWS BUILD/README.md`](WINDOWS%20BUILD/README.md) · [All releases](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases)

---

## What this app does (30-second version)

- 📋 **Paste the schedule** from the Visit Tracker on Box — include **times** and **column headers** (the app uses headers to match the right forms to each patient)
- 👀 **Preview each patient** — see which forms will land on their clipboard
- 📁 **Generate PDFs in one batch** — consistent order, correct language, every time
- 🔒 **Works offline** — no cloud upload, no database; patient info stays on your machine until you save PDFs

That’s the whole vibe: less manual form hunting, more time for patients.

---

## Privacy 🔒

We take this seriously at a free clinic:

- No network APIs — the app doesn’t phone home
- Patient data lives in memory for the current session only
- **Clear Session (Privacy)** wipes parsed data and preview state when you’re done
- PDF output only goes where *you* choose to save it

---

<details>
<summary><strong>What’s in this repo 🗂️</strong> — for curious folks &amp; maintainers</summary>

This GitHub repo is the **workspace** — source code, clinic forms, and build scripts for people who maintain the app. Front desk staff use the **release downloads** above, not this folder directly.

```text
SCU/
├── APP SOURCE/          ← live app code + ClinicForms PDFs
├── MAC BUILD/           ← Mac packaging (PyInstaller)
├── WINDOWS BUILD/       ← Windows packaging + build_windows.bat
├── OTHER FILES/         ← older reference / debug material
└── SCU_CBoards.py       ← main app entry point
```

**Practical intent:**

- Source code and live forms stay tied to the main project
- Mac build outputs live under `MAC BUILD/`
- Windows build source/output lives under `WINDOWS BUILD/`
- Older/debug/reference material lives under `OTHER FILES/`

</details>

---

<details>
<summary><strong>Developer reference 🛠️</strong> — how the app works under the hood</summary>

Everything in this section is for maintainers, builders, and curious volunteers who want the full picture.

<details>
<summary><strong>Main script</strong></summary>

- **Entry point:** `SCU_CBoards.py`
- **Core classes:**
  - `PDFProcessor` — form path resolution, top-sheet personalization, PDF merge
  - `ClinicApp` — Qt UI, spreadsheet paste/edit, patient parsing, preview, output actions

</details>

<details>
<summary><strong>Input workflow</strong> — paste, parse, preview</summary>

On clinic day, the Front Desk Manager copies the patient schedule from the **Visit Tracker** on **Box** and pastes it into the app.

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

**Parsing behavior:**

- Paste directly from clipboard (tab/newline grid)
- Staff can edit cells directly in the grid after paste
- The patient preview auto-refreshes when spreadsheet cells are edited
- Leading blank pasted rows are automatically removed before import
- If pasted row 1 looks like headers, the app uses those headers immediately to align incoming values into the app’s fixed columns
- The pasted header row is treated as mapping metadata and is not left behind as a patient row in the spreadsheet body
- If no header row is pasted, the app falls back to built-in default headers and shows a warning asking staff to include headers
- After a header-row paste, the app shows:
  - a `Column Check` popup saying whether recognized columns already match or were re-aligned
  - a second `Ignored Columns` popup if unsupported columns such as `SOMA` were skipped
- Any non-blank marker in optional form columns counts as selected (`x`, `need`, `fill`, etc.)
- If a true no-header paste looks shifted left by one column, the app still offers the older right-shift correction flow
- When a visible shift is applied, the info log records only the first populated row’s moved values and target headers
- PDF generation rebuilds patient data from the current spreadsheet automatically, so staff do not need to click **Build Patient Preview** before generating
- Demo rows named `Al Demo` / `al demo` are excluded from preview and generated outputs

</details>

<details>
<summary><strong>Top sheet personalization</strong></summary>

Top sheet template filename: `top_sheet.pdf`

**Filled fields:** Patient Name · Date of Birth · Room Number · Language

**Implementation details:**

- Field rectangles are read from top-sheet widgets
- Values are drawn as static overlay text into those rectangles
- Text is auto-sized to fit each field box
- A compact **Included Forms** list is rendered under DOB
- Each listed form includes its resolved language/source label, such as:
  - `medical_consent (spanish)`
  - `initial_visit_intake (mandarin)`
  - `vitals_sheet (fallback english)`
  - `patient_synopsis (default fallback)`

**Why this approach:** avoids interactive AcroForm batch merge issues; produces stable, readable output per patient in batch mode.

</details>

<details>
<summary><strong>Packet composition and order</strong></summary>

**Required forms** (always included):

- `medical_consent.pdf`
- `vitals_sheet.pdf`
- `patient_synopsis.pdf`
- `post_visit_instructions.pdf`

**Optional forms** (from schedule marks):

- `initial_visit_intake.pdf`
- `annual_demographics.pdf`
- `caremessage_consent.pdf`
- `specialty_clinic_consent.pdf`
- `phq9.pdf`
- `gad7.pdf`
- `tb_form.pdf`
- `welcome_packet.pdf`

**Canonical order:**

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

</details>

<details>
<summary><strong>Language handling and fallbacks</strong></summary>

**Normalized language outputs:** `english` · `spanish` · `mandarin`

**Input normalization supports:**

- multi-language cells (`Spanish, English`, `English / Arabic`, etc.)
- mixed separators (`/`, `,`, `;`, `|`, `&`, `and`)
- extra spaces and noisy text

**Priority rule:** if English appears anywhere in a multi-language value, language resolves to `english`.

**Per-form path resolution order:**

1. requested language folder (for example `ClinicForms/spanish/`)
2. `ClinicForms/default/`
3. `ClinicForms/english/`

**Preview/source labels:** `(english)`, `(spanish)`, `(mandarin)`, `(default fallback)`, `(fallback english)`, `(missing)`

</details>

<details>
<summary><strong>Form folder layout + naming</strong></summary>

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

</details>

<details>
<summary><strong>UI / branding</strong></summary>

- Window title: **SCU Clipboard Builder**
- Dark emerald/hunter-green theme accents
- Orange title text
- Top-right header logo (UI asset prioritizes `white_logo_ui.png`)
- App icon: `SCU_logo.icns`
- Patient name rows in preview highlighted orange

</details>

<details>
<summary><strong>Resource loading</strong> — dev vs bundled app</summary>

Resource discovery supports running from source or from the packaged `.app` / `.exe`.

**Bundled runtime assets:** `ClinicForms/` · `logo.png` · `white_logo_ui.png`

During local development, the app auto-detects forms from `APP SOURCE/ClinicForms/` or bundled `ClinicForms/` inside packaged builds.

Displayed log paths are sanitized to avoid personal path leakage.

</details>

<details>
<summary><strong>Run locally</strong></summary>

```bash
cd "/path/to/SCU"
python3 SCU_CBoards.py
```

Use a venv with `pyside6`, `pypdf`, `reportlab`, and `pillow` installed — see `MAC BUILD/mac_build/requirements-build.txt`.

</details>

<details>
<summary><strong>Build macOS app</strong> (PyInstaller)</summary>

Use a **dedicated minimal Python environment** — not a bloated general-purpose conda env, or the `.app` balloon to hundreds of MB.

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

**Build artifacts:**

- `MAC BUILD/dist/SCU_Clipboard_Builder.app`
- `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`
- `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`

More detail: [`MAC BUILD/README.md`](MAC%20BUILD/README.md)

</details>

<details>
<summary><strong>Build Windows app</strong> (PyInstaller)</summary>

Windows packaging lives in `WINDOWS BUILD/Windows_Build_Source/`.

**Fastest option on Windows:**

1. Clone or download this repo
2. Open `WINDOWS BUILD\Windows_Build_Source\`
3. Double-click **`build_windows.bat`**
4. Output: `dist_win\win_SCU_CBoards.zip`

**Requirements:** Python 3.10+, “Add to PATH” checked during install.

More detail: [`WINDOWS BUILD/README.md`](WINDOWS%20BUILD/README.md) · [`BUILD_ON_PC.md`](WINDOWS%20BUILD/Windows_Build_Source/BUILD_ON_PC.md)

**Manual command-line option:**

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

**Windows build outputs:**

- `dist_win\win_SCU_CBoards\win_SCU_CBoards.exe`
- shareable zip: `dist_win\win_SCU_CBoards.zip`

**Windows testing checklist:**

- [ ] App opens normally
- [ ] `ClinicForms` is bundled and auto-detected
- [ ] Logo assets load correctly
- [ ] Paste flow works
- [ ] Header popups work
- [ ] Preview updates on edits
- [ ] Individual and batch PDFs generate correctly
- [ ] Top-sheet text placement looks correct

</details>

<details>
<summary><strong>Distribution notes</strong></summary>

Front Desk Manager: open the **release page** for your computer (instructions and download are on the same page):

- **Windows:** [Windows App — July 2026](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/Windows-App-2026-07-02)
- **Mac:** [macOS App — July 2026](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01)

Staff can still override bundled forms via **Select Forms Folder** in the app.

</details>

<details>
<summary><strong>Troubleshooting quick notes 🔧</strong></summary>

| Issue | Fix |
|---|---|
| Top sheet fields scrambled | Use the latest build with header-based alignment and the no-header shift prompt fallback |
| Missing language form | Verify the file exists in the requested language, `default`, or `english` |
| Blurry/missing logo | Ensure `white_logo_ui.png` and `logo.png` are present and bundled |
| Mac build huge or conflicts | Build with the minimal venv in `MAC BUILD/` — see Build macOS app above |
| Windows build conflicts | Build only from a clean copy of `WINDOWS BUILD/Windows_Build_Source/` on a real Windows PC |

</details>

</details>

---

*Questions? Ask your clinic coordinator or whoever sent you this repo link. You’ve got this. 💚*
