#!/usr/bin/env python3
"""
🐳 UnrealOS Django Docker Manager
Simple Docker Compose management for UnrealOS Django
"""

import os
import sys
import subprocess
import questionary
import yaml
from pathlib import Path
from typing import Dict, List

# Import configuration
from config import get_default_config, validate_config, AppConstants, DockerCommands


class DockerManager:
    """Simple Docker Compose manager"""
    
    def __init__(self):
        self.config = get_default_config()
        self.main_file = self.config.docker.paths.get_compose_path("docker-compose.yml")
        self.services = {}
        
        # Validate configuration
        if not validate_config(self.config):
            sys.exit(1)
    
    def run_command(self, command: str, service: str = None) -> bool:
        """Run docker-compose command"""
        cmd = ["docker-compose", "-f", str(self.main_file)]
        cmd.extend(command.split())
        
        # Add service name at the end if specified
        if service:
            cmd.append(service)
        
        print(f"🚀 {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            return False

    def get_running_containers(self) -> Dict[str, str]:
        """Get list of running containers using docker-compose ps (copied from cli.py)"""
        try:
            # Use docker-compose ps to get services with their actual names
            result = subprocess.run(
                ["docker-compose", "-f", str(self.main_file), "ps"],
                capture_output=True,
                text=True,
                check=True,
            )
            
            containers = {}
            lines = result.stdout.strip().split('\n')
            
            # Find header line to determine column positions
            header_line = None
            service_col_pos = None
            status_col_pos = None
            
            for i, line in enumerate(lines):
                if 'SERVICE' in line and 'STATUS' in line:
                    header_line = line
                    service_col_pos = line.find('SERVICE')
                    status_col_pos = line.find('STATUS')
                    break
            
            if header_line is None or service_col_pos is None or status_col_pos is None:
                raise Exception("Could not parse docker-compose ps header")
            
            # Process service lines (skip header and any lines before it)
            for line in lines[i+1:]:
                if line.strip() and not line.startswith('-'):
                    try:
                        # Extract service name and status based on column positions
                        if len(line) > service_col_pos:
                            # Get service name (from SERVICE column)
                            service_part = line[service_col_pos:status_col_pos].strip() if status_col_pos > service_col_pos else line[service_col_pos:].strip()
                            service_name = service_part.split()[0] if service_part else ""
                            
                            # Get status (from STATUS column)
                            if len(line) > status_col_pos:
                                status_part = line[status_col_pos:].strip()
                                status = status_part.split()[0] if status_part else ""
                                
                                # Check if service is running (status contains "Up")
                                if service_name and "Up" in status:
                                    containers[service_name] = status
                    except:
                        continue
            
            return containers
        except Exception as e:
            # Fallback to docker ps if docker-compose ps fails
            try:
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                containers = {}
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        name, status = line.split("|", 1)
                        # Map container names to service names
                        # unrealos_django -> django, unrealos_postgres -> postgres, etc.
                        if name.startswith("unrealos_"):
                            service_name = name.replace("unrealos_", "")
                            containers[service_name] = status
                        else:
                            containers[name] = status
                
                return containers
            except:
                print(f"⚠️  Error parsing containers: {e}")
                return {}
    
    def debug_containers(self):
        """Debug container detection"""
        print("🔍 Debug: Container Detection")
        print("=" * 50)
        
        try:
            # Test docker-compose ps
            result = subprocess.run(
                ["docker-compose", "-f", str(self.main_file), "ps"],
                capture_output=True, text=True, check=True
            )
            print("📋 docker-compose ps output:")
            print(result.stdout)
            
            # Test docker ps
            result2 = subprocess.run(
                ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
                capture_output=True, text=True, check=True
            )
            print("\n🐳 docker ps output:")
            print(result2.stdout)
            
            # Test our parsing
            containers = self.get_running_containers()
            print(f"\n🎯 Detected containers: {containers}")
            
        except Exception as e:
            print(f"❌ Debug error: {e}")

    def is_nginx_running(self) -> bool:
        """Check if nginx is running"""
        containers = self.get_running_containers()
        return any("nginx" in service.lower() for service in containers.keys())
    
    def get_service_display(self, service_name: str, status: str) -> str:
        """Format service display name"""
        emoji = "📦"
        if "django" in service_name.lower():
            emoji = "🚀"
        elif "postgres" in service_name.lower():
            emoji = "🗄️"
        elif "nginx" in service_name.lower():
            emoji = "🌐"
        elif "redis" in service_name.lower():
            emoji = "🔧"
        
        return f"🟢 {emoji} {service_name:<15} {status}"
    
    def show_quick_actions(self):
        """Show quick actions menu - Production Only"""
        actions = [
            "🏭 Start Production (Full Stack)",
            "🔧 Setup Volumes (Auto-create)",
            "🛠️  Fix Permissions (entrypoint.sh + volumes)",
            "🔍 Debug Container Detection",
            "⏹️  Stop All Services",
            "🔄 Restart All Services",
            "🔨 Rebuild All Services",
            "💀 Nuclear Rebuild (Full Clean)",
            "📊 Production Status",
            "🔙 Back"
        ]
        
        choice = questionary.select("Quick Actions:", choices=actions).ask()
        
        if not choice or choice == "🔙 Back":
            return
        
        if choice.startswith("🏭"):
            self.run_command("up -d")
        
        elif choice.startswith("⏹️"):
            self.run_command("down")
        
        elif choice.startswith("🔄"):
            self.run_command("restart")
        
        elif choice.startswith("🔨"):
            self.run_command("build --no-cache")
            self.run_command("up -d")
        
        elif choice.startswith("💀"):
            self.nuclear_rebuild()
        
        elif choice.startswith("📊"):
            self.show_production_status()
        
        elif choice.startswith("🔧"):
            self.setup_volumes()
        
        elif choice.startswith("🛠️"):
            self.fix_permissions()
        
        elif choice.startswith("🔍"):
            self.debug_containers()
    
    def nuclear_rebuild(self):
        """Complete rebuild with confirmation"""
        print("💀 NUCLEAR REBUILD")
        print("⚠️  This will rebuild everything from scratch!")
        
        if not questionary.confirm("Continue?").ask():
            return

        print("💀 Stopping services...")
        self.run_command("down")
        
        print("💀 Cleaning system...")
        subprocess.run(["docker", "system", "prune", "-af"], capture_output=True)
        
        print("💀 Fixing permissions...")
        self.fix_permissions()
        
        print("💀 Setting up volumes...")
        self.setup_volumes(auto_confirm=True)
        
        print("💀 Rebuilding...")
        self.run_command("build --no-cache --pull")
        self.run_command("up -d")
        
        print("✅ Nuclear rebuild completed!")
    
    def fix_permissions(self):
        """Fix common permission issues automatically"""
        print("🔧 Fixing Docker permissions...")
        
        docker_dir = self.config.docker.paths.docker_dir
        
        # Fix entrypoint.sh permissions
        entrypoint_path = docker_dir / "scripts" / "entrypoint.sh"
        if entrypoint_path.exists():
            try:
                subprocess.run(["chmod", "+x", str(entrypoint_path)], check=True, capture_output=True)
                print(f"✅ Fixed entrypoint.sh permissions: {entrypoint_path}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to fix entrypoint.sh: {e}")
        
        # Fix volumes permissions
        volumes_dir = docker_dir / "volumes"
        if volumes_dir.exists():
            try:
                subprocess.run(["sudo", "chown", "-R", f"{os.getenv('USER')}:{os.getenv('USER')}", str(volumes_dir)], 
                             check=True, capture_output=True)
                subprocess.run(["sudo", "chmod", "-R", "755", str(volumes_dir)], 
                             check=True, capture_output=True)
                print(f"✅ Fixed volumes permissions: {volumes_dir}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to fix volumes: {e}")
        
        print("🔧 Permission fixes completed!")
    
    def parse_volumes_from_compose(self) -> List[str]:
        """Parse bind mount volumes from docker-compose files"""
        volumes = []
        docker_dir = self.config.docker.paths.docker_dir
        
        # Files to parse
        compose_files = [
            docker_dir / "docker-compose.yml",
            docker_dir / "docker-compose.base.yml", 
            docker_dir / "docker-compose.apps.yml"
        ]
        
        for compose_file in compose_files:
            if not compose_file.exists():
                continue
                
            try:
                with open(compose_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                if not data or 'services' not in data:
                    continue
                
                for service_name, service_config in data['services'].items():
                    if 'volumes' not in service_config:
                        continue
                    
                    for volume in service_config['volumes']:
                        if isinstance(volume, str) and ':' in volume:
                            # Parse bind mount: ./volumes/postgres/data:/var/lib/postgresql/data
                            host_path = volume.split(':')[0].strip()
                            
                            # Convert relative paths to absolute
                            if host_path.startswith('./'):
                                host_path = docker_dir / host_path[2:]
                            elif host_path.startswith('../'):
                                host_path = docker_dir.parent / host_path[3:]
                            else:
                                host_path = Path(host_path)
                            
                            volumes.append(str(host_path))
                            
            except Exception as e:
                print(f"⚠️  Could not parse {compose_file}: {e}")
        
        return list(set(volumes))  # Remove duplicates
    
    def setup_volumes(self, auto_confirm: bool = False):
        """Auto-create volume directories from docker-compose.yml"""
        print("🔧 Setting up volumes from docker-compose files...")
        
        volumes = self.parse_volumes_from_compose()
        
        if not volumes:
            print("⚠️  No bind mount volumes found in docker-compose files")
            return

        print(f"📁 Found {len(volumes)} volume directories:")
        for volume in volumes:
            print(f"   • {volume}")
        
        if not auto_confirm and not questionary.confirm("Create missing directories and fix permissions?").ask():
            return

        created_count = 0
        fixed_count = 0
        
        for volume_path in volumes:
            path = Path(volume_path)
            
            # Create directory if it doesn't exist
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created: {path}")
                    created_count += 1
                except Exception as e:
                    print(f"❌ Failed to create {path}: {e}")
                    continue
            
            # Fix permissions
            try:
                subprocess.run(["chmod", "755", str(path)], check=True, capture_output=True)
                fixed_count += 1
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Could not fix permissions for {path}: {e}")
        
        print(f"🎯 Summary:")
        print(f"   📁 Created: {created_count} directories")
        print(f"   🔧 Fixed: {fixed_count} permissions")
        print(f"✅ Volume setup completed!")
    
    def show_docker_status(self):
        """Show Docker status"""
        containers = self.get_running_containers()
        nginx_running = self.is_nginx_running()
        
        print(f"\n🐳 UnrealOS Django Docker Status")
        print("=" * 60)
        
        # Docker health check
        if nginx_running and len(containers) >= 2:
            health_status = "🟢 HEALTHY"
        elif len(containers) >= 1:
            health_status = "🟡 PARTIAL"
        else:
            health_status = "🔴 DOWN"
        
        print(f"Docker Health: {health_status}")
        print(f"Running Services: {len(containers)}")
        print(f"Nginx Status: {'🟢 Active' if nginx_running else '🔴 Inactive'}")
        
        if containers:
            print(f"\n🐳 Docker Stack:")
            print("-" * 50)
            
            # Group services by importance
            critical_services = []
            support_services = []
            
            for service_name, status in containers.items():
                if any(x in service_name.lower() for x in ["django", "postgres", "nginx"]):
                    critical_services.append((service_name, status))
                else:
                    support_services.append((service_name, status))
            
            if critical_services:
                print("  🎯 Critical Services:")
                for service_name, status in critical_services:
                    display = self.get_service_display(service_name, status)
                    print(f"    {display}")
            
            if support_services:
                print("  🔧 Support Services:")
                for service_name, status in support_services:
                    display = self.get_service_display(service_name, status)
                    print(f"    {display}")
        else:
            print(f"\n🔴 PRODUCTION STACK IS DOWN!")
            print(f"   Run: 🏭 Start Production to deploy")
        
        if containers:
            print(f"\n🌐 Production URLs:")
            if nginx_running:
                print(f"   🏭 Public Admin: {self.config.docker.production_admin_url}")
                print(f"   🏭 Public API: {self.config.docker.production_api_url}")
                print(f"   🔧 Direct Access: {self.config.docker.development_admin_url}")
            else:
                print(f"   ⚠️  Nginx not running - no public access!")
                print(f"   🔧 Direct Access: {self.config.docker.development_admin_url}")
                print(f"   💡 Start Nginx to enable public URLs")
        
        input("\nPress Enter to continue...")
    
    def show_container_menu(self, service_name: str):
        """Container management menu - Level 2"""
        containers = self.get_running_containers()
        is_running = service_name in containers
        
        while True:
            print(f"\n🔧 Container: {service_name}")
            print(f"📊 Status: {'🟢 Running' if is_running else '🔴 Stopped'}")
            if is_running:
                print(f"📋 Info: {containers[service_name]}")
            
            actions = []
            
            if is_running:
                actions.extend([
                    "🖥️  Enter Container",
                    "📋 Show Logs",
                    "🔄 Restart Container",
                    "⏹️  Stop Container",
                    "🔨 Rebuild & Start"
                ])
                
                # Special actions for specific containers
                if "postgres" in service_name.lower():
                    actions.append("🗄️  Database Shell")
                elif "django" in service_name.lower():
                    actions.extend([
                        "🌐 Open Admin Panel",
                        "🔨 Quick Rebuild"
                    ])
            else:
                actions.extend([
                    "🚀 Start Container",
                    "🔨 Rebuild & Start"
                ])
            
            actions.append("🔙 Back")
            
            choice = questionary.select("Container Actions:", choices=actions).ask()
            
            if not choice or choice == "🔙 Back":
                break
            
            self.handle_container_action(service_name, choice)
            
            # Refresh status
            containers = self.get_running_containers()
            is_running = service_name in containers
    
    def handle_container_action(self, service_name: str, action: str):
        """Handle container-specific actions"""
        if action == "🖥️  Enter Container":
            self.enter_container(service_name)
        
        elif action == "📋 Show Logs":
            self.show_container_logs(service_name)
        
        elif action == "🔄 Restart Container":
            self.run_command("restart", service=service_name)
        
        elif action == "⏹️  Stop Container":
            self.run_command("stop", service=service_name)
        
        elif action == "🚀 Start Container":
            self.run_command("up -d", service=service_name)
        
        elif action == "🔨 Rebuild & Start":
            print(f"🔨 Rebuilding {service_name}...")
            self.run_command("stop", service=service_name)
            self.run_command("build --no-cache", service=service_name)
            self.run_command("up -d", service=service_name)
            print(f"✅ {service_name} rebuilt and started successfully!")
        
        elif action == "🔨 Quick Rebuild":
            self.quick_rebuild_container(service_name)
        
        elif action == "🗄️  Database Shell":
            self.database_shell(service_name)
        
        elif action == "🌐 Open Admin Panel":
            self.open_admin_panel()
    
    def enter_container(self, service_name: str):
        """Enter container with interactive shell"""
        print(f"🖥️  Entering container: {service_name}")
        print("💡 Use 'exit' to leave the container")
        
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(self.main_file), "ps", "-q", service_name],
                capture_output=True, text=True, check=True
            )
            
            container_id = result.stdout.strip()
            if not container_id:
                print(f"❌ Could not find container for {service_name}")
                return
            
            # Try bash first, then sh as fallback
            shells = ["/bin/bash", "/bin/sh"]
            
            for shell in shells:
                try:
                    subprocess.run(
                        ["docker", "exec", "-it", container_id, shell],
                        check=True
                    )
                    return
                except subprocess.CalledProcessError:
                    continue
            
            # If both shells fail, try without specifying shell
            subprocess.run(["docker", "exec", "-it", container_id], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to enter container: {e}")
        except KeyboardInterrupt:
            print("\n👋 Exited container")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_container_logs(self, service_name: str):
        """Show container logs"""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(self.main_file), "ps", "-q", service_name],
                capture_output=True, text=True, check=True
            )
            
            container_id = result.stdout.strip()
            if container_id:
                print(f"📋 Showing logs for {service_name} (Ctrl+C to exit)...")
                subprocess.run(["docker", "logs", "--tail", "50", "-f", container_id])
            else:
                print(f"❌ Could not find container for {service_name}")
        except KeyboardInterrupt:
            print(f"\n👋 Stopped viewing logs for {service_name}")
        except Exception as e:
            print(f"❌ Error showing logs: {e}")
    
    def quick_rebuild_container(self, service_name: str):
        """Quick rebuild single container"""
        print(f"🔨 Quick rebuild: {service_name}")
        
        # Stop and remove container
        print("🧹 Cleaning up...")
        subprocess.run(["docker", "rm", "-f", service_name], capture_output=True)
        
        # Rebuild and start
        print("🔨 Rebuilding...")
        self.run_command("build --no-cache", service=service_name)
        
        print("🚀 Starting...")
        self.run_command("up -d", service=service_name)
        
        print(f"✅ {service_name} rebuilt successfully!")
    
    def database_shell(self, service_name: str):
        """Connect to database"""
        print("🗄️  Connecting to PostgreSQL...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(self.main_file), "ps", "-q", service_name],
                capture_output=True, text=True, check=True
            )
            
            container_id = result.stdout.strip()
            if container_id:
                subprocess.run([
                    "docker", "exec", "-it", container_id, 
                    "psql", "-U", self.config.docker.postgres_user, "-d", self.config.docker.postgres_db
                ])
            else:
                print(f"❌ Container {service_name} not found")
        except KeyboardInterrupt:
            print("\n👋 Exited database shell")
        except Exception as e:
            print(f"❌ Could not connect to database: {e}")
    
    def open_admin_panel(self):
        """Open Django admin panel"""
        nginx_running = self.is_nginx_running()
        
        if nginx_running:
            url = self.config.docker.production_admin_url
            print(f"🏭 Opening Production Admin: {url}")
        else:
            url = self.config.docker.development_admin_url
            print(f"🚀 Opening Development Admin: {url}")
        
        subprocess.run(["open", url], capture_output=True)
    
    
    def run_menu(self):
        """Run Docker management menu"""
        print(f"🐳 {AppConstants.PROJECT_NAME} Docker Manager")
        print("=" * 60)

        while True:
            containers = self.get_running_containers()
            nginx_running = self.is_nginx_running()
            
            # Show Docker status
            if nginx_running and len(containers) >= 2:
                health_status = "🟢 HEALTHY"
            elif len(containers) >= 1:
                health_status = "🟡 PARTIAL"
            else:
                health_status = "🔴 DOWN"
            
            print(f"\n🐳 Docker Health: {health_status}")
            print(f"📊 Running Services: {len(containers)}")
            print(f"🌐 Nginx: {'🟢 Active' if nginx_running else '🔴 Inactive'}")
            
            # Show running containers summary
            if containers:
                critical = [s for s in containers.keys() if any(x in s.lower() for x in ["django", "postgres", "nginx"])]
                print(f"🎯 Critical: {', '.join(critical) if critical else 'None'}")
            else:
                print(f"🔴 PRODUCTION STACK DOWN - Start services!")
            
            # Build menu choices
            choices = []
            
            # Add running containers
            if containers:
                for service_name, status in containers.items():
                    display = self.get_service_display(service_name, status)
                    choices.append({"name": display, "value": service_name})

            # Add system options
            choices.extend([
                questionary.Separator("=" * 30),
                {"name": "⚡ Docker Actions", "value": "quick"},
                {"name": "📊 Docker Status", "value": "status"},
                {"name": "❌ Exit", "value": "exit"}
            ])
            
            choice = questionary.select("Select container or action:", choices=choices).ask()

            if not choice or choice == "exit":
                print("👋 Goodbye!")
                break
            elif choice == "quick":
                self.show_quick_actions()
            elif choice == "status":
                self.show_docker_status()
            else:
                # Container selected - show container menu
                self.show_container_menu(choice)


def main():
    """Main function"""
    if "--help" in sys.argv or "-h" in sys.argv:
        print(f"""
🐳 {AppConstants.PROJECT_NAME} Docker Manager

Usage:
  python3 manage.py              # Docker management menu
  python3 manage.py --help       # Show this help

Docker Features:
  🐳 Full stack deployment with Nginx
  📦 Container-level management
  📊 Docker health monitoring
  🔨 Zero-downtime rebuilds

Menu Structure:
  Level 1: Docker containers + actions
  Level 2: Container-specific operations

Docker Commands:
  🏭 Start:    docker-compose up -d
  ⏹️  Stop:     docker-compose down
  🔨 Rebuild:  docker-compose build --no-cache
""")
        return

    # Install dependencies if needed
    try:
        import questionary
    except ImportError:
        print("Installing questionary...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "questionary"])
        import questionary
    
    # Run manager
    manager = DockerManager()
    manager.run_menu()


if __name__ == "__main__":
    main()