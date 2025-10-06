"""
OpenAPI Generator for Django Revolution

Main coordinator for generating OpenAPI schemas and client libraries.
"""

import time
import shutil
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import jinja2
from datetime import datetime

from ..config import DjangoRevolutionSettings, GenerationResult, GenerationSummary
from ..zones import ZoneManager, ZoneDetector
from ..utils import (
    Logger,
    ErrorHandler,
    ensure_directories,
    get_django_manage_py,
    run_command,
)
from .heyapi_ts import HeyAPITypeScriptGenerator
from .python_client import PythonClientGenerator
from .archive_manager import ArchiveManager
from .schema_postprocessor import SchemaPostprocessor


class OpenAPIGenerator:
    """Main OpenAPI generator coordinating all processes."""

    def __init__(self, config: Optional[DjangoRevolutionSettings] = None):
        """
        Initialize the OpenAPI generator.

        Args:
            config: Optional configuration. If None, will load from settings.
        """
        from ..config import get_settings

        self.config = config or get_settings()
        self.logger = Logger("openapi_generator")
        self.error_handler = ErrorHandler(self.logger)

        # Initialize components
        self.zone_manager = ZoneManager(self.config)
        self.zone_detector = ZoneDetector(self.config, self.logger)

        # Setup output directories
        self.output_dir = Path(self.config.output.base_directory)
        self._setup_directories()

        # Initialize generators
        self.ts_generator = HeyAPITypeScriptGenerator(self.config, self.logger)
        self.python_generator = PythonClientGenerator(self.config, self.logger)

        # Initialize additional services
        self.archive_manager = ArchiveManager(self.config, self.logger, self.output_dir)
        self.schema_postprocessor = SchemaPostprocessor(self.logger)

        self.logger.info("OpenAPI Generator initialized")

    def _setup_directories(self):
        """Setup output directories based on configuration."""
        directories = [
            self.output_dir / self.config.output.schemas_directory,
            self.output_dir / self.config.output.clients_directory / "typescript",
            self.output_dir / self.config.output.clients_directory / "python",
            self.output_dir / self.config.output.temp_directory,
            Path(self.config.generators.typescript.output_directory),
            Path(self.config.generators.python.output_directory),
        ]

        ensure_directories(*directories)
        self.logger.debug("Output directories created")

    def validate_environment(self) -> bool:
        """
        Validate that the environment is ready for generation.

        Returns:
            bool: True if environment is valid
        """
        self.logger.info("Validating environment...")

        # Check if zones are available
        zones = self.zone_manager.zones
        if not zones:
            self.logger.error("No zones configured")
            return False

        # Check TypeScript generator if enabled
        if self.config.generators.typescript.enabled:
            if not self.ts_generator.is_available():
                self.logger.warning("TypeScript generator not available")
                if self.config.auto_install_deps:
                    from ..utils import auto_install_dependencies

                    auto_install_dependencies()

        # Check Python generator if enabled
        if self.config.generators.python.enabled:
            if not self.python_generator.is_openapi_generator_available():
                self.logger.warning("Modern Python generator not available")
                if self.config.auto_install_deps:
                    from ..utils import auto_install_dependencies

                    auto_install_dependencies()

        self.logger.success("Environment validation completed")
        return True

    def _generate_single_schema(
        self, zone_name: str, zone, schemas_dir: Path, manage_py: Path
    ) -> Tuple[str, Optional[Path]]:
        """
        Generate schema for a single zone.

        Args:
            zone_name: Name of the zone
            zone: Zone configuration
            schemas_dir: Directory for schemas
            manage_py: Path to Django manage.py

        Returns:
            Tuple of (zone_name, schema_file_path or None)
        """
        try:
            self.logger.info(f"Generating schema for zone: {zone_name}")

            # Schema file path
            schema_file = schemas_dir / f"{zone_name}.yaml"

            # Create URLconf for this zone
            urlconf_module = self.zone_manager.create_dynamic_urlconf_module(
                zone_name, zone
            )

            if not urlconf_module:
                self.logger.error(f"Failed to create URLconf for {zone_name}")
                return zone_name, None

            # Generate schema using drf-spectacular
            import sys
            cmd = [
                sys.executable,
                str(manage_py),
                "spectacular",
                "--file",
                str(schema_file),
                "--api-version",
                zone.version,
                "--urlconf",
                urlconf_module.__name__,
            ]

            success, output = run_command(" ".join(cmd), timeout=60)

            if success and schema_file.exists():
                # Postprocess schema to fix COMPONENT_SPLIT issues
                if self.schema_postprocessor.process_schema_file(schema_file):
                    self.logger.success(f"Schema generated and postprocessed: {schema_file}")
                else:
                    self.logger.warning(f"Schema generated but postprocessing failed: {schema_file}")

                return zone_name, schema_file
            else:
                self.logger.error(f"Schema generation failed for {zone_name}: {output}")
                return zone_name, None

        except Exception as e:
            self.logger.error(f"Exception generating schema for {zone_name}: {e}")
            return zone_name, None

    def generate_schemas(self, zones: Optional[List[str]] = None) -> Dict[str, Path]:
        """
        Generate OpenAPI schemas for zones using drf-spectacular with multithreading support.

        Args:
            zones: Optional list of zone names. If None, generates for all zones.

        Returns:
            Dictionary mapping zone names to schema file paths
        """
        self.logger.info("Generating OpenAPI schemas...")

        # Get zones to process
        all_zones = self.zone_manager.zones
        if zones:
            zones_to_process = {
                name: zone for name, zone in all_zones.items() if name in zones
            }
        else:
            zones_to_process = all_zones

        if not zones_to_process:
            self.logger.warning("No zones to process")
            return {}

        # Create schemas directory
        schemas_dir = self.output_dir / self.config.output.schemas_directory
        schemas_dir.mkdir(parents=True, exist_ok=True)

        # Find Django manage.py
        manage_py = get_django_manage_py()
        if not manage_py:
            self.logger.error("Django manage.py not found")
            return {}

        generated_schemas = {}

        # Check if multithreading is enabled and we have multiple zones
        if (
            self.config.enable_multithreading
            and len(zones_to_process) > 1
            and self.config.max_workers > 1
        ):

            self.logger.info(
                f"Using multithreaded generation with {self.config.max_workers} workers for {len(zones_to_process)} zones"
            )

            # Use ThreadPoolExecutor for concurrent schema generation
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self.config.max_workers, len(zones_to_process))
            ) as executor:

                # Submit all schema generation tasks
                future_to_zone = {
                    executor.submit(
                        self._generate_single_schema,
                        zone_name,
                        zone,
                        schemas_dir,
                        manage_py,
                    ): zone_name
                    for zone_name, zone in zones_to_process.items()
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_zone):
                    zone_name = future_to_zone[future]
                    try:
                        zone_name_result, schema_file = future.result()
                        if schema_file:
                            generated_schemas[zone_name_result] = schema_file
                    except Exception as e:
                        self.logger.error(
                            f"Exception in thread for zone {zone_name}: {e}"
                        )
        else:
            # Fallback to sequential generation
            if len(zones_to_process) == 1:
                self.logger.info("Single zone detected, using sequential generation")
            elif not self.config.enable_multithreading:
                self.logger.info("Multithreading disabled, using sequential generation")
            else:
                self.logger.info("Using sequential generation")

            for zone_name, zone in zones_to_process.items():
                zone_name_result, schema_file = self._generate_single_schema(
                    zone_name, zone, schemas_dir, manage_py
                )
                if schema_file:
                    generated_schemas[zone_name_result] = schema_file

        self.logger.info(f"Generated {len(generated_schemas)} schemas")
        return generated_schemas

    def generate_typescript_clients(
        self,
        schemas: Optional[Dict[str, Path]] = None,
        zones: Optional[List[str]] = None,
    ) -> Dict[str, GenerationResult]:
        """
        Generate TypeScript clients for zones with multithreading support.

        Args:
            schemas: Optional dictionary of zone schemas
            zones: Optional list of zone names

        Returns:
            Dictionary of generation results
        """
        if not self.config.generators.typescript.enabled:
            self.logger.info("TypeScript generation disabled")
            return {}

        self.logger.info("Generating TypeScript clients...")

        # Generate schemas if not provided
        if schemas is None:
            schemas = self.generate_schemas(zones)

        # Check if multithreading is enabled and we have multiple schemas
        if (
            self.config.enable_multithreading
            and len(schemas) > 1
            and self.config.max_workers > 1
        ):

            self.logger.info(
                f"Using multithreaded TypeScript generation with {self.config.max_workers} workers for {len(schemas)} schemas"
            )

            # Use ThreadPoolExecutor for concurrent client generation
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self.config.max_workers, len(schemas))
            ) as executor:

                # Submit all client generation tasks
                future_to_zone = {
                    executor.submit(
                        self.ts_generator.generate_client, zone_name, schema_path
                    ): zone_name
                    for zone_name, schema_path in schemas.items()
                }

                # Collect results as they complete
                results = {}
                for future in concurrent.futures.as_completed(future_to_zone):
                    zone_name = future_to_zone[future]
                    try:
                        result = future.result()
                        results[zone_name] = result
                    except Exception as e:
                        self.logger.error(
                            f"Exception in TypeScript thread for zone {zone_name}: {e}"
                        )
                        # Create failed result
                        results[zone_name] = GenerationResult(
                            success=False,
                            zone_name=zone_name,
                            output_path=Path(),
                            files_generated=0,
                            error_message=str(e),
                        )
        else:
            # Fallback to sequential generation
            if len(schemas) == 1:
                self.logger.info(
                    "Single schema detected, using sequential TypeScript generation"
                )
            elif not self.config.enable_multithreading:
                self.logger.info(
                    "Multithreading disabled, using sequential TypeScript generation"
                )
            else:
                self.logger.info("Using sequential TypeScript generation")

            results = self.ts_generator.generate_all(schemas)

        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(
            f"TypeScript generation completed: {successful}/{len(results)} successful"
        )

        return results

    def generate_python_clients(
        self,
        schemas: Optional[Dict[str, Path]] = None,
        zones: Optional[List[str]] = None,
    ) -> Dict[str, GenerationResult]:
        """
        Generate Python clients for zones with multithreading support.

        Args:
            schemas: Optional dictionary of zone schemas
            zones: Optional list of zone names

        Returns:
            Dictionary of generation results
        """
        if not self.config.generators.python.enabled:
            self.logger.info("Python generation disabled")
            return {}

        self.logger.info("Generating Python clients...")

        # Generate schemas if not provided
        if schemas is None:
            schemas = self.generate_schemas(zones)

        # Check if multithreading is enabled and we have multiple schemas
        if (
            self.config.enable_multithreading
            and len(schemas) > 1
            and self.config.max_workers > 1
        ):

            self.logger.info(
                f"Using multithreaded Python generation with {self.config.max_workers} workers for {len(schemas)} schemas"
            )

            # Use ThreadPoolExecutor for concurrent client generation
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self.config.max_workers, len(schemas))
            ) as executor:

                # Submit all client generation tasks
                future_to_zone = {
                    executor.submit(
                        self.python_generator.generate_client, zone_name, schema_path
                    ): zone_name
                    for zone_name, schema_path in schemas.items()
                }

                # Collect results as they complete
                results = {}
                for future in concurrent.futures.as_completed(future_to_zone):
                    zone_name = future_to_zone[future]
                    try:
                        result = future.result()
                        results[zone_name] = result
                    except Exception as e:
                        self.logger.error(
                            f"Exception in Python thread for zone {zone_name}: {e}"
                        )
                        # Create failed result
                        results[zone_name] = GenerationResult(
                            success=False,
                            zone_name=zone_name,
                            output_path=Path(),
                            files_generated=0,
                            error_message=str(e),
                        )
        else:
            # Fallback to sequential generation
            if len(schemas) == 1:
                self.logger.info(
                    "Single schema detected, using sequential Python generation"
                )
            elif not self.config.enable_multithreading:
                self.logger.info(
                    "Multithreading disabled, using sequential Python generation"
                )
            else:
                self.logger.info("Using sequential Python generation")

            results = self.python_generator.generate_all(schemas)

        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(
            f"Python generation completed: {successful}/{len(results)} successful"
        )

        return results

    def archive_clients(
        self,
        typescript_results: Dict[str, GenerationResult],
        python_results: Dict[str, GenerationResult],
    ) -> Dict[str, any]:
        """
        Archive generated clients.

        Args:
            typescript_results: TypeScript generation results
            python_results: Python generation results

        Returns:
            Archive operation results
        """
        self.logger.info("Archiving generated clients...")

        clients_dir = self.output_dir / self.config.output.clients_directory
        return self.archive_manager.archive_all_clients(
            clients_dir, typescript_results, python_results
        )





    def generate_all(
        self, zones: Optional[List[str]] = None, archive: bool = True
    ) -> GenerationSummary:
        """
        Generate all clients for specified zones.

        Args:
            zones: Optional list of zone names. If None, generates for all zones.
            archive: Whether to archive generated clients

        Returns:
            GenerationSummary with results
        """
        start_time = time.time()

        self.logger.info("Starting complete OpenAPI client generation...")

        # Validate environment
        if not self.validate_environment():
            return GenerationSummary(
                total_zones=0,
                successful_typescript=0,
                successful_python=0,
                failed_typescript=0,
                failed_python=0,
                total_files_generated=0,
                duration_seconds=time.time() - start_time,
                typescript_results={},
                python_results={},
            )

        # Get zones to process
        all_zones = self.zone_manager.zones
        if zones:
            zones_to_process = {
                name: zone for name, zone in all_zones.items() if name in zones
            }
            if not zones_to_process:
                self.logger.error(f"None of the specified zones found: {zones}")
                return GenerationSummary(
                    total_zones=0,
                    successful_typescript=0,
                    successful_python=0,
                    failed_typescript=0,
                    failed_python=0,
                    total_files_generated=0,
                    duration_seconds=time.time() - start_time,
                    typescript_results={},
                    python_results={},
                )
        else:
            zones_to_process = all_zones

        self.logger.info(
            f"Processing {len(zones_to_process)} zones: {list(zones_to_process.keys())}"
        )

        # Clean output directories
        self.clean_output()

        # Generate schemas
        schemas = self.generate_schemas(list(zones_to_process.keys()))

        # Generate TypeScript and Python clients in parallel if multithreading is enabled
        if (
            self.config.enable_multithreading
            and len(schemas) > 1
            and self.config.max_workers > 1
        ):

            self.logger.info(
                f"Using multithreaded client generation with {self.config.max_workers} workers"
            )

            # Use ThreadPoolExecutor for concurrent client generation
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(
                    self.config.max_workers, len(schemas) * 2
                )  # *2 for TS + Python
            ) as executor:

                # Submit TypeScript generation tasks
                ts_futures = {
                    executor.submit(
                        self.generate_typescript_clients, {zone: schemas[zone]}, [zone]
                    ): f"ts_{zone}"
                    for zone in schemas.keys()
                }

                # Submit Python generation tasks
                py_futures = {
                    executor.submit(
                        self.generate_python_clients, {zone: schemas[zone]}, [zone]
                    ): f"py_{zone}"
                    for zone in schemas.keys()
                }

                # Combine all futures
                all_futures = {**ts_futures, **py_futures}

                # Collect results
                typescript_results = {}
                python_results = {}

                for future in concurrent.futures.as_completed(all_futures):
                    task_name = all_futures[future]
                    try:
                        result = future.result()
                        if task_name.startswith("ts_"):
                            zone = task_name[3:]  # Remove "ts_" prefix
                            typescript_results[zone] = result.get(
                                zone,
                                GenerationResult(
                                    success=False,
                                    zone_name=zone,
                                    output_path=Path(),
                                    files_generated=0,
                                    error_message="No result returned",
                                ),
                            )
                        elif task_name.startswith("py_"):
                            zone = task_name[3:]  # Remove "py_" prefix
                            python_results[zone] = result.get(
                                zone,
                                GenerationResult(
                                    success=False,
                                    zone_name=zone,
                                    output_path=Path(),
                                    files_generated=0,
                                    error_message="No result returned",
                                ),
                            )
                    except Exception as e:
                        self.logger.error(
                            f"Exception in client generation thread for {task_name}: {e}"
                        )
                        zone = task_name[3:]  # Remove prefix
                        failed_result = GenerationResult(
                            success=False,
                            zone_name=zone,
                            output_path=Path(),
                            files_generated=0,
                            error_message=str(e),
                        )
                        if task_name.startswith("ts_"):
                            typescript_results[zone] = failed_result
                        else:
                            python_results[zone] = failed_result
        else:
            # Sequential generation
            self.logger.info("Using sequential client generation")

            # Generate TypeScript clients
            typescript_results = self.generate_typescript_clients(schemas)

            # Generate Python clients
            python_results = self.generate_python_clients(schemas)

        # Generate consolidated index.ts AFTER all clients are generated
        self.logger.info("Generating consolidated index.ts for all zones...")
        self._generate_consolidated_index(list(zones_to_process.keys()))

        # Archive clients if requested
        if archive:
            self.archive_clients(typescript_results, python_results)

        # Calculate summary
        successful_typescript = sum(1 for r in typescript_results.values() if r.success)
        failed_typescript = len(typescript_results) - successful_typescript

        successful_python = sum(1 for r in python_results.values() if r.success)
        failed_python = len(python_results) - successful_python

        total_files = sum(
            r.files_generated for r in typescript_results.values() if r.success
        ) + sum(r.files_generated for r in python_results.values() if r.success)

        duration = time.time() - start_time

        summary = GenerationSummary(
            total_zones=len(zones_to_process),
            successful_typescript=successful_typescript,
            successful_python=successful_python,
            failed_typescript=failed_typescript,
            failed_python=failed_python,
            total_files_generated=total_files,
            duration_seconds=duration,
            typescript_results=typescript_results,
            python_results=python_results,
        )

        # Log final summary
        self.logger.success(
            f"Generation completed in {duration:.1f}s: "
            f"{successful_typescript} TypeScript, {successful_python} Python, "
            f"{total_files} total files"
        )

        return summary

    def clean_output(self) -> bool:
        """
        Clean output directories.

        Returns:
            bool: True if cleaning successful
        """
        try:
            # Clean main output directory
            if self.output_dir.exists():
                # Keep certain files/directories
                keep_patterns = [".gitkeep", "README.md"]

                for item in self.output_dir.iterdir():
                    if any(item.match(pattern) for pattern in keep_patterns):
                        continue

                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            # Recreate directories
            self._setup_directories()

            self.logger.success("Output directories cleaned")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clean output directories: {e}")
            return False

    def _generate_consolidated_index(self, zones: List[str]):
        """
        Generate consolidated index.ts for all zones.

        Args:
            zones: List of zone names
        """
        try:
            

            def camelcase(name: str) -> str:
                """Convert snake_case to camelCase."""
                parts = name.split("_")
                return parts[0] + "".join(part.title() for part in parts[1:])

            # Setup Jinja2 environment
            templates_dir = Path(__file__).parent / "templates" / "typescript"
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Prepare context
            context = {
                "zones": zones,
                "generation_time": datetime.now().isoformat(),
                "camelcase": camelcase,
            }

            # Render template
            template = env.get_template("index_consolidated.ts.j2")
            index_content = template.render(**context)

            # Write consolidated index.ts
            ts_output_dir = (
                self.output_dir / self.config.output.clients_directory / "typescript"
            )
            with open(ts_output_dir / "index.ts", "w", encoding="utf-8") as f:
                f.write(index_content)

            self.logger.success(
                f"Consolidated index.ts generated for all zones: {zones}"
            )

        except ImportError:
            self.logger.warning(
                "Jinja2 not available, skipping consolidated index generation"
            )
        except Exception as e:
            self.logger.error(f"Failed to generate consolidated index.ts: {e}")

    def get_status(self) -> Dict[str, any]:
        """
        Get current generator status.

        Returns:
            Dictionary with status information
        """
        zones = self.zone_manager.zones

        return {
            "zones_detected": len(zones),
            "zones": {name: zone.model_dump() for name, zone in zones.items()},
            "typescript_available": (
                self.ts_generator.is_available()
                if self.config.generators.typescript.enabled
                else False
            ),
            "python_available": (
                self.python_generator.is_openapi_generator_available()
                if self.config.generators.python.enabled
                else False
            ),
            "output_dir": str(self.output_dir),
            "config": self.config.to_dict(),
            "multithreading": {
                "enabled": self.config.enable_multithreading,
                "max_workers": self.config.max_workers,
                "threading_available": True,  # Python's threading is always available
            },
        }
