import os
import sys
import subprocess
import shutil

def log(msg, level="info"):
    colors = {
        "info": "\033[94m[INFO]\033[0m",
        "success": "\033[92m[SUCCESS]\033[0m",
        "warning": "\033[93m[WARNING]\033[0m",
        "error": "\033[91m[ERROR]\033[0m"
    }
    prefix = colors.get(level, "[INFO]")
    print(f"{prefix} {msg}")

def run_command(command, description):
    log(f"Running: {description}...", "info")
    try:
        # Use shell=True for Windows compatibility
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Failed to run: {description}", "error")
        print(f"Error stdout:\n{e.stdout}")
        print(f"Error stderr:\n{e.stderr}")
        return False

def main():
    # Enable colored output on Windows terminal
    os.system('color')
    
    log("Starting Quotation Generator Build & Installer Packaging Pipeline", "info")
    
    # 1. Check virtualenv
    venv_pyinstaller = os.path.join(".venv", "Scripts", "pyinstaller.exe")
    if not os.path.exists(venv_pyinstaller):
        log("PyInstaller was not found in .venv/Scripts/pyinstaller.exe. Trying system 'pyinstaller' command...", "warning")
        venv_pyinstaller = "pyinstaller"
        
    # 2. Clean previous builds
    log("Cleaning previous build and dist directories...", "info")
    for folder in ["build", "dist", "installer_output"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                log(f"Removed old '{folder}' folder.", "info")
            except Exception as e:
                log(f"Could not fully clear '{folder}': {e}", "warning")
                
    # 3. Build executable using PyInstaller spec file
    pyinstaller_cmd = f'"{venv_pyinstaller}" --noconfirm QuotationGenerator.spec'
    if not run_command(pyinstaller_cmd, "PyInstaller compilation"):
        log("PyInstaller compilation failed. Aborting installer creation.", "error")
        sys.exit(1)
        
    log("Successfully compiled standalone executable using PyInstaller!", "success")
    
    # 4. Locate Inno Setup Compiler (ISCC.exe)
    iscc_paths = [
        "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
        "C:\\Program Files\\Inno Setup 6\\ISCC.exe",
        "C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe",
        "C:\\Program Files\\Inno Setup 5\\ISCC.exe",
    ]
    
    iscc_path = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_path = path
            break
            
    if not iscc_path:
        # Check if ISCC is in PATH
        which_iscc = shutil.which("ISCC")
        if which_iscc:
            iscc_path = which_iscc
            
    if not iscc_path:
        log("Inno Setup Compiler (ISCC.exe) was not found in standard paths.", "error")
        log("Please install Inno Setup 6 (https://jrsoftware.org/isdownload.php) and try again.", "warning")
        sys.exit(1)
        
    log(f"Found Inno Setup Compiler at: {iscc_path}", "success")
    
    # 5. Compile Inno Setup Script
    os.makedirs("installer_output", exist_ok=True)
    inno_cmd = f'"{iscc_path}" QuotationGenerator.iss'
    if not run_command(inno_cmd, "Inno Setup packaging"):
        log("Inno Setup compilation failed.", "error")
        sys.exit(1)
        
    # Find the output installer file
    setup_file = None
    if os.path.exists("installer_output"):
        files = os.listdir("installer_output")
        for f in files:
            if f.endswith(".exe"):
                setup_file = os.path.join("installer_output", f)
                break
                
    if setup_file:
        log(f"Installer compiled successfully! Created: {setup_file}", "success")
        log(f"Size: {os.path.getsize(setup_file) / (1024*1024):.2f} MB", "info")
        print("\n" + "="*80)
        print("\033[92m[ BUILD COMPLETED SUCCESSFULLY ]\033[0m")
        print("="*80)
        print(f"Installer path: {os.path.abspath(setup_file)}")
        print("\nTo share this software:")
        print("1. Go to your GitHub repository.")
        print("2. Click on 'Releases' -> 'Draft a new release'.")
        print("3. Upload the setup .exe file found in the 'installer_output' directory.")
        print("4. Publish the release! Anyone can now download and install the software.")
        print("="*80 + "\n")
    else:
        log("Build finished, but could not locate the compiled setup executable.", "warning")

if __name__ == "__main__":
    main()
