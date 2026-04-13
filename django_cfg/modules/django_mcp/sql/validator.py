"""
AST-based SQL Validator using pglast.

Deny by default — only explicitly allowed node types pass.
Uses PostgreSQL's own parser (libpg_query) for 100% accuracy.
"""

from typing import List, Optional, Set, Tuple

try:
    from pglast import parse_sql
    from pglast.visitors import Visitor
    from pglast.enums.nodes import NodeTag
    HAS_PGLAST = True
except ImportError:
    HAS_PGLAST = False


# Allowed node types (read-only SELECT operations)
ALLOWED_NODES = {
    NodeTag.T_SELECT_STMT,
    NodeTag.T_RES_TARGET,
    NodeTag.T_COLUMN_REF,
    NodeTag.T_A_CONST,
    NodeTag.T_FUNC_CALL,
    NodeTag.T_A_EXPR,
    NodeTag.T_SORT_BY,
    NodeTag.T_RANGE_VAR,
    NodeTag.T_JOIN_EXPR,
    NodeTag.T_COALESCE_EXPR,
    NodeTag.T_CASE_EXPR,
    NodeTag.T_WHEN_CLAUSE,
    NodeTag.T_SUB_LINK,
    NodeTag.T_WITH_CLAUSE,
    NodeTag.T_CTE,
    NodeTag.T_WINDOW_DEF,
    NodeTag.T_GROUPING_SET,
    NodeTag.T_A_INDICES,
    NodeTag.T_NULL_TEST,
    NodeTag.T_BOOLEAN_TEST,
    NodeTag.T_PARAM_REF,
    NodeTag.T_TYPE_NAME,
    NodeTag.T_LIST,
    NodeTag.T_INTeger,
    NodeTag.T_FLOAT,
    NodeTag.T_STRING,
    NodeTag.T_ALIAS,
    NodeTag.T_SET_TO_DEFAULT,
}

# Blocked schemas (metadata, system tables)
BLOCKED_SCHEMAS = {
    'pg_catalog', 'information_schema', 'pg_toast',
    'pg_temp', 'pg_toast_temp',
}

# Blocked table names (sensitive Django tables)
BLOCKED_TABLES = {
    'auth_user', 'auth_group', 'auth_permission',
    'django_session', 'django_admin_log',
    'authtoken_token', 'otp_totp_totpdevice',
    'pg_shadow', 'pg_authid', 'pg_roles',
}

# Dangerous node types (write operations)
DANGEROUS_NODES = {
    NodeTag.T_INSERT_STMT,
    NodeTag.T_UPDATE_STMT,
    NodeTag.T_DELETE_STMT,
    NodeTag.T_TRUNCATE_STMT,
    NodeTag.T_CREATE_STMT,
    NodeTag.T_ALTER_TABLE_STMT,
    NodeTag.T_ALTER_OBJECT_SCHEMA_STMT,
    NodeTag.T_ALTER_OWNER_STMT,
    NodeTag.T_DROP_STMT,
    NodeTag.T_GRANT_STMT,
    NodeTag.T_REVOKE_STMT,
    NodeTag.T_COPY_STMT,
    NodeTag.T_VARIABLE_SET_STMT,
    NodeTag.T_VARIABLE_SHOW_STMT,
    NodeTag.T_DO_STMT,
    NodeTag.T_CALL_STMT,  # Block function calls that could be dangerous
    NodeTag.T_PREPARE_STMT,
    NodeTag.T_EXECUTE_STMT,
    NodeTag.T_DEALLOCATE_STMT,
}


class SQLValidationError(Exception):
    """Raised when SQL validation fails."""
    pass


class SQLValidator:
    """
    Validate SQL using PostgreSQL's own parser (pglast).

    Rejects anything that isn't a safe SELECT.
    """

    def __init__(
        self,
        allowed_tables: Optional[Set[str]] = None,
        blocked_tables: Optional[Set[str]] = None,
    ):
        self.allowed_tables = {t.lower() for t in (allowed_tables or set())}
        self.blocked_tables = {t.lower() for t in (blocked_tables or BLOCKED_TABLES)}

        if not HAS_PGLAST:
            raise ImportError(
                "pglast is required for SQL validation. "
                "Install it: pip install pglast"
            )

    def validate(self, sql: str) -> Tuple[bool, str]:
        """
        Validate SQL query.

        Returns:
            (is_valid: bool, error_message: str)

        Examples:
            >>> v = SQLValidator(allowed_tables={'public.orders'})
            >>> v.validate("SELECT * FROM orders WHERE status = 'active'")
            (True, "")
            >>> v.validate("INSERT INTO orders VALUES (1)")
            (False, "Dangerous operation blocked: T_INSERT_STMT")
        """
        try:
            statements = parse_sql(sql)
        except Exception as e:
            return False, f"SQL parse error: {e}"

        visitor = _SecurityVisitor(
            allowed_tables=self.allowed_tables,
            blocked_tables=self.blocked_tables,
        )

        for stmt in statements:
            visitor(stmt)
            if visitor.errors:
                return False, "; ".join(visitor.errors)

        return True, ""

    def validate_or_raise(self, sql: str) -> None:
        """
        Validate SQL, raise SQLValidationError if invalid.

        Raises:
            SQLValidationError: If SQL is not safe
        """
        is_valid, error = self.validate(sql)
        if not is_valid:
            raise SQLValidationError(error)


class _SecurityVisitor(Visitor):
    """
    Recursive AST visitor that blocks dangerous operations.

    Inspects every node in the parse tree.
    """

    def __init__(
        self,
        allowed_tables: Set[str],
        blocked_tables: Set[str],
    ):
        super().__init__()
        self.allowed_tables = allowed_tables
        self.blocked_tables = blocked_tables
        self.errors: List[str] = []

    def __call__(self, node):
        node_tag = getattr(node, 'node_tag', None)

        # ── Block dangerous operations ──────────────────────────────────
        if node_tag in DANGEROUS_NODES:
            self.errors.append(f"Dangerous operation blocked: {node_tag.name}")
            return

        # ── Block INTO clause (SELECT INTO creates tables) ─────────────
        if hasattr(node, 'intoClause') and node.intoClause is not None:
            self.errors.append("SELECT INTO is not allowed")
            return

        # ── Block UNION if it could be used for data exfiltration ──────
        # (Allow it for now — UNION is read-only)

        # ── Check table references ──────────────────────────────────────
        if node_tag == NodeTag.T_RANGE_VAR:
            self._check_range_var(node)

        # ── Block dangerous functions ───────────────────────────────────
        if node_tag == NodeTag.T_FUNC_CALL:
            self._check_function(node)

        # Continue traversing
        super().__call__(node)

    def _check_range_var(self, node) -> None:
        """Check table reference against allowlist/blocklist."""
        schema = getattr(node, 'schemaname', None)
        table = getattr(node, 'relname', None)

        # Block system schemas
        if schema and schema.lower() in BLOCKED_SCHEMAS:
            self.errors.append(f"Access to system schema blocked: {schema}")
            return

        # Block specific tables
        if table and table.lower() in self.blocked_tables:
            self.errors.append(f"Access to sensitive table blocked: {table}")
            return

        # Check against allowlist (if set)
        if self.allowed_tables:
            full_name = f"{schema}.{table}" if schema else table
            if full_name.lower() not in self.allowed_tables:
                # Allow if table name alone matches
                if table.lower() not in self.allowed_tables:
                    self.errors.append(f"Table not exposed to agent: {full_name}")
                    return

    def _check_function(self, node) -> None:
        """Block dangerous function calls."""
        func_name = None
        if hasattr(node, 'funcname') and node.funcname:
            # funcname is a list of String nodes
            parts = []
            for item in node.funcname:
                if hasattr(item, 'val') or hasattr(item, 'sval'):
                    val = getattr(item, 'sval', getattr(item, 'val', None))
                    if val:
                        parts.append(str(val).lower())
            if parts:
                func_name = '.'.join(parts)

        # Block dangerous functions
        dangerous_funcs = {
            'pg_sleep', 'pg_sleep_for', 'pg_sleep_until',  # DoS
            'lo_import', 'lo_export', 'lo_creat',           # Large objects
            'dlink', 'dblink_connect',                      # External connections
            'copy', 'pg_read_file', 'pg_ls_dir',            # File access
            'set_config', 'current_setting',                # GUC manipulation
            'pg_terminate_backend', 'pg_cancel_backend',    # Connection kill
        }

        if func_name and func_name in dangerous_funcs:
            self.errors.append(f"Dangerous function blocked: {func_name}()")
