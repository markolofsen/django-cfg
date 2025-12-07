# Django CFG Thin Bootstrapper (Windows)
# This script downloads the appropriate Go binary and executes it.

$ErrorActionPreference = "Stop"
$REPO = "markolofsen/django-cfg"
$VERSION = "latest"
$BINARY_NAME = "djangocfg-installer.exe"

Write-Host "🚀 Starting Django CFG Installer..." -ForegroundColor Cyan

# Detect Architecture
$arch = "x86_64" # GoReleaser uses x86_64 for amd64
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") {
    $arch = "arm64"
}

Write-Host "💻 Detected: Windows/$arch"

# Construct Download URL
$archiveName = "$BINARY_NAME-windows-$arch.zip"
$downloadUrl = "https://github.com/$REPO/releases/latest/download/$archiveName"

Write-Host "⬇️  Downloading installer from: $downloadUrl"

# Create temp directory
$tmpDir = [System.IO.Path]::GetTempPath()
$archiveFile = Join-Path $tmpDir $archiveName
$extractDir = Join-Path $tmpDir "djangocfg_extracted"

# Download
Invoke-WebRequest -Uri $downloadUrl -OutFile $archiveFile

# Extract
Write-Host "📂 Extracting..."
Expand-Archive -Path $archiveFile -DestinationPath $extractDir -Force

# Run
$binaryPath = Join-Path $extractDir $BINARY_NAME
Write-Host "🚀 Running installer..."
& $binaryPath
