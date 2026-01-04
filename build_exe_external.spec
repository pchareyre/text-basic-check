"""
PyInstaller spec file for Text Correction Application - External Model Architecture.

This architecture keeps the T5 model external to the executable.
Pros: Smaller executable (~100-150 MB), easier model updates
Cons: Requires model directory alongside exe

Usage:
    pyinstaller build_exe_external.spec
"""

import sys
from pathlib import Path

# Get absolute paths
ROOT_DIR = Path.cwd()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
TEXT_CHECK_DIR = ROOT_DIR / "text_basic_check"

# Data files to include (NO MODEL)
datas = [
    # Include all backend modules
    (str(BACKEND_DIR / "app"), "backend/app"),
    
    # Include frontend modules
    (str(FRONTEND_DIR), "frontend"),
    
    # Include text_basic_check library
    (str(TEXT_CHECK_DIR), "text_basic_check"),
    
    # Note: T5 model directory NOT included - must be in same directory as exe
]

# Hidden imports (modules not automatically detected)
hiddenimports = [
    'backend.app.main',
    'backend.app.config',
    'backend.app.models',
    'backend.app.routers.health',
    'backend.app.routers.files',
    'backend.app.services.correction',
    'backend.app.services.storage',
    'frontend.app',
    'frontend.config',
    'frontend.components.sidebar',
    'frontend.components.upload',
    'frontend.utils.api_client',
    'text_basic_check',
    'text_basic_check.spell_checker',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'streamlit',
    'streamlit.web.cli',
    'symspellpy',
    'transformers',
    'optimum',
    'optimum.onnxruntime',
    'onnxruntime',
    'sentencepiece',
    'tokenizers',
    'pydantic',
    'pydantic_settings',
    'fastapi',
    'fastapi.responses',
    'fastapi.middleware',
    'fastapi.middleware.cors',
]

# Analysis
a = Analysis(
    ['launcher.py'],  # Entry point script
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ (Python archive)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None
)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TextCorrectionApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Show console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)

# COLLECT (create directory with exe and dependencies)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TextCorrectionApp_External',
)
