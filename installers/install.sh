#!/bin/bash

# Django CFG Thin Bootstrapper
# This script downloads the appropriate Go binary and executes it.
#
# Usage:
#   Interactive mode:  curl -L https://djangocfg.com/install.sh | sh
#   Headless mode:     curl -L https://djangocfg.com/install.sh | sh -s -- --config '{"project_name":"myapp","main_domain":"example.com"}'
#
# Config JSON fields:
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

# Parse arguments - look for --config
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
    curl -fsSL "$DOWNLOAD_URL" -o "$BINARY_PATH"
elif command_exists wget; then
    wget -q "$DOWNLOAD_URL" -O "$BINARY_PATH"
else
    echo "❌ Error: curl or wget is required."
    exit 1
fi

chmod +x "$BINARY_PATH"

echo "🚀 Running installer..."

# Run installer with config if provided
if [ -n "$CONFIG_JSON" ]; then
    echo "📋 Running in headless mode with config..."
    "$BINARY_PATH" --headless --config "$CONFIG_JSON" $EXTRA_ARGS
else
    "$BINARY_PATH" $EXTRA_ARGS
fi
