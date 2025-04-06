# -*- mode: python ; coding: utf-8 -*-

import glob
import os

datas = []

# Add all images
for f in glob.glob("images/**/*", recursive=True):
    if os.path.isfile(f):
        relative_path = os.path.relpath(f, "images")
        datas.append((f, os.path.join("images", os.path.dirname(relative_path))))

# Add all fonts
for f in glob.glob("fonts/**/*", recursive=True):
    if os.path.isfile(f):
        relative_path = os.path.relpath(f, "fonts")
        datas.append((f, os.path.join("fonts", os.path.dirname(relative_path))))

# Add all theme files
for f in glob.glob("theme/**/*", recursive=True):
    if os.path.isfile(f):
        relative_path = os.path.relpath(f, "theme")
        datas.append((f, os.path.join("theme", os.path.dirname(relative_path))))

import stable_baselines3
version_path = os.path.join(os.path.dirname(stable_baselines3.__file__), 'version.txt')
datas.append((version_path, 'stable_baselines3'))

datas.append(('ppo_model.zip', 'models'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
