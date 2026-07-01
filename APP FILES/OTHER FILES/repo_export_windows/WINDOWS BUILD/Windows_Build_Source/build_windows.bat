@echo off
setlocal

cd /d "%~dp0"

set "APP_NAME=win_SCU_CBoards"
set "BUILD_DIR=build_win"
set "DIST_DIR=dist_win"
set "SPEC_FILE=%APP_NAME%.spec"
set "APP_ENTRY=win_SCU_CBoards.py"
set "APP_SOURCE=SCU_CBoards.py"
set "APP_FOLDER=%DIST_DIR%\%APP_NAME%"
set "ZIP_FILE=%DIST_DIR%\%APP_NAME%.zip"

echo ============================================
echo Building SCU Clipboard Builder for Windows
echo ============================================
echo.

if not exist "%APP_SOURCE%" (
    echo Missing required file: %APP_SOURCE%
    echo Make sure you are running this batch file from the copied Windows_Build_Source folder.
    echo.
    pause
    exit /b 1
)

if not exist "%APP_ENTRY%" (
    echo Missing required file: %APP_ENTRY%
    echo Make sure you are running this batch file from the copied Windows_Build_Source folder.
    echo.
    pause
    exit /b 1
)

if not exist "ClinicForms" (
    echo Missing required folder: ClinicForms
    echo Make sure the full Windows_Build_Source contents were copied over.
    echo.
    pause
    exit /b 1
)

if not exist "logo.png" (
    echo Missing required file: logo.png
    echo.
    pause
    exit /b 1
)

if not exist "white_logo_ui.png" (
    echo Missing required file: white_logo_ui.png
    echo.
    pause
    exit /b 1
)

set "PY_CMD="

where py >nul 2>nul
if not errorlevel 1 set "PY_CMD=py"

if not defined PY_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo Python was not found on this Windows machine.
    echo.
    echo Please install Python 3.10+ from python.org and check:
    echo   Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo Using Python launcher: %PY_CMD%
echo.
echo Installing/updating build dependencies...
%PY_CMD% -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo Failed while upgrading pip.
    pause
    exit /b 1
)

%PY_CMD% -m pip install pyinstaller pyside6 pypdf reportlab pandas openpyxl
if errorlevel 1 (
    echo.
    echo Failed while installing required Python packages.
    pause
    exit /b 1
)

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%SPEC_FILE%" del /q "%SPEC_FILE%"

set ICON_ARG=
if exist "SCU_logo.ico" (
    set ICON_ARG=--icon "SCU_logo.ico"
) else (
    echo No SCU_logo.ico found. Building without a custom Windows icon.
)

echo.
echo Building executable...
%PY_CMD% -m PyInstaller --clean --noconfirm --windowed --name "%APP_NAME%" --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%" --specpath . --paths "%CD%" %ICON_ARG% --add-data "ClinicForms;ClinicForms" --add-data "logo.png;." --add-data "white_logo_ui.png;." "%APP_ENTRY%"

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

where powershell >nul 2>nul
if not errorlevel 1 (
    if exist "%ZIP_FILE%" del /q "%ZIP_FILE%"
    echo.
    echo Creating shareable zip...
    powershell -NoProfile -Command "Compress-Archive -Path '%APP_FOLDER%' -DestinationPath '%ZIP_FILE%' -Force"
)

echo.
echo Build complete.
echo End users can open:
echo   %APP_FOLDER%\%APP_NAME%.exe
if exist "%ZIP_FILE%" (
    echo.
    echo Shareable zip created:
    echo   %ZIP_FILE%
)
echo.
pause
