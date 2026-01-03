@echo off
REM Export T5-small model to ONNX format
REM This script must be run on a machine with internet access

echo ======================================
echo Exporting T5-small to ONNX format
echo ======================================
echo.

REM Check if optimum-cli is installed
where optimum-cli >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: optimum-cli not found
    echo Please install: pip install optimum[onnxruntime]
    pause
    exit /b 1
)

REM Export T5-small to ONNX
echo Exporting T5-small model...
echo This will download the model from Hugging Face (requires internet)
echo.

optimum-cli export onnx --model t5-small --task text2text-generation --output onnx-t5-small

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Done! Export successful
    echo.
    echo Output directory: onnx-t5-small\
    echo Files created:
    echo   - encoder_model.onnx
    echo   - decoder_model.onnx
    echo   - decoder_with_past_model.onnx
    echo   - tokenizer files (spiece.model, config.json, etc.^)
    echo.
    echo Next step: Quantize the models
    echo   python quantize_t5.py
) else (
    echo.
    echo ERROR: Export failed
    pause
    exit /b 1
)

pause
