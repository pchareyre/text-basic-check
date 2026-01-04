@echo off
REM Build script for Windows executable - External Model Architecture
REM This keeps the T5 model external to the executable

echo ======================================
echo Building Windows Executable
echo Architecture: EXTERNAL MODEL
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

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist\TextCorrectionApp_External" rmdir /s /q dist\TextCorrectionApp_External

REM Build executable
echo Building executable with PyInstaller...
echo This may take several minutes...
echo.
pyinstaller build_exe_external.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Copy model directory if it exists
if exist "t5-small-onnx-q" (
    echo.
    echo Copying T5 model to distribution...
    xcopy /E /I /Y "t5-small-onnx-q" "dist\TextCorrectionApp_External\t5-small-onnx-q"
    echo Done!
) else (
    echo.
    echo WARNING: T5 model not found at t5-small-onnx-q/
    echo.
    echo The executable will work but T5 grammar correction will not be available.
    echo To enable T5 correction later:
    echo   1. Run: export_model.bat
    echo   2. Run: python quantize_t5.py
    echo   3. Copy 't5-small-onnx-q/' directory next to TextCorrectionApp.exe
    echo.
)

echo.
echo ======================================
echo Build Complete!
echo ======================================
echo.
echo Output directory: dist\TextCorrectionApp_External\
echo.
echo Files included:
echo   - TextCorrectionApp.exe  (Main executable)
echo   - Dependencies           (DLLs and libraries)
if exist "dist\TextCorrectionApp_External\t5-small-onnx-q" (
    echo   - t5-small-onnx-q/       (T5 model - EXTERNAL)
) else (
    echo   - t5-small-onnx-q/       (NOT INCLUDED - add later)
)
echo.

REM Calculate size
for /f "tokens=3" %%a in ('dir "dist\TextCorrectionApp_External" /s /-c ^| find "bytes"') do set SIZE=%%a
set /a SIZE_MB=%SIZE% / 1048576
echo Total size: ~%SIZE_MB% MB
echo.

echo To distribute:
echo   1. Zip the entire 'dist\TextCorrectionApp_External\' directory
echo   2. Users extract and run TextCorrectionApp.exe
echo   3. Model can be updated by replacing t5-small-onnx-q/ directory
echo.
echo To test:
echo   cd dist\TextCorrectionApp_External
echo   TextCorrectionApp.exe
echo.
pause
