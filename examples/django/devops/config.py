#!/usr/bin/env python3
"""
🔧 ReformsAI Django Docker Manager - Configuration
Centralized configuration for Docker Compose management
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


# =============================================================================
# 🎯 Application Constants
# =============================================================================

class AppConstants:
    """Application-wide constants"""
    
    # Project Info
    PROJECT_NAME = "ReformsAI Django"
    PROJECT_SLUG = "reforms-django"
    
    # Service Types
    SERVICE_TYPES = {
        "database": "🗄️",
        "application": "🚀", 
        "proxy": "🌐",
        "infrastructure": "🔧"
    }
    
    # Status Emojis
    STATUS_EMOJIS = {
        "running": "🟢",
        "stopped": "🔴",
        "build": "🔨",
        "package": "📦"
    }
    
    # Service Priorities (higher = start first)
    SERVICE_PRIORITIES = {
        "postgres": 2,
        "redis": 2,
        "database": 2,
        "django": 1,
        "application": 1,
        "nginx": 0,
        "proxy": 0
    }


# =============================================================================
# 🐳 Docker Configuration
# =============================================================================

@dataclass
class DockerPaths:
    """Docker-related paths configuration"""
    
    # Base paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    docker_dir: Path = field(init=False)
    devops_dir: Path = field(init=False)
    
    # Compose files
    main_compose: str = "docker-compose.yml"
    
    # Volume paths (bind mounts)
    logs_dir: Path = field(init=False)
    static_dir: Path = field(init=False)
    media_dir: Path = field(init=False)
    
    def __post_init__(self):
        """Initialize computed paths"""
        self.docker_dir = self.project_root / "docker"
        self.devops_dir = self.project_root / "devops"
        self.logs_dir = self.project_root / "logs"
        self.static_dir = self.project_root / "static"
        self.media_dir = self.project_root / "media"
    
    def get_compose_path(self, filename: str) -> Path:
        """Get full path to compose file"""
        return self.docker_dir / filename
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        for dir_path in [self.logs_dir, self.static_dir, self.media_dir]:
            dir_path.mkdir(exist_ok=True)


@dataclass
class DockerConfig:
    """Docker Compose configuration"""
    
    paths: DockerPaths = field(default_factory=DockerPaths)
    
    # Compose settings
    compose_files: List[str] = field(default_factory=list)
    profiles: List[str] = field(default_factory=lambda: ["development", "production"])
    
    # Network settings (use Docker Compose default)
    # default_network: str = "docker_default"  # Auto-created by docker-compose
    
    # Database settings
    postgres_user: str = "unrealos"
    postgres_db: str = "unrealos_db"
    postgres_host: str = "postgres"  # Docker service name
    postgres_port: int = 5432
    
    # Application URLs
    production_admin_url: str = "http://localhost/admin/"
    development_admin_url: str = "http://localhost:8000/admin/"
    production_api_url: str = "http://localhost/api/docs/"
    development_api_url: str = "http://localhost:8000/api/docs/"
    
    def __post_init__(self):
        """Auto-detect compose files"""
        self.compose_files = self._detect_compose_files()
        self.paths.ensure_directories()
    
    def _detect_compose_files(self) -> List[str]:
        """Detect compose files from main compose file"""
        import yaml
        
        main_path = self.paths.get_compose_path(self.paths.main_compose)
        
        if not main_path.exists():
            return []
        
        try:
            with open(main_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data.get("include", [])
        except Exception:
            return []


# =============================================================================
# 🚀 Service Configuration
# =============================================================================

@dataclass
class Service:
    """Docker service configuration"""
    
    name: str
    file: Path
    type: str
    has_build: bool
    ports: List[str] = field(default_factory=list)
    status: str = "unknown"
    priority: int = 0
    profiles: List[str] = field(default_factory=list)
    
    def get_priority(self) -> int:
        """Get service priority based on name and type"""
        name_lower = self.name.lower()
        
        # Check specific service names
        for service_name, priority in AppConstants.SERVICE_PRIORITIES.items():
            if service_name in name_lower:
                return priority
        
        return 0
    
    def get_display_emoji(self) -> str:
        """Get emoji for service type"""
        return AppConstants.SERVICE_TYPES.get(self.type, "📦")


# =============================================================================
# 🌐 Application URLs and Endpoints
# =============================================================================

@dataclass
class AppUrls:
    """Application URLs configuration"""
    
    # Base URLs
    django_base: str = "http://localhost:8000"
    nginx_base: str = "http://localhost"
    
    # Endpoints
    admin_path: str = "/admin/"
    api_docs_path: str = "/api/docs/"
    health_path: str = "/cfg/health/"
    
    def get_admin_url(self, use_nginx: bool = False) -> str:
        """Get admin panel URL"""
        base = self.nginx_base if use_nginx else self.django_base
        return f"{base}{self.admin_path}"
    
    def get_api_docs_url(self, use_nginx: bool = False) -> str:
        """Get API documentation URL"""
        base = self.nginx_base if use_nginx else self.django_base
        return f"{base}{self.api_docs_path}"
    
    def get_health_url(self, use_nginx: bool = False) -> str:
        """Get health check URL"""
        base = self.nginx_base if use_nginx else self.django_base
        return f"{base}{self.health_path}"


# =============================================================================
# 🔧 Command Templates
# =============================================================================

class DockerCommands:
    """Docker command templates"""
    
    # Basic commands
    UP = "up -d"
    DOWN = "down"
    RESTART = "restart"
    BUILD = "build"
    BUILD_NO_CACHE = "build --no-cache"
    BUILD_PULL = "build --no-cache --pull"
    
    # Compose commands
    PS = "ps"
    LOGS = "logs"
    EXEC = "exec"
    
    # Cleanup commands
    DOWN_RMI = "down --rmi all"
    SYSTEM_PRUNE = ["docker", "system", "prune", "-af"]
    BUILDER_PRUNE = ["docker", "builder", "prune", "-af"]
    
    @staticmethod
    def get_profile_command(command: str, profile: str) -> List[str]:
        """Get command with profile"""
        return ["--profile", profile] + command.split()


# =============================================================================
# 🗄️ Database Configuration
# =============================================================================

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    
    # PostgreSQL settings
    postgres_user: str = "unrealos"
    postgres_password: str = "unrealos_password"
    postgres_db: str = "unrealos_db"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    
    # Redis settings (optional)
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    def get_postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# =============================================================================
# 📋 Main Configuration Class
# =============================================================================

@dataclass
class ManagerConfig:
    """Main configuration for Docker Manager"""
    
    # Sub-configurations
    docker: DockerConfig = field(default_factory=DockerConfig)
    urls: AppUrls = field(default_factory=AppUrls)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Manager settings
    auto_open_browser: bool = True
    show_container_logs: bool = True
    confirm_destructive_actions: bool = True
    
    # Timeouts (seconds)
    container_start_timeout: int = 60
    health_check_timeout: int = 30
    command_timeout: int = 300
    
    def show_info(self) -> None:
        """Show configuration information"""
        print(f"\n📋 {AppConstants.PROJECT_NAME} Configuration:")
        print(f"   📁 Project Root: {self.docker.paths.project_root}")
        print(f"   🐳 Docker Dir: {self.docker.paths.docker_dir}")
        print(f"   📄 Main Compose: {self.docker.paths.main_compose}")
        print(f"   📄 Detected Files: {len(self.docker.compose_files)}")
        for i, file in enumerate(self.docker.compose_files, 1):
            print(f"     {i}. {file}")
        print(f"   🌐 Django URL: {self.urls.django_base}")
        print(f"   🏭 Nginx URL: {self.urls.nginx_base}")
        print()


# =============================================================================
# 🎯 Configuration Factory
# =============================================================================

def get_default_config() -> ManagerConfig:
    """Get default configuration instance"""
    return ManagerConfig()


def get_config_from_env() -> ManagerConfig:
    """Get configuration with environment variable overrides"""
    config = get_default_config()
    
    # Override with environment variables if present
    if os.getenv("DJANGO_PORT"):
        port = os.getenv("DJANGO_PORT")
        config.urls.django_base = f"http://localhost:{port}"
    
    if os.getenv("NGINX_PORT"):
        port = os.getenv("NGINX_PORT")
        if port != "80":
            config.urls.nginx_base = f"http://localhost:{port}"
    
    return config


# =============================================================================
# 🧪 Configuration Validation
# =============================================================================

def validate_config(config: ManagerConfig) -> bool:
    """Validate configuration"""
    try:
        # Check paths exist
        if not config.docker.paths.project_root.exists():
            print(f"❌ Project root not found: {config.docker.paths.project_root}")
            return False
        
        if not config.docker.paths.docker_dir.exists():
            print(f"❌ Docker directory not found: {config.docker.paths.docker_dir}")
            return False
        
        main_compose = config.docker.paths.get_compose_path(config.docker.paths.main_compose)
        if not main_compose.exists():
            print(f"❌ Main compose file not found: {main_compose}")
            return False
        
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test configuration
    config = get_default_config()
    config.show_info()
    validate_config(config)
