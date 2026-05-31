import os
import sys

# Resolve base directory
if getattr(sys, 'frozen', False):
    # Frozen PyInstaller executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Development environment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(script_dir) == 'src':
        base_dir = os.path.dirname(script_dir)
    else:
        base_dir = script_dir

# Add base directory to sys.path so that absolute 'src.' package imports work at runtime
if base_dir not in sys.path:
    sys.path.append(base_dir)

def get_db_path(db_name):
    """
    Resolves the absolute path to a database file.
    Supports both frozen (executable) and development environments.
    """
    import platform
    if platform.system() == 'Windows':
        db_dir = os.path.join(base_dir, "db")
    else:
        # On macOS and Linux, store the database in the user's home directory
        # to bypass Gatekeeper's read-only translocation and permission sandbox.
        home = os.path.expanduser("~")
        db_dir = os.path.join(home, ".quotation_manager", "db")

    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    return os.path.join(db_dir, db_name)

def get_appdata_dir():
    """
    Returns a cross-platform directory for storing application data/configurations.
    Falls back to the user home directory on macOS/Linux.
    """
    import platform
    if platform.system() == 'Windows':
        appdata = os.getenv('APPDATA')
        if appdata:
            return appdata
    return os.path.expanduser("~")

# 🚀 Dynamic Search Path Registration
# Appends all structured directories under src/ to sys.path so imports work perfectly
src_dir = os.path.join(base_dir, "src")
for sub in ["components", "features", "themes", "models", "utils"]:
    sub_path = os.path.join(src_dir, sub)
    if os.path.exists(sub_path) and sub_path not in sys.path:
        sys.path.append(sub_path)
