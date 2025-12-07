#!/bin/bash

# Django CFG Thin Bootstrapper
# This script downloads the appropriate Go binary and executes it.

set -e

REPO="markolofsen/django-cfg"
VERSION="latest" # Or specific version
BINARY_NAME="djangocfg-installer"

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

# Construct Download URL
# GoReleaser naming: djangocfg-installer-linux-x86_64.tar.gz
# We mapped x86_64 -> amd64 in script, but GoReleaser uses x86_64. Let's fix script mapping.

case "${ARCH}" in
    amd64)     ARCH=x86_64;;
    arm64)     ARCH=arm64;;
    *)         echo "Unsupported Architecture: ${ARCH}"; exit 1;;
esac

ARCHIVE_NAME="$BINARY_NAME-$OS-$ARCH.tar.gz"
DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/$ARCHIVE_NAME"

echo "⬇️  Downloading installer from: $DOWNLOAD_URL"

# Create temp directory
TMP_DIR=$(mktemp -d)
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

ARCHIVE_FILE="$TMP_DIR/$ARCHIVE_NAME"
EXTRACT_DIR="$TMP_DIR/extracted"
mkdir -p "$EXTRACT_DIR"

# Download and Extract
if command_exists curl; then
    curl -fsSL "$DOWNLOAD_URL" -o "$ARCHIVE_FILE"
elif command_exists wget; then
    wget -q "$DOWNLOAD_URL" -O "$ARCHIVE_FILE"
else
    echo "❌ Error: curl or wget is required."
    exit 1
fi

tar -xzf "$ARCHIVE_FILE" -C "$EXTRACT_DIR"

# Find the binary (it might be in a subdirectory depending on goreleaser config, usually root)
BINARY_PATH="$EXTRACT_DIR/$BINARY_NAME"
chmod +x "$BINARY_PATH"

echo "🚀 Running installer..."
"$BINARY_PATH"
