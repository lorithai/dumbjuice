import os
import shutil
import requests
from bs4 import BeautifulSoup
import importlib
import json
import sys
import subprocess
import stat
import zipfile
import re
from packaging.version import Version, InvalidVersion

#import dumbjuice.addins as addins

base_path = os.path.dirname(__file__)
with open(os.path.join(base_path,"__version__.py"),"r") as infile:
    dj_version = infile.readline().split("=")[-1].strip()[1:-1]+".0"
print(dj_version)

ICON_NAME = "djicon.ico"
HARDCODED_IGNORES = {"dumbjuice_build","dumbjuice_dist",".gitignore",".git",".git/","*.git"}
default_config = {"gui":False,"ignore":None,"use_gitignore":False,"include":None,"addins":None,"mainfile":"main.py"}
ADDINS_LIBRARY = {"ffmpeg":{"relpath":"addins/ffmpeg/bin","installer_source":"https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"}}

def create_dist_zip(build_folder, dist_folder, zip_filename):
    os.makedirs(dist_folder, exist_ok=True)
    zip_path = os.path.join(dist_folder, zip_filename + ".zip")

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_folder):
            for file in files:
                if file == "install.nsi":
                    continue  # optionally skip the nsis script
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, build_folder)
                zipf.write(abs_path, rel_path)

    print(f"Created zip archive at: {zip_path}")

def handle_remove_readonly(func, path, exc_info):
    # Clear the read-only flag and try again
    os.chmod(path, stat.S_IWRITE)
    func(path)

def find_makensis():
    local_path = os.path.join(os.path.dirname(__file__), "bin", "nsis", "makensis.exe") 
    if os.path.isfile(local_path):
        return local_path
    raise RuntimeError("NSIS not found")

def generate_nsis_script(conf, active_addins=None,python_exe="python.exe"):
    python_version = conf['python_version'].split(".")
    py_major = python_version[0]
    py_minor = python_version[1]
    if len(python_version) == 3:
        major_minor = ".".join(python_version[:-1])
    elif len(python_version) == 2:
        major_minor = ".".join(python_version)
    else:
        raise RuntimeError(f"Invalid python version number {python_version}")
    python_version = get_latest_windows_python(major_minor)
    
    app_name = conf['program_name']
    binpath = str(importlib.resources.files('dumbjuice.bin').joinpath('').resolve())
    mainfile = conf['mainfile']
    addin_blocks = []
    for addin_name in active_addins:
        meta = ADDINS_LIBRARY[addin_name]
        zip_name = addin_name + ".zip"
        install_path = os.path.join("$INSTDIR", meta["relpath"].replace("/", "\\"))
        install_check_path = os.path.join(install_path, "*.*")

        skip_label = f"skip_addin_{addin_name}"
        
        block = f"""
        ; --- {addin_name} add-in installation ---
        IfFileExists "{install_check_path}" {skip_label}
        
        DetailPrint "Installing add-in: {addin_name}"
        inetc::get "{meta['installer_source']}" "$TEMP\\{zip_name}" /END
        Pop $0
        StrCmp $0 "OK" 0 +3
            DetailPrint "Extracting {addin_name}..."
            nsisunz::Unzip "$TEMP\\{zip_name}" "{install_path}"
            Delete "$TEMP\\{zip_name}"
        
        {skip_label}:
        """
        addin_blocks.append(block)
    addins_scripts = "\n".join(addin_blocks)

    script = f"""
# -*- coding: utf-8 -*-
!addplugindir "{binpath}"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

VIProductVersion "{dj_version}"
VIFileVersion "1.0.0.0"
VIAddVersionKey /LANG=1033 "CompanyName" "Larks Wombat Systems"
VIAddVersionKey /LANG=1033 "FileDescription" "DumbJuice Installer"
VIAddVersionKey /LANG=1033 "LegalCopyright" "2025 Larks Wombat Systems"
VIAddVersionKey /LANG=1033 "ProductName" "DumbJuice"
VIAddVersionKey /LANG=1033 "ProductVersion" "{dj_version}"
VIAddVersionKey /LANG=1033 "FileVersion" "1.0.0.0"

; Static variables (requires curly brackets, double in this case)
!define PYENV_DIR "$PROFILE\\.pyenv\\pyenv-win"
!define PYENV_REPO "https://github.com/pyenv-win/pyenv-win/archive/refs/heads/master.zip"
!define DJ_INSTALL_DIR "$PROFILE\\.dumbjuice"

; Runtime variables (doesn't need curly brackets)
var DJ_PYTHON_DIR
var DJ_APP_DIR

Name "Dumbjuice installer for {app_name}"
OutFile "install.exe"
InstallDir "${{DJ_INSTALL_DIR}}" ; becomes INSTDIR
RequestExecutionLevel admin

; UI elements 
; Page directory
Page instfiles

Section "Install {app_name}"

  ; Define paths
  StrCpy $DJ_PYTHON_DIR "$INSTDIR\\python\\{python_version}"
  StrCpy $DJ_APP_DIR "$INSTDIR\\programs\\{app_name}"

  ; Create folders
  CreateDirectory $DJ_APP_DIR

  ; Set output to app folder
  SetOutPath $DJ_APP_DIR

  ; Copy all app files
  File /r "appfolder\\*.*"
  
  ; --- Check for Python ---
  ; 1. Check Python version is in DumbJuice
  IfFileExists "$DJ_PYTHON_DIR\\python.exe" Install_venv

; Check if pyenv-win exists
IfFileExists "${{PYENV_DIR}}\\bin\\pyenv.bat" Install_python

  ; Install pyenv-win
  DetailPrint "Downloading pyenv-win..."
  inetc::get /CAPTION "Downloading pyenv-win..." /RESUME "" "${{PYENV_REPO}}" "$TEMP\\pyenv-win.zip" /END
  Pop $0
  StrCmp $0 "OK" +2
    Abort "Failed to download pyenv-win"

  ; Extract pyenv-win
  nsisunz::Unzip "$TEMP\\pyenv-win.zip" "$TEMP\\pyenv-win"
  
  CreateDirectory "$PROFILE\\.pyenv"
  ; Move the pyenv-win folder
  Rename "$TEMP\\pyenv-win\\pyenv-win-master\\pyenv-win" "$PROFILE\\.pyenv\\pyenv-win"
  
  ; Copy the .version file (pyenv doesn't work without this)
  CopyFiles /SILENT "$TEMP\\pyenv-win\\pyenv-win-master\\.version" "$PROFILE\\.pyenv\\"


Install_python:
  DetailPrint "Checking Python {python_version} in pyenv..."
  nsExec::Exec '"$PROFILE\\.pyenv\\pyenv-win\\bin\\pyenv.bat" versions | findstr {python_version}'

  Pop $0
  StrCmp $0 "0" Move_pyenv_python

  DetailPrint "Installing Python {python_version} via pyenv..."
  nsExec::ExecToLog '"$PROFILE\\.pyenv\\pyenv-win\\bin\\pyenv.bat" install {python_version}'

Move_pyenv_python:
  DetailPrint "Copying Python {python_version} to DumbJuice..."
  CopyFiles /SILENT "$PROFILE\\.pyenv\\pyenv-win\\versions\\{python_version}\\*.*" "$INSTDIR\\python\\{python_version}"

Install_venv:

  ; --- Create virtual environment ---
  DetailPrint "Creating virtual environment..."
  ExecWait '"$DJ_PYTHON_DIR\\python.exe" -m venv "$DJ_APP_DIR\\venv"'

  ; --- Install requirements ---
  DetailPrint "Installing dependencies..."
  ExecWait '"$DJ_APP_DIR\\venv\\Scripts\\pip.exe" install -r "$DJ_APP_DIR\\requirements.txt"'

  ; Install addins
  {addins_scripts}

  ; Create shortcut on desktop
  DetailPrint "Creating desktop shortcut..."
  CreateShortCut "$DESKTOP\\{app_name}.lnk" "$DJ_APP_DIR\\venv\\Scripts\\{python_exe}" '"$DJ_APP_DIR\\{mainfile}"' "$INSTDIR\\programs\\{app_name}\\djicon.ico"
  DetailPrint "Creating debug shortcut..."
  CreateShortCut "$DJ_APP_DIR\\{app_name}_debug.lnk" "$DJ_APP_DIR\\venv\\Scripts\\python.exe" '"$DJ_APP_DIR\\{mainfile}"' "$DJ_APP_DIR\\djicon.ico"
  Goto done

done:
MessageBox MB_OK "Installer finished. A shortcut for {app_name} has been created on the Desktop"
SectionEnd
"""
    return script

def load_gitignore(source_folder):
    """Load ignore patterns from .gitignore if it exists."""
    gitignore_path = os.path.join(source_folder, ".gitignore")
    ignore_patterns = set()

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    ignore_patterns.add(line)

    return ignore_patterns

def addins_to_main(main_py_path, addin_relpaths):
    """
    add-in PATH patching code into the top of the main.py file.
    Uses namespaced variables to prevent naming conflicts.
    
    Args:
        main_py_path (str): Full path to main.py (or other entrypoint).
        addin_relpaths (List[str]): List of relative paths to prepend to PATH.
    """
    start_marker = "# >>> dumbjuice addins >>>"
    end_marker = "# <<< dumbjuice addins <<<"

    # Generate the code block with namespaced variables (Clumsy attempt at such)
    lines = [start_marker]
    lines.append("import os")
    lines.append("import sys")
    lines.append("")
    lines.append(f"_dj_addin_relpaths = {repr(addin_relpaths)}")
    lines.append("_dj_base_path = os.path.dirname(sys.argv[0])")
    lines.append("for _dj_rel in _dj_addin_relpaths:")
    lines.append("    _dj_abs_path = os.path.abspath(os.path.join(_dj_base_path, _dj_rel))")
    lines.append("    if _dj_abs_path not in os.environ['PATH']:")
    lines.append("        os.environ['PATH'] = _dj_abs_path + os.pathsep + os.environ['PATH']")
    lines.append(end_marker)
    added_block = "\n".join(lines) + "\n\n"

    # Read the original content
    with open(main_py_path, "r", encoding="utf-8") as f:
        original = f.read()

    # Remove any previous added block
    if start_marker in original and end_marker in original:
        pre = original.split(start_marker)[0]
        post = original.split(end_marker)[-1]
        cleaned = pre.strip() + "\n\n" + post.lstrip()
    else:
        cleaned = original

    # Write the new file with addin at the top
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(added_block + cleaned)

    print(f"[dumbjuice] Added addin paths into {main_py_path}")

def get_default_icon():
    f"""Returns the path to the default {ICON_NAME} file."""
    return str(importlib.resources.files('dumbjuice.assets') / ICON_NAME) # / joins the paths


def get_latest_windows_python(major_minor: str, kind="exe") -> str:
    """
    Find latest available Windows Python release for given major.minor.
    kind = "exe" (full installer) or "embed" (embeddable zip).
    Returns version string like "3.11.9".
    """
    base_url = "https://www.python.org/ftp/python/"
    resp = requests.get(base_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # collect versions matching major.minor.patch/
    versions = []
    for a in soup.find_all("a", href=True):
        m = re.match(rf"^{re.escape(major_minor)}\.(\d+)/$", a["href"])
        if m:
            versions.append(int(m.group(1)))

    versions.sort(reverse=True)  # newest first

    for patch in versions:
        v = f"{major_minor}.{patch}"
        dir_url = f"{base_url}{v}/"
        r = requests.get(dir_url)
        r.raise_for_status()
        files = r.text

        if kind == "exe" and f"python-{v}-amd64.exe" in files:
            return v
        if kind == "embed" and f"python-{v}-embed-amd64.zip" in files:
            return v

    raise RuntimeError(f"No Windows {kind} installer found for {major_minor}")


def is_python_version_available(python_version):
    url = f"https://www.python.org/ftp/python/{python_version}/"
    response = requests.get(url)
    # If the version page exists, the status code will be 200
    if response.status_code == 200:
        return True
    else:
        return False

def build(target_folder=None):
    if target_folder is None:
        target_folder = os.getcwd()

    config_path = os.path.join(target_folder,"dumbjuice.conf")

    print("DumbJuice in:",target_folder)
    try:
        with open(config_path, "r") as f:
            loaded_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Invalid or missing dumbjuice.conf file.")
        sys.exit(1)
    required_keys = ["program_name", "python_version"]
    missing_keys = [key for key in required_keys if key not in loaded_config or not loaded_config[key]]
    if missing_keys:
        print(f"Error: Missing or empty required config values: {', '.join(missing_keys)}")
        sys.exit(1)  # Exit the script if critical settings are missing

    config = default_config.copy()
    config.update(loaded_config)
    python_version = config["python_version"]
    print("Using combined config with defaults:")
    print(config)
    if "gui" in config:
        gui = config["gui"]
    else:
        gui = False

    if gui:
        python_executable = "pythonw.exe"
    else:
        python_executable = "python.exe"

    # Check if the specified Python version is available
    if not is_python_version_available(python_version):
        print(f"Error: Python version {python_version} is not available for download.")
        return  # Exit the function to stop further processing
    
    build_folder = os.path.join(os.getcwd(), "dumbjuice_build")
    dist_folder = os.path.join(os.getcwd(), "dumbjuice_dist")
    zip_filename = config["program_name"]
    source_folder = target_folder
    # Ensure build folder exists

    if os.path.exists(build_folder):
        try:
            shutil.rmtree(build_folder, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Could not delete existing build folder: {e}")
            print("Make sure the files (especially install.exe) are not open or locked.")
            sys.exit(1)

    os.makedirs(build_folder)

    # Copy appfolder contents to the build folder
    appfolder = os.path.join(build_folder, 'appfolder')
    #print(appfolder)
    if not os.path.exists(appfolder):
        os.makedirs(appfolder)

    # Copy contents of the user's appfolder into the new appfolder
    excluded_files = set()
    if config["use_gitignore"]:
        excluded_files = excluded_files | load_gitignore(target_folder)
    # add custom files to ignore set
    if config["ignore"] is not None:
        excluded_files = excluded_files | set(config["ignore"])

    excluded_files = excluded_files | HARDCODED_IGNORES # some hardcoded ones to ensure the build folders aren't added recursively 
    if config["include"] is not None:
        excluded_files.difference_update(set(config["include"]))
    excluded_files = {item.rstrip('/') for item in excluded_files} # not sure why, but the .gitignore items with a trailing / is not identified by ignore_patterns, maybe not, dunno, but this way works so meh
    shutil.copytree(source_folder, appfolder, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*excluded_files))

    # get the defult icon if there isn't one available
    if not os.path.isfile(os.path.join(appfolder,ICON_NAME)):
        shutil.copyfile(get_default_icon(),os.path.join(appfolder,ICON_NAME))

    active_addins = {}
    if "addins" in config:
        active_addin_relpaths = []
        for addin_name in config["addins"]:
            if addin_name in ADDINS_LIBRARY:
                active_addins[addin_name] = ADDINS_LIBRARY[addin_name]["relpath"]
                active_addin_relpaths.append(ADDINS_LIBRARY[addin_name]["relpath"])
            else:
                print(f"addin '{addin_name}' is not supported. Available are {list(ADDINS_LIBRARY.keys())}")

    if len(active_addin_relpaths) > 0:
        addins_to_main(os.path.join(appfolder,config["mainfile"]), active_addin_relpaths)
    else:
        active_addin_relpaths = None

    script = generate_nsis_script(config, active_addins,python_executable)     
    nsis_file = os.path.join(build_folder,"installer.nsi")
    makensis_path = importlib.resources.files('dumbjuice.bin') / 'nsis' / 'makensis.exe'
    with open(nsis_file ,"w") as outfile:
        outfile.write(script)

    try:
        result = subprocess.run(
            [makensis_path, nsis_file],
            check=True,
            capture_output=True,
            text=True
        )
        print("NSIS build output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("NSIS build failed:\n", e.stderr)

    
    create_dist_zip(build_folder, dist_folder, zip_filename)

    

    