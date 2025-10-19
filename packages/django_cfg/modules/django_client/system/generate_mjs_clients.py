#!/usr/bin/env python3
"""
Script to generate lightweight MJS (ES Module) clients for django-cfg project.

This script generates JavaScript ES modules with JSDoc type annotations
organized by Django apps for use in Django HTML templates.

Usage:
    poetry run python src/django_cfg/modules/django_client/system/generate_mjs_clients.py
    poetry run python src/django_cfg/modules/django_client/system/generate_mjs_clients.py --clean
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mjs_generator import MJSGenerator


def main():
    """Main function to generate MJS clients."""

    parser = argparse.ArgumentParser(
        description='Generate MJS API clients with JSDoc types for django-cfg project'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean existing files before generation'
    )
    parser.add_argument(
        '--schema',
        type=str,
        help='Path to OpenAPI schema file (YAML or JSON)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for generated clients'
    )

    args = parser.parse_args()

    # Determine paths
    script_dir = Path(__file__).parent
    django_client_dir = script_dir.parent  # django_client module
    modules_dir = django_client_dir.parent  # modules
    django_cfg_dir = modules_dir.parent  # django_cfg
    src_dir = django_cfg_dir.parent  # src
    dev_dir = src_dir.parent  # django-cfg-dev
    example_django_dir = dev_dir.parent / "django-cfg-example" / "django"

    # Output directory for MJS clients
    if args.output:
        mjs_output_dir = Path(args.output)
    else:
        mjs_output_dir = django_cfg_dir / "static" / "js" / "api"

    # Schema location
    if args.schema:
        schema_path = Path(args.schema)
    else:
        schema_path = example_django_dir / "openapi" / "schemas" / "cfg.yaml"

    print("🚀 Generating MJS API clients with JSDoc type annotations...")
    print(f"📁 Schema: {schema_path}")
    print(f"📁 Output: {mjs_output_dir}")

    # Generate schema if it doesn't exist
    if not schema_path.exists():
        print("⚙️  Generating OpenAPI schema first...")
        os.chdir(example_django_dir)

        result = subprocess.run(
            ["poetry", "run", "python", "manage.py", "generate_client", "--typescript", "--no-python"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0 or not schema_path.exists():
            print("❌ Error: Could not generate schema")
            print(result.stderr)
            sys.exit(1)

    # Check for dependencies
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML is required. Install with: pip install pyyaml")
        sys.exit(1)

    try:
        import jinja2
    except ImportError:
        print("❌ Jinja2 is required. Install with: pip install jinja2")
        sys.exit(1)

    # Generate MJS clients
    try:
        generator = MJSGenerator(schema_path, mjs_output_dir)
        file_count = generator.generate()

        print("\n✅ MJS clients generated successfully!")
        print(f"📊 Generated {file_count} files in {mjs_output_dir}")
        print("📂 Structure: Organized by Django apps with JSDoc types")

        # Clean up openapi directory if it was created
        openapi_dir = example_django_dir / "openapi"
        if openapi_dir.exists():
            print(f"🧹 Cleaning up example project openapi directory: {openapi_dir}")
            shutil.rmtree(openapi_dir)

        print("\n📝 Usage examples in Django template:")
        print("""
    <!-- Import from app folder with type support -->
    <script type="module">
        // Your IDE will provide autocomplete and type hints!
        import { tasksAPI } from '{% static "api/tasks/index.mjs" %}';

        async function loadTaskStats() {
            try {
                // IDE knows the return type from JSDoc annotations
                const stats = await tasksAPI.cfgTasksApiTasksStatsRetrieve();
                console.log('Task Stats:', stats);
            } catch (error) {
                // APIError type is documented
                console.error('Error:', error);
            }
        }

        loadTaskStats();
    </script>

    <!-- Import multiple APIs from main index -->
    <script type="module">
        import { tasksAPI, paymentsAPI } from '{% static "api/index.mjs" %}';

        // Both APIs have full JSDoc documentation
        const tasks = await tasksAPI.cfgTasksApiTasksStatsRetrieve();
        const webhooks = await paymentsAPI.cfgPaymentsWebhooksHealthRetrieve();
    </script>

    <!-- Use with custom base URL -->
    <script type="module">
        import { TasksAPI } from '{% static "api/tasks/index.mjs" %}';

        // Constructor is documented with JSDoc
        const api = new TasksAPI('https://api.example.com');
        const stats = await api.cfgTasksApiTasksStatsRetrieve();
    </script>
        """)

        print("\n🎯 Benefits of JSDoc types:")
        print("   • IDE autocomplete and IntelliSense")
        print("   • Type checking in VS Code and other editors")
        print("   • Inline documentation in your editor")
        print("   • Works with TypeScript if needed")
        print("   • No build step required!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
