import os

_ffmpeg_path = os.path.join("$dumbJuicePath","addins","ffmpeg")
_ffmpeg_tmp_path = os.path.join("$env:temp","ffmpeg.zip")

ffmpeg = f"""

$ffmpegInstallFolder = "{_ffmpeg_path}"
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

$ffmpegDownloadPath = "{_ffmpeg_tmp_path}"

# Check if ffmpeg is already installed in the known location
if (-not (Test-Path $ffmpegInstallFolder)) {{
    Write-Output "ffmpeg not found. Installing..."
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegDownloadPath
    Write-Output "Extracting ffmpeg..."
    New-Item -Path $ffmpegInstallFolder -ItemType Directory -Force
    Expand-Archive -Path $ffmpegDownloadPath -DestinationPath $ffmpegInstallFolder
}}

$ffmpegDir = Get-ChildItem -Path "$ffmpegInstallFolder" -Directory | Where-Object {{ $_.Name -like "ffmpeg*-essentials_build" }}
#$ffmpegPath = Join-Path -Path $ffmpegDir.FullName -ChildPath "bin\\ffmpeg.exe"
$ffmpegPath = Join-Path -Path $ffmpegDir.FullName -ChildPath "bin"



"""

print(ffmpeg)