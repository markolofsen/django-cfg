#!/bin/bash

# 🚀 Simple Ubuntu Development Environment Setup
# Installs Node.js, Python 3.12, Docker & essential tools

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Simple logging
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
step() { echo -e "${YELLOW}🔧 $1${NC}"; }

# Check Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    error "This script is for Ubuntu only!"
    exit 1
fi

# Check sudo
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
    info "This script needs sudo privileges"
    sudo -v || exit 1
fi

echo "🚀 Ubuntu Development Environment Setup"
echo "======================================="
echo

# Ask before starting
if [[ "$1" != "-y" ]]; then
    echo "🎯 Ready to install development tools!"
    echo "This will install: Node.js + npm, Python 3.12, Docker + docker-compose, mc, psql, and essential tools"
    echo
    read -p "Continue? (y/N): " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && { info "Cancelled"; exit 0; }
fi

echo
info "Starting installation..."

# Update system
step "Updating system..."
sudo apt-get update -qq
sudo apt-get install -y curl ca-certificates gnupg software-properties-common

# Install Node.js
step "Installing Node.js LTS..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Fix npm permissions
if [[ $EUID -ne 0 ]]; then
    mkdir -p ~/.npm-global
    npm config set prefix '~/.npm-global'
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    export PATH=~/.npm-global/bin:$PATH
fi

# Install TypeScript tools
npm install -g tsx typescript ts-node @types/node 2>/dev/null || warn "Some packages failed"

# Install Python 3.12
step "Installing Python 3.12..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -qq
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip python3-full

# Create python3 symlink
sudo ln -sf /usr/bin/python3.12 /usr/bin/python3

# Install essential Python packages for manage.py
step "Installing Python packages..."
python3 -m pip install --user --break-system-packages \
    questionary pyyaml python-dotenv 2>/dev/null || {
    warn "pip --user failed, trying virtual environment"
    # Fallback: create virtual environment
    python3 -m venv ~/.dev-env
    source ~/.dev-env/bin/activate
    pip install questionary pyyaml python-dotenv
    echo 'source ~/.dev-env/bin/activate' >> ~/.bashrc
}

# Ensure PATH includes user bin
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
    export PATH=$HOME/.local/bin:$PATH
fi

# Install Docker
step "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker and add user to group
sudo systemctl start docker
sudo systemctl enable docker
if [[ $EUID -ne 0 ]]; then
    sudo usermod -aG docker $USER
    
    # Test Docker access
    if ! docker ps &>/dev/null; then
        warn "Docker permissions not applied yet"
        info "Run: newgrp docker  # to apply docker group to current session"
        info "Or logout/login to apply permanently"
    else
        success "Docker access configured"
    fi
fi

# Install docker-compose standalone (for compatibility)
step "Installing docker-compose standalone..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install essential tools
step "Installing essential tools..."
sudo apt-get install -y git vim nano htop tree jq unzip build-essential mc postgresql-client

# Cleanup
sudo apt-get autoremove -y -qq
npm cache clean --force 2>/dev/null || true

echo
success "Installation completed! 🎉"

# Show what was installed
echo
echo "📋 Installed:"
echo "✅ Node.js: $(node --version 2>/dev/null || echo 'Failed')"
echo "✅ Python: $(python3 --version 2>/dev/null || echo 'Failed')"
echo "✅ Docker: $(docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',' || echo 'Failed')"
echo "✅ npm: $(npm --version 2>/dev/null || echo 'Failed')"
echo "✅ mc: $(mc --version 2>/dev/null | head -1 | cut -d' ' -f3 || echo 'Failed')"
echo "✅ psql: $(psql --version 2>/dev/null | cut -d' ' -f3 || echo 'Failed')"
echo "✅ docker-compose: $(docker-compose --version 2>/dev/null | cut -d' ' -f3 | tr -d ',' || echo 'Failed')"

echo
echo "💡 Next Steps:"
echo "  🔄 Restart terminal: source ~/.bashrc"
echo "  🧪 Test: node --version && python3 --version && docker --version && docker-compose --version"
echo "  🐳 Test Docker manager: python3 devops/manage.py --help"
echo "  📁 File manager: mc (Midnight Commander)"
echo ""
echo "🐳 Docker Setup:"
if ! docker ps &>/dev/null 2>&1; then
    echo "  ⚠️  Docker permissions not active in current session"
    echo "  🔧 Quick fix: newgrp docker"
    echo "  🔄 Permanent fix: logout/login"
    echo "  🧪 Test: docker ps"
else
    echo "  ✅ Docker ready to use!"
fi
echo
echo "🎉 Happy coding! 🚀"
