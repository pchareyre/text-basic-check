@echo off
REM Build script for Windows executable - Embedded Model Architecture
REM This includes the T5 model inside the executable distribution

echo ======================================
echo Building Windows Executable
echo Architecture: EMBEDDED MODEL
echo ======================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller not installed
    echo Installing PyInstaller...
    pip install -r requirements_exe.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if model exists
if not exist "t5-small-onnx-q" (
    echo WARNING: T5 model not found at t5-small-onnx-q/
    echo.
    echo The application will work but T5 grammar correction will not be available.
    echo To enable T5 correction:
    echo   1. Run: export_model.bat
    echo   2. Run: python quantize_t5.py
    echo.
    set /p continue="Continue building without T5 model? (y/n): "
    if /i not "%continue%"=="y" exit /b 0
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist\TextCorrectionApp_Embedded" rmdir /s /q dist\TextCorrectionApp_Embedded

REM Build executable
echo Building executable with PyInstaller...
echo This may take several minutes...
echo.
pyinstaller build_exe_embedded.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ======================================
echo Build Complete!
echo ======================================
echo.
echo Output directory: dist\TextCorrectionApp_Embedded\
echo.
echo Files included:
echo   - TextCorrectionApp.exe  (Main executable)
echo   - Dependencies           (DLLs and libraries)
echo   - t5-small-onnx-q/       (T5 model - EMBEDDED)
echo.

REM Calculate size
for /f "tokens=3" %%a in ('dir "dist\TextCorrectionApp_Embedded" /s /-c ^| find "bytes"') do set SIZE=%%a
set /a SIZE_MB=%SIZE% / 1048576
echo Total size: ~%SIZE_MB% MB
echo.

echo To distribute:
echo   1. Zip the entire 'dist\TextCorrectionApp_Embedded\' directory
echo   2. Users extract and run TextCorrectionApp.exe
echo.
echo To test:
echo   cd dist\TextCorrectionApp_Embedded
echo   TextCorrectionApp.exe
echo.
pause
