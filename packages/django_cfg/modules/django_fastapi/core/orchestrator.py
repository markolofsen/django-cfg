"""
FastAPI ORM Generation Orchestrator.

Coordinates the full generation pipeline from Django models to FastAPI code.
"""

import logging
from pathlib import Path
from typing import Optional

from .ir.models import GeneratedFile, GenerationResult
from .parser import DjangoModelParser
from .generator import (
    GeneratorContext,
    SQLModelGenerator,
    SchemasGenerator,
    CRUDGenerator,
    DatabaseConfigGenerator,
)
from ..config import FastAPIConfig

logger = logging.getLogger(__name__)


class FastAPIOrchestrator:
    """
    Orchestrates the FastAPI ORM code generation pipeline.

    Coordinates:
    - Django model parsing
    - SQLModel generation
    - Pydantic schema generation
    - CRUD repository generation
    - Database configuration

    Example:
        config = FastAPIConfig(output_dir="fastapi/")
        orchestrator = FastAPIOrchestrator(config)
        result = orchestrator.generate()
    """

    def __init__(
        self,
        config: Optional[FastAPIConfig] = None,
        output_dir: Optional[Path] = None,
        dry_run: bool = False,
    ):
        """
        Initialize the orchestrator.

        Args:
            config: FastAPI generation configuration
            output_dir: Override output directory
            dry_run: If True, don't write files
        """
        self.config = config or FastAPIConfig()
        if output_dir:
            self.config.output_dir = str(output_dir)
        self.dry_run = dry_run

        # Initialize parser
        self.parser = DjangoModelParser(
            exclude_models=set(self.config.exclude_models),
        )

    def generate(
        self,
        apps: Optional[list[str]] = None,
    ) -> GenerationResult:
        """
        Execute the full generation pipeline.

        Args:
            apps: Specific apps to process (overrides config.apps)

        Returns:
            GenerationResult with generated files and stats
        """
        logger.info("Starting FastAPI ORM generation...")
        errors: list[str] = []
        warnings: list[str] = []

        # Determine which apps to process
        target_apps = apps if apps else (self.config.apps or None)

        # 1. Parse Django models
        logger.info("Parsing Django models...")
        try:
            models = self.parser.parse_apps(
                app_labels=target_apps,
                exclude_apps=self.config.exclude_apps,
            )
            logger.info(f"Parsed {len(models)} models")
        except Exception as e:
            error_msg = f"Failed to parse Django models: {e}"
            logger.error(error_msg)
            return GenerationResult(
                models_count=0,
                files=[],
                errors=[error_msg],
            )

        if not models:
            warnings.append("No models found to generate")
            return GenerationResult(
                models_count=0,
                files=[],
                warnings=warnings,
            )

        # 2. Create generator context
        context = GeneratorContext(
            config=self.config,
            models=models,
        )

        # 3. Run generators
        all_files: list[GeneratedFile] = []

        # SQLModel models
        logger.info("Generating SQLModel models...")
        model_gen = SQLModelGenerator(context)
        all_files.extend(model_gen.generate())

        # Pydantic schemas
        if self.config.include_schemas:
            logger.info("Generating Pydantic schemas...")
            schema_gen = SchemasGenerator(context)
            all_files.extend(schema_gen.generate())

        # CRUD repositories
        if self.config.include_crud:
            logger.info("Generating CRUD repositories...")
            crud_gen = CRUDGenerator(context)
            all_files.extend(crud_gen.generate())

        # Database configuration
        if self.config.include_database_config:
            logger.info("Generating database configuration...")
            db_gen = DatabaseConfigGenerator(context)
            all_files.extend(db_gen.generate())

        # 4. Create root __init__.py
        root_init = self._generate_root_init(models, context)
        all_files.append(root_init)

        # 5. Create CLAUDE.md instructions file
        claude_md = self._generate_claude_md(models, context)
        all_files.append(claude_md)

        # 6. Write files (unless dry_run)
        if not self.dry_run:
            self._write_files(all_files)
            logger.info(f"Wrote {len(all_files)} files to {self.config.output_dir}")
        else:
            logger.info(f"Dry run: would write {len(all_files)} files")

        return GenerationResult(
            models_count=len(models),
            files=all_files,
            errors=errors,
            warnings=warnings,
        )

    def _generate_root_init(self, models, context: GeneratorContext) -> GeneratedFile:
        """Generate root __init__.py with all exports."""
        apps = list(context.group_models_by_app().keys())

        # Track model names to detect duplicates
        seen_names: dict[str, str] = {}  # model_name -> app_label
        duplicates: set[str] = set()

        for model in models:
            if model.name in seen_names:
                duplicates.add(model.name)
            seen_names[model.name] = model.app_label

        lines = [
            '"""',
            "FastAPI ORM - Auto-generated code.",
            "",
            "Generated by django-cfg FastAPI ORM Generator.",
            '"""',
            "",
            "# Database",
            "from .database import get_session, init_db",
            "",
            "# Models by app",
        ]

        all_exports = ["get_session", "init_db"]

        for app in sorted(apps):
            app_models = [m.name for m in models if m.app_label == app]
            if app_models:
                imports_parts = []
                for model_name in app_models:
                    if model_name in duplicates:
                        # Use alias for duplicates: Currency -> CfgCurrency
                        alias = f"{self._to_camel_case(app)}{model_name}"
                        imports_parts.append(f"{model_name} as {alias}")
                        all_exports.append(alias)
                    else:
                        imports_parts.append(model_name)
                        all_exports.append(model_name)

                lines.append(f"from .{app}.models import {', '.join(imports_parts)}")

        lines.append("")
        lines.append("__all__ = [")
        for export in all_exports:
            lines.append(f'    "{export}",')
        lines.append("]")

        return GeneratedFile(
            path=Path(self.config.output_dir) / "__init__.py",
            content="\n".join(lines),
        )

    def _generate_claude_md(self, models, context: GeneratorContext) -> GeneratedFile:
        """Generate CLAUDE.md with instructions for AI assistants."""
        from datetime import datetime

        app_list = sorted(context.group_models_by_app().keys())
        model_count = len(models)

        content = f'''# Auto-Generated FastAPI ORM

> **DO NOT MODIFY THESE FILES MANUALLY**
>
> This directory contains auto-generated SQLModel ORM code.
> Any manual changes will be overwritten on next generation.

## Overview

This ORM layer was automatically generated from Django models using the
[django-cfg](https://djangocfg.com) FastAPI ORM Generator.

- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Models**: {model_count}
- **Apps**: {len(app_list)}

## Source

These models mirror the database schema defined in the Django project.
The source of truth is the Django models - this is a read-only reflection.

### Included Apps

{chr(10).join(f"- `{app}`" for app in app_list)}

## Structure

```
orm/
├── __init__.py      # Root exports
├── database.py      # Async session configuration
├── CLAUDE.md        # This file
└── <app>/
    ├── __init__.py
    ├── models.py    # SQLModel table classes
    ├── schemas.py   # Pydantic schemas (Create/Read/Update)
    └── crud.py      # Async CRUD repository
```

## Usage

```python
from orm import get_session, init_db
from orm.users.models import User
from orm.users.schemas import UserCreate, UserRead
from orm.users.crud import UserRepository

# In FastAPI endpoint
@app.get("/users/{{user_id}}")
async def get_user(user_id: int, session = Depends(get_session)):
    return await UserRepository.get_by_id(session, user_id)
```

## Regeneration

To regenerate this ORM after Django model changes:

```bash
# From Django project directory
python manage.py generate_fastapi

# Or via make
make orm
```

## Important Notes

1. **Do not edit** - All files are auto-generated
2. **Extend, don't modify** - Create wrapper classes in separate files
3. **Keep in sync** - Regenerate after any Django model changes
4. **Database schema** - Defined by Django migrations, not these models

## django-cfg

This ORM was generated by django-cfg, a Django configuration and tooling package.

For more information: https://djangocfg.com
'''

        return GeneratedFile(
            path=Path(self.config.output_dir) / "CLAUDE.md",
            content=content,
        )

    @staticmethod
    def _to_camel_case(name: str) -> str:
        """Convert snake_case to CamelCase."""
        components = name.split('_')
        return ''.join(x.title() for x in components)

    def _write_files(self, files: list[GeneratedFile]) -> None:
        """Write generated files to disk."""
        for file in files:
            # Ensure directory exists
            file.path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(file.path, "w", encoding="utf-8") as f:
                f.write(file.content)

            logger.debug(f"Wrote: {file.path}")
