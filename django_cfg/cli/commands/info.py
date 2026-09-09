"""
Django CFG Info Command

Shows information about django-cfg installation and available features.
"""

import click

from ..utils import (
    check_dependencies,
    get_package_info,
    get_standard_dependencies,
    get_template_info,
)


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def info(verbose: bool):
    """
    📋 Show django-cfg installation and system information
    
    Displays version, installation path, available features,
    and optional dependency status.
    """

    click.echo("🚀 Django CFG - Production-ready Django Configuration Framework")
    click.echo("=" * 70)

    # Package information
    package_info = get_package_info()
    if not package_info["installed"]:
        click.echo("❌ django-cfg not found or not properly installed")
        return

    click.echo(f"📦 Version: {package_info['version']}")
    click.echo(f"🐍 Python: {package_info['python_version']}")
    if verbose and package_info['path']:
        click.echo(f"📁 Installation: {package_info['path']}")

    click.echo()

    # Template information
    template_info = get_template_info()
    click.echo("📋 Project Template:")

    if template_info["available"]:
        template_name = template_info['name']
        if template_info["type"] == "archive":
            size_info = f" ({template_info.get('size_kb', 0):.1f} KB, {template_info.get('file_count', 0)} files)"
            status = "✅" if template_info.get("is_valid", True) else "⚠️ "
            click.echo(f"   {status} {template_name} archive - Available{size_info}")
        else:
            click.echo(f"   ✅ {template_name} - Available")

        if verbose and template_info['path']:
            click.echo(f"   📁 Path: {template_info['path']}")
            if template_info["type"] == "archive":
                click.echo("   📦 Type: ZIP Archive")
                if "size_bytes" in template_info:
                    click.echo(f"   📏 Size: {template_info['size_bytes']} bytes")
    else:
        click.echo("   ❌ Template archive not found")
        click.echo("   💡 Run: python scripts/template_manager.py create")

    click.echo()

    # Dependencies check
    deps = check_dependencies(get_standard_dependencies())

    # Group dependencies by category
    categories = {
        "🔧 Core Dependencies": ["django", "pydantic", "pydantic-yaml", "click"],
        "🌐 Service Integrations": ["openai", "telegram-bot-api"],
        "🎨 Admin & UI": ["django-unfold", "django-constance"],
        "📊 API & Documentation": ["djangorestframework", "drf-spectacular"],
        "⚡ Background Processing": ["rearq", "redis"],
    }

    for category, dep_list in categories.items():
        click.echo(f"{category}:")
        category_deps = {dep: deps.get(dep, False) for dep in dep_list}

        # Show installed first, then missing
        for dep, is_installed in category_deps.items():
            if is_installed:
                status = "✅" if dep in ["django", "pydantic", "pydantic-yaml", "click"] else "✅"
                click.echo(f"   {status} {dep}")

        for dep, is_installed in category_deps.items():
            if not is_installed:
                status = "❌" if dep in ["django", "pydantic", "pydantic-yaml", "click"] else "⚪"
                click.echo(f"   {status} {dep}")

        click.echo()

    # Legend
    click.echo("Legend:")
    click.echo("   ✅ Installed and available")
    click.echo("   ⚪ Optional - not installed")
    click.echo("   ❌ Required - missing")

    click.echo()

    # Available commands
    click.echo("🎯 Available Commands:")
    click.echo("   django-cfg create-project <name>  - Create new Django project")
    click.echo("   django-cfg info                   - Show this information")
    click.echo("   django-cfg --help                 - Show help")

    click.echo()

    # Quick start
    click.echo("🚀 Quick Start:")
    click.echo("   # Create a new project")
    click.echo("   django-cfg create-project 'My Awesome Project'")
    click.echo()
    click.echo("   # Install optional dependencies")
    click.echo("   pip install django-unfold")
    click.echo()
    click.echo("📚 Documentation: https://djangocfg.com")
    click.echo("🐙 GitHub: https://github.com/markolofsen/django-cfg")

    # Warnings for missing critical dependencies
    missing_critical = [dep for dep in ["django", "pydantic"] if not deps.get(dep, False)]
    if missing_critical:
        click.echo()
        click.echo("⚠️  Warning: Missing critical dependencies:")
        for dep in missing_critical:
            click.echo(f"   pip install {dep}")
