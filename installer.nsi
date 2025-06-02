
!define APP_NAME "gui_example_app"
!define PYTHON_VERSION "3.11.7"
!define PYTHON_INSTALLER "python-$PYTHON_VERSION-amd64.exe"
!define PYTHON_URL "https://www.python.org/ftp/python/$PYTHON_VERSION/$PYTHON_INSTALLER"

OutFile "install.exe"
InstallDir "$PROGRAMFILES\$APP_NAME"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install MyApp"

  SetOutPath "$INSTDIR"

  ; Copy all app files (must include requirements.txt and main.py)
  File /r "build_output\*.*

  ; Download Python installer
  DetailPrint "Downloading Python..."
  nsisdl::download "$PYTHON_URL" "$TEMP\$PYTHON_INSTALLER
  Pop $0
  StrCmp $0 "cancel" cancel_download

  ; Install Python silently to a subfolder
  DetailPrint "Installing Python..."
  ExecWait '"$TEMP\$PYTHON_INSTALLER" /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir=$INSTDIR\python'

  ; Create virtual environment
  DetailPrint "Creating virtual environment..."
  ExecWait '"$INSTDIR\python\python.exe" -m venv "$INSTDIR\venv"'

  ; Install requirements
  DetailPrint "Installing requirements..."
  
  ExecWait '"$INSTDIR\venv\Scripts\pip.exe" install -r "$INSTDIR\requirements.txt"'

  ; Create desktop shortcut
  DetailPrint "Creating shortcut..."
  $INSTDIR\main.py
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\venv\Scripts\pythonw.exe" "$INSTDIR\main.py"

  Goto done

cancel_download:
  MessageBox MB_OK "Download cancelled or failed"

done:

SectionEnd

