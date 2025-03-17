# DumbJuice
DumbJuice is a Python module that simplifies the process of packaging small Python programs into self-contained installable packages. These packages can be shared with non-technical users, who only need to run a single install.bat file to install Python, set up a virtual environment, install necessary dependencies, and create a shortcut to the program on their desktop.

## Installation
To install the dumbjuice module

`
pip install dumbjuice
`

## Usage

### Requirements


#### Recommended project structure
project_folder/
│
├── main.py                # Your main program file
├── dumbjuice.conf          # Configuration file for DumbJuice
├── .gitignore (optional)   # Git ignore file (optional)
├── requirements.txt        # Your program's dependencies (if any)
├── djicon.ico (optional)   # Optional icon file for the application
│
├── some_folder/            # Additional folders (optional)
│   ├── other_file.py       # Other Python files
│   └── subfolder/          # Nested subfolders (optional)
│       └── another_file.py
│
└── other_script.py         # Additional Python script files (optional)

#### Configuration
The build function needs a json configuration file (dumbjuice.conf) with the following:
`
{
  "program_name": "MyProgram",
  "python_version": "3.11.7",
  "gui": false,
  "ignore": ["*.git", "*.gitignore"],
  "use_gitignore": true,
  "include": ["my_module.py"]
}
`
program_name: The name of your program. (*)
python_version: The Python version to be installed (e.g., "3.8.10"). (*)
gui: Set to true if your program requires a GUI; set to false for console programs. 
ignore: A list of files or directories to be excluded from the build.
use_gitignore: Set to true if you want to use .gitignore rules to determine which files to exclude.
include: A list of files or directories that should always be included, even if they are in the ignore list.

* required

### Building
To build the installer for your program, navigate to the folder containing your program's files and configuration, and run the following:
`
python -m dumbjuice build [target_folder]
`

Alternatively, if you want to use the command line interface (CLI), you can use the following command:
`
dumbjuice-build [target_folder]
`

or in python
`
import dumbjuice as dj
dj.build(<target_folder>)

target_folder (optional): Path to the folder containing your python program files. If not provided, the current working directory will be used.


## What Happens During the Build Process?
* Your program files, including the requirements.txt and dumbjuice.conf, are copied into a new folder structure in dumbjuice_build/appfolder
* A build.ps1 file is created that is responsible for installing the program and necessary for the user is added dumbjuice_build/appfolder
* A install.bat file which initiates the build.ps1 on the users end when started is added to dumbjuice_build/
* The entire dumbjuice_build folder is zipped and added to dumbjuice_dist

## What happens during the install process?
* DumbJuice looks for already existing DumbJuice installation and adds it if necessary
* DumbJuice script creates the program structure in /DumbJuice/programs/<program_name> and copies over the files in appfolder/
* DumbJuice script install the defined python version (if not present in DumbJuice already), creates a venv for the program and installs all modules defined in requirements.txt
* DumbJuice script creates shortcuts for the user which starts the program

## Starting a program
Simply double click the generated <program_name> shortcut, either on the Desktop or in the /DumbJuice/programs/<program_name> folder

## Instructions
in your python app folder create a dumbjuice.conf
if you are using any libraries and modules that require installing by pip, include that in a requirements.txt file as well

`
import dumbjuice as dj
dj.build("appfolder")
`

