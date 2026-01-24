#!/bin/bash

# Django CFG Installer
# This script downloads the appropriate Go binary and executes it.
#
# Usage:
#   New project (interactive):    curl -L https://djangocfg.com/install.sh | sh
#   New project (headless):       curl -L https://djangocfg.com/install.sh | sh -s -- --config '{"project_name":"myapp"}'
#   Setup cloned project:         ./installers/install.sh --setup
#   Auto-detect mode:             ./installers/install.sh  (detects if inside existing project)
#
# Config JSON fields (for new projects):
#   project_name  - Project directory name (required for headless)
#   main_domain   - Main domain (e.g., example.com)
#   api_domain    - API domain (e.g., api.example.com)
#   db_name       - Database name (default: djangocfg)
#   db_user       - Database user (default: postgres)
#   db_password   - Database password (default: empty for local)

set -e

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

REPO="markolofsen/django-cfg"
BINARY_NAME="djangocfg-installer"

# Parse arguments
CONFIG_JSON=""
EXTRA_ARGS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_JSON="$2"
            shift 2
            ;;
        --config=*)
            CONFIG_JSON="${1#*=}"
            shift
            ;;
        --setup|--simulate|--dry-run|--headless)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Detect OS and Arch
OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Linux*)     OS=linux;;
    Darwin*)    OS=darwin;;
    *)          echo "Unsupported OS: ${OS}"; exit 1;;
esac

case "${ARCH}" in
    x86_64)    ARCH=amd64;;
    arm64)     ARCH=arm64;;
    aarch64)   ARCH=arm64;;
    *)         echo "Unsupported Architecture: ${ARCH}"; exit 1;;
esac

echo "🚀 Starting Django CFG Installer..."
echo "💻 Detected: $OS/$ARCH"

# Construct Download URL (binary files without .tar.gz extension)
BINARY_FILE="$BINARY_NAME-$OS-$ARCH"
DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/$BINARY_FILE"

echo "⬇️  Downloading installer from: $DOWNLOAD_URL"

# Create temp directory
TMP_DIR=$(mktemp -d)
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

BINARY_PATH="$TMP_DIR/$BINARY_NAME"

# Download binary
if command_exists curl; then
    curl -fsSL "$DOWNLOAD_URL" -o "$BINARY_PATH" || {
        echo "❌ Failed to download installer"
        echo "💡 Try downloading manually:"
        echo "   curl -L $DOWNLOAD_URL -o djangocfg-installer"
        echo "   chmod +x djangocfg-installer"
        echo "   ./djangocfg-installer"
        exit 1
    }
elif command_exists wget; then
    wget -q "$DOWNLOAD_URL" -O "$BINARY_PATH" || {
        echo "❌ Failed to download installer"
        exit 1
    }
else
    echo "❌ Error: curl or wget is required."
    exit 1
fi

# Make binary executable
chmod +x "$BINARY_PATH" || {
    echo "⚠️  Warning: Failed to set execute permissions"
    echo "💡 You may need to run: chmod +x $BINARY_PATH"
}

echo "🚀 Running installer..."

# Build command with all arguments
if [ -n "$CONFIG_JSON" ]; then
    echo "📋 Running in headless mode with config..."
    "$BINARY_PATH" --headless --config "$CONFIG_JSON" $EXTRA_ARGS
else
    "$BINARY_PATH" $EXTRA_ARGS
fi
