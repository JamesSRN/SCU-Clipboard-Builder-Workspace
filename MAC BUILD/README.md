# MAC BUILD 🍎

Looking to get started? Check out the **Mac release page** [here](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01).

---

**The Saturday Clinic** · free care for uninsured patients in Milwaukee

Are you setting up front desk today on a **Mac**? You're gonna want this tool.

The **SCU Clipboard Builder** turns the patient schedule into ready-to-print clipboard packets automatically. Just copy the schedule from the **Visit Tracker** on **Box**, paste it into the app, click **Generate**, and print. Done. ✨

New to this? Don't worry — everything you need is on the release page:

**[Start Here → Mac install instructions + download](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01)**

Scroll to **Assets** at the bottom of that page to download the zip file.

**When you paste:** include the **times** and **column headers** from the Visit Tracker — the app uses those headers to make sure the right forms go on each clipboard. 📌

On **Windows** instead? See [`WINDOWS BUILD/README.md`](../WINDOWS%20BUILD/README.md).

---

<details>
<summary><strong>Quick reminder</strong> — if you already downloaded the app</summary>

1. Download **`SCU_Clipboard_Builder.app.zip`** from **Assets** on the release page
2. Unzip it
3. Open **`SCU_Clipboard_Builder.app`**
4. If macOS blocks the app: **right-click** → **Open** → **Open** again (or **Open Anyway** in Privacy & Security)

Full step-by-step instructions and troubleshooting are on the [release page](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/macos-app-2026-07-01).

**Note:** Updates to this GitHub repo do not automatically update the app on your Mac. When there is a new release, download again from the release page.

</details>

<details>
<summary><strong>Build from source 🛠️</strong> — for maintainers only</summary>

Front desk staff do **not** need this section — use the release download above.

Use a **dedicated minimal Python environment** for Mac builds. Do not use a general-purpose conda env (for example one with torch/scipy installed) or PyInstaller will bundle hundreds of MB of unused libraries.

**PyInstaller spec file:** `MAC BUILD/mac_build/SCU_Clipboard_Builder.spec`

**Build dependencies:** `MAC BUILD/mac_build/requirements-build.txt`

**Build command** (from repo root):

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

**Expected app size** after a clean build: roughly **120–180 MB** unzipped (vs ~740 MB when built from a bloated conda env).

**Build outputs** (`MAC BUILD/build/`, `MAC BUILD/dist/`) stay local and are not committed because of size.

**Local copy** (for maintainers): `MAC BUILD/dist/SCU_Clipboard_Builder.app.zip`

</details>

---

*Questions? Ask your clinic coordinator or whoever sent you this repo link. You've got this. 💚*
