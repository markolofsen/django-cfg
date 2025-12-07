# Django CFG Thin Bootstrapper (Windows)
# This script downloads the appropriate Go binary and executes it.
#
# Usage:
#   Interactive mode:  iwr https://djangocfg.com/install.ps1 -UseBasicParsing | iex
#   Headless mode:     $env:DJANGOCFG_CONFIG='{"project_name":"myapp","main_domain":"example.com"}'; iwr https://djangocfg.com/install.ps1 -UseBasicParsing | iex
#
# Config JSON fields:
#   project_name  - Project directory name (required for headless)
#   main_domain   - Main domain (e.g., example.com)
#   api_domain    - API domain (e.g., api.example.com)
#   db_name       - Database name (default: djangocfg)
#   db_user       - Database user (default: postgres)
#   db_password   - Database password (default: empty for local)

$ErrorActionPreference = "Stop"
$REPO = "markolofsen/django-cfg"
$BINARY_NAME = "djangocfg-installer"

Write-Host "🚀 Starting Django CFG Installer..." -ForegroundColor Cyan

# Detect Architecture
$arch = "amd64"
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") {
    $arch = "arm64"
}

Write-Host "💻 Detected: Windows/$arch"

# Construct Download URL (binary files, .exe for Windows)
$binaryFile = "$BINARY_NAME-windows-$arch.exe"
$downloadUrl = "https://github.com/$REPO/releases/latest/download/$binaryFile"

Write-Host "⬇️  Downloading installer from: $downloadUrl"

# Create temp directory
$tmpDir = [System.IO.Path]::GetTempPath()
$binaryPath = Join-Path $tmpDir "$BINARY_NAME.exe"

# Download
Invoke-WebRequest -Uri $downloadUrl -OutFile $binaryPath

Write-Host "🚀 Running installer..."

# Check for config from environment variable
$configJson = $env:DJANGOCFG_CONFIG

if ($configJson) {
    Write-Host "📋 Running in headless mode with config..."
    & $binaryPath --headless --config $configJson
} else {
    & $binaryPath
}

# Cleanup
Remove-Item -Path $binaryPath -Force -ErrorAction SilentlyContinue
