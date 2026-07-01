# WINDOWS BUILD 💻

Looking to get started? Check out the **Windows release page** [here](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/Windows-App-2026-07-02).

---

**The Saturday Clinic** · free care for uninsured patients in Milwaukee

Are you setting up front desk today on **Windows**? You're gonna want this tool.

The **SCU Clipboard Builder** turns the patient schedule into ready-to-print clipboard packets automatically. Just copy the schedule from the **Visit Tracker** on **Box**, paste it into the app, click **Generate**, and print. Done.

New to this? Don't worry — everything you need is on the release page:

**[Start Here → Windows install instructions + download](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/Windows-App-2026-07-02)**

Scroll to **Assets** at the bottom of that page to download the zip file.

**When you paste:** include the **times** and **column headers** from the Visit Tracker — the app uses those headers to make sure the right forms go on each clipboard.

**Clinic day:** copy → paste → **Generate** (save to **OneDrive**) → print → **delete the file** once you're done! That's it, no more hunting for forms! 🖨️

On a **Mac** instead? See [`MAC BUILD/README.md`](../MAC%20BUILD/README.md).

---

<details>
<summary><strong>Quick reminder</strong> — if you already downloaded the app</summary>

1. Download **`win_SCU_CBoards.zip`** from **Assets** on the release page
2. **Extract All** in File Explorer — do not open the zip directly
3. Double-click **`win_SCU_CBoards.exe`** inside the extracted folder
4. **Expect a security pop-up — that's totally normal.** If Windows shows **"Windows protected your PC"**, click **More info** → **Run anyway**. You're not doing anything wrong.

Full step-by-step instructions and troubleshooting are on the [release page](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace/releases/tag/Windows-App-2026-07-02).

**Note:** Updates to this GitHub repo do not automatically update the app on your PC. When there is a new release, download again from the release page.

</details>

<details>
<summary><strong>Build from source</strong> — for maintainers only</summary>

Front desk staff do **not** need this section — use the release download above. Do **not** run `build_windows.bat` unless you are rebuilding the app.

Source and build script are **already on GitHub** — no Mac needed.

1. On your PC, download the repo: [SCU-Clipboard-Builder-Workspace](https://github.com/JamesSRN/SCU-Clipboard-Builder-Workspace) → **Code** → **Download ZIP** (or `git clone` the repo)
2. Open folder: `WINDOWS BUILD\Windows_Build_Source\`
3. Double-click **`build_windows.bat`**
4. When finished, use **`win_SCU_CBoards.zip`** in `dist_win\` (extract → run `win_SCU_CBoards.exe`)

More detail: [`Windows_Build_Source/BUILD_ON_PC.md`](Windows_Build_Source/BUILD_ON_PC.md)

</details>

---

*Questions? Ask your clinic coordinator or whoever sent you this repo link. You've got this. 💚*
