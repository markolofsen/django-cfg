"""
Vector search method generator for CRUD repositories.
"""

from ....ir.models import ParsedModel


def generate_vector_search(model: ParsedModel, vector_field) -> list[str]:
    """
    Generate cosine similarity vector_search() for models with a VectorField.

    Uses pgvector's cosine_distance() via SQLAlchemy so no raw SQL is needed.
    The generated method filters by an optional FK field named 'project_id' if present,
    otherwise performs a global search.
    """
    field_name = vector_field.name  # e.g. "embedding"

    # Detect project_id FK for scoped search (common pattern in knowbase)
    has_project_id = any(f.name == "project_id" for f in model.fields)

    return [
        "    @staticmethod",
        "    async def vector_search(",
        "        session: AsyncSession,",
        "        embedding: list[float],",
        *(["        project_id: Optional[str] = None,"] if has_project_id else []),
        "        limit: int = 10,",
        "        threshold: float = 0.0,",
        f"    ) -> list[{model.name}]:",
        '        """',
        f'        Cosine similarity search on {model.name}.{field_name}.',
        '        Returns records ordered by descending similarity (closest first).',
        '        threshold filters out results with similarity below the given value.',
        '        """',
        "        from pgvector.sqlalchemy import Vector",
        "        from sqlalchemy import cast, func",
        f"        vec = cast(embedding, Vector)",
        f"        distance = {model.name}.{field_name}.cosine_distance(vec)",
        f"        stmt = (",
        f"            select({model.name}, (1 - distance).label(\"similarity\"))",
        f"            .where({model.name}.{field_name} is not None)",
        f"            .where(1 - distance >= threshold)",
        f"            .order_by(distance)",
        f"            .limit(limit)",
        f"        )",
        *(
            [
                f"        if project_id is not None:",
                f"            stmt = stmt.where({model.name}.project_id == project_id)",
            ]
            if has_project_id else []
        ),
        "        result = await session.execute(stmt)",
        f"        return list(result.scalars().all())",
    ]
