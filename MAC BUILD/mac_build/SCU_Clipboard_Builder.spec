# -*- mode: python ; coding: utf-8 -*-
import os

# Repo root: MAC BUILD/mac_build -> MAC BUILD -> SCU
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, "..", ".."))

# Packages not used by SCU_CBoards.py. Keep these out even if present in the build env.
EXCLUDES = [
    "torch",
    "torchvision",
    "torchaudio",
    "scipy",
    "matplotlib",
    "numba",
    "llvmlite",
    "pyarrow",
    "pandas",
    "openpyxl",
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
    "sklearn",
    "tensorflow",
    "cv2",
]

a = Analysis(
    [os.path.join(PROJECT_ROOT, "SCU_CBoards.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, "APP SOURCE", "ClinicForms"), "ClinicForms"),
        (os.path.join(PROJECT_ROOT, "logo.png"), "."),
        (os.path.join(PROJECT_ROOT, "white_logo_ui.png"), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SCU_Clipboard_Builder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[os.path.join(PROJECT_ROOT, "SCU_logo.icns")],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SCU_Clipboard_Builder",
)
app = BUNDLE(
    coll,
    name="SCU_Clipboard_Builder.app",
    icon=os.path.join(PROJECT_ROOT, "SCU_logo.icns"),
    bundle_identifier=None,
)
