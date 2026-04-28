"""
Standard CRUD method generators for repository classes.
"""

from ....ir.models import ParsedModel


def generate_get_by_id(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        f"    async def get_by_id(session: AsyncSession, id: int) -> Optional[{model.name}]:",
        f'        """Get {model.name} by ID."""',
        f"        statement = select({model.name}).where({model.name}.id == id)",
        "        result = await session.execute(statement)",
        "        return result.scalars().first()",
    ]


def generate_get_all(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        "    async def get_all(",
        "        session: AsyncSession,",
        "        skip: int = 0,",
        "        limit: int = 100,",
        f"    ) -> Sequence[{model.name}]:",
        f'        """Get all {model.name} records with pagination."""',
        f"        statement = select({model.name}).offset(skip).limit(limit)",
        "        result = await session.execute(statement)",
        "        return result.scalars().all()",
    ]


def generate_get_by_ids(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        f"    async def get_by_ids(session: AsyncSession, ids: List[int]) -> Sequence[{model.name}]:",
        f'        """Get multiple {model.name} records by IDs."""',
        f"        statement = select({model.name}).where({model.name}.id.in_(ids))",
        "        result = await session.execute(statement)",
        "        return result.scalars().all()",
    ]


def generate_create(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        f"    async def create(session: AsyncSession, obj: {model.name}) -> {model.name}:",
        f'        """Create a new {model.name}."""',
        "        session.add(obj)",
        "        await session.commit()",
        "        await session.refresh(obj)",
        "        return obj",
    ]


def generate_create_many(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        f"    async def create_many(session: AsyncSession, objects: List[{model.name}]) -> List[{model.name}]:",
        f'        """Create multiple {model.name} records."""',
        "        session.add_all(objects)",
        "        await session.commit()",
        "        for obj in objects:",
        "            await session.refresh(obj)",
        "        return objects",
    ]


def generate_update(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        "    async def update(",
        "        session: AsyncSession,",
        "        id: int,",
        "        data: dict,",
        f"    ) -> Optional[{model.name}]:",
        f'        """Update a {model.name} by ID."""',
        f"        obj = await {model.name}Repository.get_by_id(session, id)",
        "        if obj:",
        "            for key, value in data.items():",
        "                if value is not None and hasattr(obj, key):",
        "                    setattr(obj, key, value)",
        "            await session.commit()",
        "            await session.refresh(obj)",
        "        return obj",
    ]


def generate_delete(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        "    async def delete(session: AsyncSession, id: int) -> bool:",
        f'        """Delete a {model.name} by ID."""',
        f"        obj = await {model.name}Repository.get_by_id(session, id)",
        "        if obj:",
        "            await session.delete(obj)",
        "            await session.commit()",
        "            return True",
        "        return False",
    ]


def generate_exists(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        "    async def exists(session: AsyncSession, id: int) -> bool:",
        f'        """Check if {model.name} exists by ID."""',
        f"        statement = select({model.name}.id).where({model.name}.id == id)",
        "        result = await session.execute(statement)",
        "        return result.scalar() is not None",
    ]


def generate_count(model: ParsedModel) -> list[str]:
    return [
        "    @staticmethod",
        "    async def count(session: AsyncSession) -> int:",
        f'        """Count all {model.name} records."""',
        "        from sqlalchemy import func",
        f"        statement = select(func.count()).select_from({model.name})",
        "        result = await session.execute(statement)",
        "        return result.scalar() or 0",
    ]
