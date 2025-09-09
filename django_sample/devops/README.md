# 🚀 UnrealOS Django DevOps Tools

Complete DevOps toolkit for UnrealOS Django project development and deployment.

## 📁 What's Inside

- **`setup.sh`** - Ubuntu development environment setup script
- **`manage.py`** - Docker infrastructure management CLI
- **`README.md`** - this documentation

## 🛠️ Environment Setup

### Quick Ubuntu Setup
```bash
# Install everything (Node.js, Python 3.12, Docker)
./devops/setup.sh

# Install with auto-confirmation
./devops/setup.sh -y

# Install only specific components
./devops/setup.sh --node-only
./devops/setup.sh --python-only  
./devops/setup.sh --docker-only

# Verify current installation
./devops/setup.sh --verify
```

### What Gets Installed
- **Node.js LTS** + npm + TypeScript tools (tsx, tsc, ts-node)
- **Python 3.12** + venv + pipx + development tools
- **Docker** + Docker Compose + buildx plugin
- **CLI Tools** via pipx: poetry, black, isort, questionary

### Requirements
- Ubuntu 20.04+ (recommended 22.04+)
- sudo privileges
- Internet connection

## 🐳 Docker Management

### Interactive Docker Manager
```bash
# Launch interactive menu
python3 devops/manage.py

# Or with direct commands
python3 devops/manage.py --help
```

### Docker Manager Features
- 🔄 **Interactive Menu** - service management
- 🔨 **Quick Rebuild** - fast service rebuilds
- 🖥️ **Container Shell** - direct container access
- 📋 **Log Monitoring** - real-time log viewing
- 🚀 **Service Prioritization** - correct startup order
- 💀 **Nuclear Rebuild** - complete infrastructure reset
- 📊 **Status Dashboard** - service health overview

### Docker Architecture
```
🗄️  Database Layer
├── postgres (PostgreSQL 16)
└── redis (Redis 7) [optional]

🚀 Application Layer  
└── django (UnrealOS Django)

🌐 Proxy Layer
└── nginx (Production reverse proxy)
```

### Data Storage
All data stored in project bind mounts:
- `../logs/` - Django application logs
- `../static/` - static files (CSS, JS, images)
- `../media/` - user uploaded media

## 🚀 Quick Start Guide

### 1. Setup Development Environment
```bash
# Clone and setup
cd unrealos-django/
./devops/setup.sh -y
```

### 2. Start Docker Services
```bash
# Interactive management
python3 devops/manage.py

# Or direct commands
docker-compose -f docker/docker-compose.yml up -d
```

### 3. Access Services
- **Django Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **Via Nginx**: http://localhost/ (production)

## 📋 Common Tasks

### Development Workflow
```bash
# 1. Start development environment
python3 devops/manage.py
# Select: Quick Actions → Start All Services

# 2. Make code changes
# Edit your Django code...

# 3. Quick rebuild Django
python3 devops/manage.py
# Select: django → Quick Rebuild

# 4. View logs
python3 devops/manage.py  
# Select: django → Show Logs
```

### Production Deployment
```bash
# 1. Setup production server
./devops/setup.sh -y

# 2. Start with nginx
docker-compose --profile production up -d

# 3. Monitor services
python3 devops/manage.py
# Select: System Status
```

### Troubleshooting
```bash
# Check service status
python3 devops/manage.py
# Select: System Status

# View all logs
docker-compose logs -f

# Nuclear rebuild (last resort)
python3 devops/manage.py
# Select: Quick Actions → Nuclear Rebuild

# Manual container access
docker-compose exec django bash
```

## 🔧 Advanced Usage

### Environment Variables
Create `.env` file in project root:
```bash
# Django settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# Redis (optional)
REDIS_URL=redis://redis:6379/0
```

### Custom Docker Compose
Override default settings:
```bash
# Create docker-compose.override.yml
version: '3.8'
services:
  django:
    environment:
      - DEBUG=true
    ports:
      - "8001:8000"  # Custom port
```

### Python Package Management
```bash
# Install packages (respects PEP 668)
pipx install package-name

# Or use virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install package-name
```

## 🐛 Troubleshooting

### Common Issues

**1. Permission Denied (Docker)**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

**2. Port Already in Use**
```bash
# Check what's using port 8000
sudo lsof -i :8000
# Kill process or change port in docker-compose.yml
```

**3. Python Package Installation Fails**
```bash
# Use pipx for CLI tools
pipx install questionary

# Or create virtual environment
python3 -m venv ~/.global-venv
source ~/.global-venv/bin/activate
pip install questionary
```

**4. Database Connection Issues**
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Log Locations
- **Docker logs**: `docker-compose logs [service]`
- **Django logs**: `./logs/` directory
- **System logs**: `/var/log/` (Ubuntu)

## 🔍 Monitoring & Debugging

### Health Checks
```bash
# Service status
python3 devops/manage.py

# Container health
docker-compose ps

# Resource usage
docker stats

# System resources
htop
```

### Performance Monitoring
```bash
# Django debug toolbar (development)
# Add to INSTALLED_APPS in settings.py

# Database queries
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Redis monitoring
docker-compose exec redis redis-cli monitor
```

## 🚀 Extending the Setup

### Adding New Services
1. Add service to `docker/docker-compose.*.yml`
2. Update `devops/manage.py` service discovery
3. Configure service priority if needed
4. Update this documentation

### Custom Setup Scripts
Create custom setup scripts in `devops/`:
```bash
# devops/custom-setup.sh
#!/bin/bash
source devops/setup.sh
# Add custom installation steps
```

---

**Built for UnrealOS Django Project** 🚀  
**Ubuntu-optimized DevOps toolkit**