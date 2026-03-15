# 🚀 Django CFG CLI

Simple command-line interface for creating Django projects with django-cfg template from GitHub.

## 📦 Installation

```bash
pip install django-cfg
```

## 🎯 Quick Start

### Create a New Project

```bash
# Extract to current directory
django-cfg create-project

# Extract to specific directory
django-cfg create-project --path ./my-project/

# Overwrite existing files
django-cfg create-project --force
```

### What It Does

Downloads the latest django-cfg template from GitHub (https://github.com/markolofsen/django-cfg) and extracts it to the specified location.

## 🔧 After Project Creation

1. **Install dependencies:**
   ```bash
   poetry install  # or: pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## 💡 Features Included

- ✅ Type-safe configuration with Pydantic v2
- ✅ OTP authentication (Email-based)
- ✅ TOTP 2FA support (Authenticator apps)
- ✅ Telegram bot integration
- ✅ Modern Unfold admin interface
- ✅ Auto-generated API documentation
- ✅ JWT authentication system
- ✅ Multi-database support with routing
- ✅ Background task processing with Dramatiq
- ✅ Docker deployment ready

## 📋 Commands

### `create-project`

Downloads and extracts the latest django-cfg template from GitHub.

```bash
django-cfg create-project [OPTIONS]
```

**Options:**
- `--path, -p PATH` - Directory where to extract the project (default: current directory)
- `--force, -f` - Overwrite existing files if they exist

### `info`

Shows information about django-cfg installation.

```bash
django-cfg info
django-cfg info --verbose
```

## 📚 Documentation

- **GitHub**: https://github.com/markolofsen/django-cfg
- **Issues**: https://github.com/markolofsen/django-cfg/issues

## 🌐 Developed by

**Unrealon.com** — Complex parsers on demand

https://unrealon.com

## 📄 License

MIT License

---

**Powered by django-cfg** 🚀