import os
import shutil
import requests
import importlib
import json
import sys
import dumbjuice.addins as addins

ICON_NAME = "djicon.ico"
HARDCODED_IGNORES = {"dumbjuice_build","dumbjuice_dist",".gitignore",".git",".git/","*.git"}
default_config = {"gui":False,"ignore":None,"use_gitignore":False,"include":None,"addins":None,"mainfile":"main.py"}
addins_environment_variable_paths = {"ffmpeg":"$ffmpegPath"}


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

def addins_PATH_import_insert():
    script = """
import json 
import os 

with open("dumbjuice.conf","r") as infile:
    djconfig = json.load(infile)

for dj_addin_path in djconfig["addin_paths"]:
    if dj_addin_path not in os.environ["PATH"]:
        if not os.environ["PATH"][-1] == ";":
            os.environ["PATH"] +=  os.pathsep + dj_addin_path + os.pathsep
        else:
            os.environ["PATH"] +=  os.pathsep + dj_addin_path

"""
    return script
def get_default_icon():
    f"""Returns the path to the default {ICON_NAME} file."""
    return str(importlib.resources.files('dumbjuice.assets') / ICON_NAME) # / joins the paths

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
    program_name = config["program_name"]

    if "gui" in config:
        gui = config["gui"]
    else:
        gui = False
         
    if gui:
        python_executable = "pythonw"
    else:
        python_executable = "python"
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
        shutil.rmtree(build_folder) 
    os.makedirs(build_folder)

    # Copy appfolder contents to the build folder
    appfolder = os.path.join(build_folder, 'appfolder')
    if not os.path.exists(appfolder):
        os.makedirs(appfolder)

    # Copy contents of the user's appfolder into the new appfolder
    excluded_files = set()
    if config["use_gitignore"]:
        excluded_files = excluded_files | load_gitignore(target_folder)

    
    if config["ignore"] is not None:
        excluded_files = excluded_files | set(config["ignore"])

    excluded_files = excluded_files | HARDCODED_IGNORES
    if config["include"] is not None:
        excluded_files.difference_update(set(config["include"]))
    excluded_files = {item.rstrip('/') for item in excluded_files} # not sure why, but the .gitignore items with a trailing / is not identified by ignore_patterns, maybe not, dunno, but this way works so meh
    shutil.copytree(source_folder, appfolder, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*excluded_files))

    if not os.path.isfile(os.path.join(appfolder,ICON_NAME)):
        shutil.copyfile(get_default_icon(),os.path.join(appfolder,ICON_NAME))


    if config["addins"] is not None:
        with open(os.path.join("dumbjuice_build","appfolder",config["mainfile"]),"r",encoding="utf-8") as infile:
            original_main_content = infile.read()

        with open(os.path.join("dumbjuice_build","appfolder",config["mainfile"]),"w",encoding="utf-8") as outfile:
            outfile.write(addins_PATH_import_insert() + "\n"+ original_main_content)

    # Generate install.bat file
    install_bat_path = os.path.join(build_folder, "install.bat")
    with open(install_bat_path, "w") as bat_file:
        bat_file.write(f'''@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0appfolder\\build.ps1"
pause
''')

    # Generate build.ps1 file
    logos = """

$asciiText = @"
                                                                                                                
88888888ba,                                     88                   88               88                          
88      `"8b                                     88                   88               ""                          
88        `8b                                    88                   88                                           
88         88  88       88  88,dPYba,,adPYba,   88,dPPYba,           88  88       88  88   ,adPPYba,   ,adPPYba,  
88         88  88       88  88P'   "88"    "8a  88P'    "8a          88  88       88  88  a8"     ""  a8P_____88  
88         8P  88       88  88      88      88  88       d8          88  88       88  88  8b          8PP"""""""  
88      .a8P   "8a,   ,a88  88      88      88  88b,   ,a8"  88,   ,d88  "8a,   ,a88  88  "8a,   ,aa  "8b,   ,aa  
 88888888Y"'     `"YbbdP'Y8  88      88      88  8Y"Ybbd8"'    "Y8888P"     `"YbbdP'Y8  88   `"Ybbd8"'    `"Ybbd8"'  
                                                                                                                     
"@
$asciiLogo = @"                                                                              
                                                        #######.           
                                                      ##*:::::::###         
                                                    ##*::%#:-###-%##        
                                                   ##:::=####::-:##         
                                                  ##::###=-*##%-%#*         
                                                  #####--:::-==##           
                                            *##########*==-=*###            
                                        %###+...........######=:=###        
                                     =%##......::..-::......::::::##+       
                                   *##.........::..:::::::::::::::%%*       
                                  ##....::::::::::::::::::::::::::%%        
                                *##......:::::::::==+:::::::::::-%#         
                               %#+......:::::==-::::::::::::::::--##        
                              =#+...:::::=+::::==:::::::::::::::=--#%       
                              ##.....:::::==:::::.-:::::::::::::---%#       
                             =#=....::::::::::::::=-=:::::::::::---##       
                             ##...::::::==:::::::::::::::::::::----##       
                             ##...:::::::=-::::-==::::--::::::-----##       
                             ##...:::::::::---:::===:::::::::------##       
                              %%..::::::::::::::::::::::::::------##        
                              ##..::::::::::::::::::::::::-------###        
                               #%.::::::::::::::::::::::--------*##         
                               .##::::::::::::::::::::---------###          
                               ##:::-:::::::::::::------------##            
                               ##::::-----------------------###             
                               ##::----------------------###+               
                                %#%%%%%####----------#####                  
                                           %#########                                           
"@
Write-Output $asciiLogo
Start-Sleep 1
Write-Output $asciiText
Start-Sleep 1
"""
    # ADDINS section
    # ADDINS ARE BEYOND JANK, dear lord. i wanted to just set the addin paths in the arguments of the .lnk shortcuts, but no go. So it is this horribleness instead
    environment_paths_to_use = []
    ps1_addins_install_string = ""
    if config["addins"] is None:
        pass
    else:
        ps1_addin_vars = ""
        for addin in config["addins"]:
            if addin in addins_environment_variable_paths:
                ps1_addin_vars += addins_environment_variable_paths[addin]
                environment_paths_to_use.append(addins_environment_variable_paths[addin])
        ps1_addins_install_string = addins.ffmpeg

    saved_paths = ",".join(environment_paths_to_use)
    ps1_addins_path_string = f"""
    # read json config
    $DumbJuiceConfigPath = "$programAppFolder\\dumbjuice.conf"
    $jsonData = Get-Content -Path $DumbJuiceConfigPath -Raw | ConvertFrom-Json
    $addins_environement_variable_paths = @({saved_paths})
    if (-not $jsonData.PSObject.Properties["addin_paths"]) {{
      $jsonData | Add-Member -MemberType NoteProperty -Name "addin_paths" -Value @()
    }}
    $jsonData.addin_paths = $addins_environement_variable_paths
    $jsonData | ConvertTo-Json -Depth 10 | Set-Content -Path $DumbJuiceConfigPath

"""
    
    build_ps1_script = f"""# Configuration
$pythonVersion = "{python_version}"

{logos} 

# Get the current user's home directory and extract the drive letter
$homeDirectory = [System.Environment]::GetFolderPath('UserProfile')
$driveLetter = $homeDirectory.Substring(0, 2)  # Get the drive letter (e.g., C: or D:)

# Construct the DumbJuice path dynamically
$dumbJuicePath = Join-Path -Path $driveLetter -ChildPath "DumbJuice"

# Create the directory if it doesn't exist
#New-Item -ItemType Directory -Path $dumbJuicePath -Force | Out-Null

Write-Output "DumbJuice path: $dumbJuicePath"

$pythonInstallPath = "$dumbJuicePath\\python\\$pythonVersion"
$programName = "{program_name}"
$programPath = "$dumbJuicePath\\programs\\$programName"
$programAppFolder = "$programPath\\appfolder"
$sourceFolder = "$PSScriptRoot"  
$venvPath = "$programPath\\venv"
$pythonExe = "$pythonInstallPath\\python.exe"
$pythonInstallerPath = "$env:TEMP\\python-installer.exe"

# Set paths for the downloaded program files (the ones inside 'appfolder')
$requirementsFile = "$programAppFolder\\requirements.txt"
#$scriptToRun = "$sourceFolder\\{config["mainfile"]}"

# Set path to the icon file
$iconFile = "$programAppFolder\\{ICON_NAME}"  # Make sure you have the .ico file in appfolder

# Ensure DumbJuice folder exists
New-Item -ItemType Directory -Path $dumbJuicePath -Force | Out-Null

# Check if Python version is installed
if (!(Test-Path "$pythonExe")) {{
    Write-Output "Python $pythonVersion not found. Downloading..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe" -OutFile $pythonInstallerPath

    Write-Output "Installing Python..."
    Start-Process -FilePath $pythonInstallerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir=$pythonInstallPath" -Wait

    # Remove installer after installation
    Remove-Item $pythonInstallerPath -Force
}} else {{
    Write-Output "Python $pythonVersion is already installed."
}}

# Ensure program directory exists
New-Item -ItemType Directory -Path $programPath -Force | Out-Null

# Ensure appfolder inside the program folder exists
New-Item -ItemType Directory -Path $programAppFolder -Force | Out-Null

# Copy the program files from appfolder (installer folder) to the appfolder inside the program folder
Write-Output "Copying application files to $programAppFolder..."
Copy-Item -Path "$sourceFolder\\*" -Recurse -Destination $programAppFolder -Force

# Create virtual environment if not exists
if (!(Test-Path "$venvPath")) {{
    Write-Output "Creating virtual environment..."
    & "$pythonExe" -m venv "$venvPath"
}}

# Install dependencies
Write-Output "Installing dependencies..."
& "$venvPath\\Scripts\\python.exe" -m pip install --upgrade pip
& "$venvPath\\Scripts\\python.exe" -m pip install -r $requirementsFile

# Install addins (if any)
{ps1_addins_install_string}
{ps1_addins_path_string}

# Create shortcut to run the program
$shortcutPath = "$programPath\\$programName.lnk"
$targetPath = "$venvPath\\Scripts\\{python_executable}.exe"
$arguments = "`"$programAppFolder\\{config["mainfile"]}`""
Write-Output "Creating shortcut..."
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.Arguments = $arguments
$Shortcut.WorkingDirectory = $programAppFolder
$Shortcut.IconLocation = $iconFile  # Set the icon location for the shortcut
$Shortcut.WindowStyle = 1
$Shortcut.Save()

# Copy the shortcut to the Desktop
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$desktopShortcutPath = "$desktopPath\$programName.lnk"

Write-Output "Copying shortcut to Desktop..."
Copy-Item -Path $shortcutPath -Destination $desktopShortcutPath
Write-Output "Shortcut copied to Desktop."

$debugShortcutPath = "$programPath\\$programName.debug.lnk"
$debugExecutablePath = "$venvPath\\Scripts\\python.exe"

Write-Output "Creating debug launcher..."
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($debugShortcutPath)
$Shortcut.TargetPath = $debugExecutablePath
$Shortcut.Arguments = "-i $arguments "
$Shortcut.WorkingDirectory = $programAppFolder
$Shortcut.IconLocation = $iconFile  # Set the icon location for the shortcut
$Shortcut.WindowStyle = 1
$Shortcut.Save()

"""
    
    build_ps1_script += """

Write-Output "Installation complete. Use the shortcut to run $programName!"
"""
    build_ps1_path = os.path.join(appfolder, "build.ps1")
    with open(build_ps1_path, "w") as ps1_file:
        ps1_file.write(build_ps1_script)

    print(f"Build files created at: {build_folder}")
    os.makedirs(dist_folder, exist_ok=True)
    shutil.make_archive(os.path.join(dist_folder, zip_filename), 'zip', build_folder)
