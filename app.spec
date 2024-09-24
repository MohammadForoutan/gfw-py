# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],  # Main script
    pathex=[],  # Additional paths, if needed
    binaries=[],  # External binaries (we'll add ffmpeg later)
    datas=[('ffmpeg/ffmpeg.exe', 'ffmpeg')],  # Add ffmpeg to the bundle
    hiddenimports=[],  # Any hidden imports can be added here
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],  # Modules to exclude
    noarchive=False,
)

# Build a .pyz archive of all the pure Python files
pyz = PYZ(a.pure)

# Bundle the .pyz with binaries, scripts, and any additional files
exe = EXE(
    pyz,
    a.scripts,  # Scripts to be included
    a.binaries,  # External binaries like ffmpeg
    a.datas,  # Data files like ffmpeg.exe
    [],
    name='app',  # Name of the final executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
	noarchive=True,
    upx=True,  # Use UPX to compress the executable (optional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False if you don't want a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,  # Bundle everything into one .exe file
)
