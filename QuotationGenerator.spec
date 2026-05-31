# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [
    ('templates', 'templates'), 
    ('logo.ico', '.'),
    ('logo.jpeg', '.')
]
binaries = []
hiddenimports = [
    'PIL.ImageTk', 'PIL.Image', 'openpyxl', 'qrcode', 'invoice', 'commercial', 
    'delivery_challan', 'generator', 'analytics', 'scrapper', 'whatsapp_bot', 
    'ui_styles', 'dashboard', 'theme_manager', 'models', 'insta_scraper',
    'config', 'invoice_selector', 'commercial_selector', 'delivery_selector',
    'pywinstyles', 'pyodbc', 'pandas', 'matplotlib', 'smtplib', 'ssl',
    'sqlite3', 'json', 'copy', 'tempfile', 'threading'
]

# Collecting heavy packages
for pkg in ['ttkbootstrap', 'reportlab', 'docx', 'matplotlib', 'pandas', 'pywinstyles']:
    try:
        tmp_ret = collect_all(pkg)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception:
        pass

a = Analysis(
    ['src/quotation.py'],
    pathex=['src', 'src/components', 'src/features', 'src/themes', 'src/models', 'src/utils'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='QuotationGenerator',
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
    icon=['logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QuotationGenerator',
)
