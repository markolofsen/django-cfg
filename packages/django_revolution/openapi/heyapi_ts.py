"""
HeyAPI TypeScript Generator for Django Revolution

Generates TypeScript clients using @hey-api/openapi-ts.
"""

from pathlib import Path
from typing import Dict, Optional, Any

from ..config import DjangoRevolutionSettings, GenerationResult
from ..utils import Logger, run_command, check_dependency, ensure_directories


class HeyAPITypeScriptGenerator:
    """TypeScript client generator using @hey-api/openapi-ts."""

    def __init__(
        self, config: DjangoRevolutionSettings, logger: Optional[Logger] = None
    ):
        """
        Initialize TypeScript generator.

        Args:
            config: Django Revolution settings
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or Logger("heyapi_ts_generator")
        self.output_dir = Path(config.generators.typescript.output_directory)

    def is_available(self) -> bool:
        """
        Check if @hey-api/openapi-ts is available.

        Returns:
            bool: True if available
        """
        return check_dependency(["npx", "@hey-api/openapi-ts", "--version"])

    def generate_client(self, zone_name: str, schema_path: Path) -> GenerationResult:
        """
        Generate TypeScript client for a single zone.

        Args:
            zone_name: Name of the zone
            schema_path: Path to OpenAPI schema file

        Returns:
            GenerationResult with operation details
        """
        self.logger.info(f"Generating TypeScript client for zone: {zone_name}")

        # Validate schema file
        if not schema_path.exists():
            error_msg = f"Schema file not found: {schema_path}"
            self.logger.error(error_msg)
            return GenerationResult(
                success=False,
                zone_name=zone_name,
                output_path=Path(),
                files_generated=0,
                error_message=error_msg,
            )

        # Setup output directory
        zone_output_dir = self.output_dir / zone_name
        ensure_directories(zone_output_dir)

        try:
            # Generate TypeScript client using @hey-api/openapi-ts
            cmd = [
                "npx",
                "@hey-api/openapi-ts",
                "--input",
                str(schema_path),
                "--output",
                str(zone_output_dir),
            ]

            # Add output format option if specified
            # Note: --format option is not supported in hey-api
            pass

            # Add test generation if enabled
            # Note: --tests option is not supported in hey-api
            pass

            success, output = run_command(" ".join(cmd), timeout=120)

            if success:
                # Count generated files
                files_generated = self._count_generated_files(zone_output_dir)

                # Generate files using templates
                self._generate_from_templates(zone_name, zone_output_dir)

                # Format generated TypeScript files if enabled
                if self.config.generators.typescript.auto_format:
                    if not self._format_typescript_files(zone_output_dir):
                        self.logger.warning("⚠️ TypeScript file formatting failed, but generation succeeded")
                else:
                    self.logger.debug("TypeScript auto-formatting disabled")

                self.logger.success(
                    f"TypeScript client generated for {zone_name}: {files_generated} files"
                )

                return GenerationResult(
                    success=True,
                    zone_name=zone_name,
                    output_path=zone_output_dir,
                    files_generated=files_generated,
                    error_message="",
                )
            else:
                error_msg = f"TypeScript generation failed: {output}"
                self.logger.error(error_msg)

                return GenerationResult(
                    success=False,
                    zone_name=zone_name,
                    output_path=zone_output_dir,
                    files_generated=0,
                    error_message=error_msg,
                )

        except Exception as e:
            error_msg = f"TypeScript generation exception: {str(e)}"
            self.logger.error(error_msg)

            return GenerationResult(
                success=False,
                zone_name=zone_name,
                output_path=zone_output_dir,
                files_generated=0,
                error_message=error_msg,
            )

    def generate_all(self, schemas: Dict[str, Path]) -> Dict[str, GenerationResult]:
        """
        Generate TypeScript clients for all provided schemas.

        Args:
            schemas: Dictionary mapping zone names to schema paths

        Returns:
            Dictionary mapping zone names to generation results
        """
        if not schemas:
            self.logger.warning("No schemas provided for TypeScript generation")
            return {}

        self.logger.info(f"Generating TypeScript clients for {len(schemas)} zones")

        results = {}

        for zone_name, schema_path in schemas.items():
            result = self.generate_client(zone_name, schema_path)
            results[zone_name] = result

        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(
            f"TypeScript generation completed: {successful}/{len(results)} successful"
        )

        return results

    def _count_generated_files(self, directory: Path) -> int:
        """
        Count the number of generated files in a directory.

        Args:
            directory: Directory to count files in

        Returns:
            Number of files generated
        """
        if not directory.exists():
            return 0

        count = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                count += 1

        return count

    def _generate_from_templates(self, zone_name: str, output_dir: Path):
        """
        Generate files using Jinja2 templates.

        Args:
            zone_name: Name of the zone
            output_dir: Output directory for the client
        """
        try:
            import jinja2
            from datetime import datetime

            # Setup Jinja2 environment
            templates_dir = Path(__file__).parent / "templates" / "typescript"
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Get zone info from config
            zones = self.config.zones
            zone_info = zones.get(zone_name, {})

            # Prepare context for templates
            context = {
                "zone_name": zone_name,
                "title": zone_info.get("title", f"{zone_name.title()} API"),
                "description": zone_info.get(
                    "description", f"TypeScript client for {zone_name} zone"
                ),
                "apps": zone_info.get("apps", []),
                "generation_time": datetime.now().isoformat(),
                "version": self.config.version,
            }

            # Generate index.ts
            index_template = env.get_template("index.ts.j2")
            index_content = index_template.render(**context)
            with open(output_dir / "index.ts", "w", encoding="utf-8") as f:
                f.write(index_content)

            # Generate package.json
            package_template = env.get_template("package.json.j2")
            package_content = package_template.render(**context)
            with open(output_dir / "package.json", "w", encoding="utf-8") as f:
                f.write(package_content)

            self.logger.debug(f"Generated template files for {zone_name}")

        except ImportError:
            self.logger.warning("Jinja2 not available, skipping template generation")
        except Exception as e:
            self.logger.warning(
                f"Failed to generate template files for {zone_name}: {e}"
            )

    def clean_output(self) -> bool:
        """
        Clean TypeScript output directory.

        Returns:
            bool: True if cleaning successful
        """
        try:
            if self.output_dir.exists():
                import shutil

                shutil.rmtree(self.output_dir)

            ensure_directories(self.output_dir)
            self.logger.success("TypeScript output directory cleaned")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clean TypeScript output directory: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get TypeScript generator status.

        Returns:
            Status information dictionary
        """
        return {
            "available": self.is_available(),
            "output_directory": str(self.output_dir),
            "enabled": self.config.generators.typescript.enabled,
            "output_format": self.config.generators.typescript.output_format,
            "generate_tests": self.config.generators.typescript.generate_tests,
            "custom_templates": self.config.generators.typescript.custom_templates,
            "auto_format": self.config.generators.typescript.auto_format,
        }

    def _format_typescript_files(self, directory: Path) -> bool:
        """
        Format TypeScript files using Prettier.
        
        Args:
            directory: Directory containing TypeScript files
            
        Returns:
            bool: True if formatting succeeded, False otherwise
        """
        try:
            # Check if prettier is available - run from django_revolution directory
            config_dir = Path(__file__).parent.parent
            success, output = run_command("npx prettier --version", timeout=10, cwd=config_dir)
            if not success:
                self.logger.warning("Prettier not available, skipping TypeScript formatting")
                return True
            
            # Format TypeScript files
            ts_files = list(directory.glob("**/*.ts")) + list(directory.glob("**/*.tsx"))
            if ts_files:
                self.logger.info(f"🎨 Formatting {len(ts_files)} TypeScript files...")
                
                # Format all TypeScript files in the directory using config
                config_dir = Path(__file__).parent.parent
                prettierrc_path = config_dir / ".prettierrc"
                
                # Get all TypeScript files to format
                ts_file_paths = [str(f) for f in ts_files if f.is_file()]
                
                if ts_file_paths:
                    if prettierrc_path.exists():
                        command_parts = ["npx", "prettier", "--config", str(prettierrc_path), "--write"] + ts_file_paths
                    else:
                        command_parts = ["npx", "prettier", "--write"] + ts_file_paths
                    
                    command = " ".join(f'"{part}"' if " " in part else part for part in command_parts)
                    success, output = run_command(command, cwd=config_dir, timeout=60)
                else:
                    self.logger.debug("No TypeScript files found to format")
                    return True
                
                if success:
                    self.logger.info("✅ TypeScript files formatted successfully")
                    return True
                else:
                    self.logger.warning(f"⚠️ TypeScript formatting failed: {output}")
                    return False
            else:
                self.logger.debug("No TypeScript files to format")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to format TypeScript files: {e}")
            return False
