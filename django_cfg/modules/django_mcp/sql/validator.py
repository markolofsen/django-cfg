"""
AST-based SQL validator using pglast.

Deny by default — only explicitly allowed statement types pass. Uses
PostgreSQL's own parser (libpg_query), so a keyword hidden in a comment, a
dollar-quoted string or a Unicode homoglyph is classified the way the server
would classify it, not the way a regex would.

Node types are matched by **class name** (``ast.SelectStmt`` → ``"SelectStmt"``)
rather than by `NodeTag` members. `NodeTag` exists, but its members are named
``T_SelectStmt``, and a name that does not exist raises `AttributeError` at
import — which is how this module previously failed to import at all.
"""

from typing import List, Optional, Set, Tuple

try:
    from pglast import parse_sql
    from pglast.visitors import Visitor

    HAS_PGLAST = True
except ImportError:  # pragma: no cover - exercised only where pglast is absent
    parse_sql = None

    # A stand-in so `class _SecurityVisitor(Visitor)` below can still be
    # defined. Without it the module raises NameError on import and
    # `HAS_PGLAST` — the flag whose whole purpose is to let a caller degrade
    # gracefully — is unreachable.
    class Visitor:  # type: ignore[no-redef]
        pass

    HAS_PGLAST = False


# Statement types that may be executed. Everything absent from this set is
# refused, so a PostgreSQL release that adds a statement type is refused by
# default rather than admitted by omission.
ALLOWED_STATEMENTS = {
    "SelectStmt",
}

# Write and control statements, listed separately from "not allowed" only so
# the refusal can name what it saw. Security does not depend on this set being
# complete — ALLOWED_STATEMENTS already is the gate.
DANGEROUS_STATEMENTS = {
    "InsertStmt",
    "UpdateStmt",
    "DeleteStmt",
    "MergeStmt",
    "TruncateStmt",
    "CreateStmt",
    "CreateTableAsStmt",
    "AlterTableStmt",
    "AlterObjectSchemaStmt",
    "AlterOwnerStmt",
    "DropStmt",
    "GrantStmt",
    "GrantRoleStmt",
    "RevokeStmt",
    "CopyStmt",
    "VariableSetStmt",
    "VariableShowStmt",
    "DoStmt",
    "CallStmt",
    "PrepareStmt",
    "ExecuteStmt",
    "DeallocateStmt",
    "TransactionStmt",
    "LockStmt",
    "CreateFunctionStmt",
    "CreateRoleStmt",
    "AlterRoleStmt",
    "DropRoleStmt",
}

# Metadata and system schemas. Reading these maps the database — roles, table
# names, column types — for whoever asks.
BLOCKED_SCHEMAS = {
    "pg_catalog",
    "information_schema",
    "pg_toast",
    "pg_temp",
    "pg_toast_temp",
}

# Tables that carry credentials or session material. Blocked by name because a
# deployment that forgot to pass `allowed_tables` would otherwise expose them.
BLOCKED_TABLES = {
    "auth_user",
    "auth_group",
    "auth_permission",
    "django_session",
    "django_admin_log",
    "authtoken_token",
    "otp_totp_totpdevice",
    "pg_shadow",
    "pg_authid",
    "pg_roles",
}

# Functions that reach outside the query: sleep (DoS), file and large-object
# access, outbound connections, session state, and killing other backends.
DANGEROUS_FUNCTIONS = {
    "pg_sleep",
    "pg_sleep_for",
    "pg_sleep_until",
    "lo_import",
    "lo_export",
    "lo_creat",
    "dblink",
    "dblink_connect",
    "dblink_exec",
    "copy",
    "pg_read_file",
    "pg_read_binary_file",
    "pg_ls_dir",
    "pg_stat_file",
    "set_config",
    "current_setting",
    "pg_terminate_backend",
    "pg_cancel_backend",
    "query_to_xml",
}


class SQLValidationError(Exception):
    """Raised when SQL validation fails."""

    pass


def _normalise_placeholders(sql: str) -> str:
    """Rewrite psycopg's ``%s`` / ``%(name)s`` markers as PostgreSQL ``$n``.

    `raw_sql` takes `params` separately and passes the query through psycopg,
    whose placeholder syntax the server's parser does not accept — a perfectly
    ordinary parameterised query would be refused as a syntax error, pushing
    callers toward interpolating values into the string instead. That is the
    opposite of what this validator exists to encourage.

    Only markers outside string literals are rewritten, so a literal
    ``'100%s off'`` keeps its text. The result is parsed, never executed.
    """
    out = []
    quote = None  # the delimiter of the literal currently open, if any
    index = 0
    param = 0
    while index < len(sql):
        char = sql[index]

        if quote:
            out.append(char)
            if char == quote:
                # '' and "" are escaped delimiters, not the end of the literal.
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    out.append(sql[index + 1])
                    index += 2
                    continue
                quote = None
            index += 1
            continue

        if char in ("'", '"'):
            quote = char
            out.append(char)
            index += 1
            continue

        if char == "%" and index + 1 < len(sql):
            rest = sql[index + 1 :]
            if rest[0] == "s":
                param += 1
                out.append(f"${param}")
                index += 2
                continue
            if rest[0] == "(":
                closing = rest.find(")s")
                if closing != -1:
                    param += 1
                    out.append(f"${param}")
                    index += closing + 3
                    continue
            if rest[0] == "%":
                # `%%` is a literal percent in psycopg's dialect.
                out.append("%%")
                index += 2
                continue

        out.append(char)
        index += 1

    return "".join(out)


def _collect_cte_names(statements) -> Set[str]:
    """Every name bound by a ``WITH`` clause anywhere in the parsed query."""
    names: Set[str] = set()

    class _CTECollector(Visitor):
        def visit(self, ancestors, node):
            if type(node).__name__ == "CommonTableExpr" and node.ctename:
                names.add(node.ctename.lower())

    collector = _CTECollector()
    for statement in statements:
        collector(statement)
    return names


def _tag(name: str) -> str:
    """The `T_`-prefixed spelling used in refusal messages.

    Callers and tests match on `T_InsertStmt`, which is what `NodeTag` calls
    the node — worth keeping even though the classification no longer goes
    through that enum.
    """
    return f"T_{name}"


class SQLValidator:
    """
    Validate SQL using PostgreSQL's own parser (pglast).

    Rejects anything that is not a safe SELECT.
    """

    def __init__(
        self,
        allowed_tables: Optional[Set[str]] = None,
        blocked_tables: Optional[Set[str]] = None,
    ):
        if not HAS_PGLAST:
            raise ImportError(
                "pglast is required for SQL validation. Install it: pip install pglast"
            )

        self.allowed_tables = {t.lower() for t in (allowed_tables or set())}
        self.blocked_tables = {t.lower() for t in (blocked_tables or BLOCKED_TABLES)}

        # The table part of each qualified entry, so an allowlist written as
        # {"public.orders"} still admits the ordinary `FROM orders`.
        self.allowed_bare_names = {t.rsplit(".", 1)[-1] for t in self.allowed_tables}

    def validate(self, sql: str) -> Tuple[bool, str]:
        """
        Validate a SQL query.

        Returns:
            (is_valid: bool, error_message: str)

        Examples:
            >>> v = SQLValidator(allowed_tables={'public.orders'})
            >>> v.validate("SELECT * FROM orders")
            (True, '')
            >>> v.validate("INSERT INTO orders VALUES (1)")[0]
            False
        """
        try:
            statements = parse_sql(_normalise_placeholders(sql))
        except Exception as e:
            # A query the server cannot parse is not a query. Refusing here
            # also means everything downstream can assume a real parse tree.
            return False, f"SQL parse error: {e}"

        if not statements:
            return False, "Empty query"

        # CTE names are defined by the query itself and are not tables, so they
        # must not be measured against the allowlist. Collected up front
        # because the walk is breadth-first: `FROM active_users` is reached
        # before the `WITH active_users AS (...)` that declares it.
        visitor = _SecurityVisitor(
            allowed_tables=self.allowed_tables,
            allowed_bare_names=self.allowed_bare_names,
            blocked_tables=self.blocked_tables,
            cte_names=_collect_cte_names(statements),
        )

        for raw in statements:
            # The top-level statement type is checked here rather than in the
            # visitor: a subquery legitimately contains a nested `SelectStmt`,
            # so "is this statement allowed" is a question about the root.
            stmt = getattr(raw, "stmt", raw)
            name = type(stmt).__name__
            if name not in ALLOWED_STATEMENTS:
                if name in DANGEROUS_STATEMENTS:
                    return False, f"Dangerous operation blocked: {_tag(name)}"
                return False, f"Statement type not allowed: {_tag(name)}"

            visitor(raw)
            if visitor.errors:
                return False, "; ".join(visitor.errors)

        return True, ""

    def validate_or_raise(self, sql: str) -> None:
        """
        Validate SQL, raising `SQLValidationError` if it is not safe.
        """
        is_valid, error = self.validate(sql)
        if not is_valid:
            raise SQLValidationError(error)


class _SecurityVisitor(Visitor):
    """
    Walks the parse tree and records every reason the query must be refused.

    Overrides `visit`, pglast's per-node hook — **not** `__call__`, which is
    the traversal itself. Overriding the latter replaces the walk instead of
    participating in it, and nothing below the root is ever inspected.
    """

    def __init__(
        self,
        allowed_tables: Set[str],
        allowed_bare_names: Set[str],
        blocked_tables: Set[str],
        cte_names: Optional[Set[str]] = None,
    ):
        super().__init__()
        self.allowed_tables = allowed_tables
        self._allowed_bare_names = allowed_bare_names
        self.blocked_tables = blocked_tables
        self.cte_names = cte_names or set()
        self.errors: List[str] = []

    def visit(self, ancestors, node) -> None:
        name = type(node).__name__

        # A write statement nested inside a SELECT — a data-modifying CTE
        # (`WITH x AS (DELETE ... RETURNING *) SELECT ...`) has a SelectStmt
        # root and would otherwise pass the root check above.
        if name in DANGEROUS_STATEMENTS:
            self.errors.append(f"Dangerous operation blocked: {_tag(name)}")
            return

        # `SELECT ... INTO new_table` creates a table. It is a SelectStmt, so
        # only the presence of the clause distinguishes it.
        if name == "IntoClause":
            self.errors.append("SELECT INTO is not allowed")
            return

        if name == "RangeVar":
            self._check_range_var(node)
        elif name == "FuncCall":
            self._check_function(node)

    def _check_range_var(self, node) -> None:
        """Check one table reference against the schema, block and allow lists."""
        schema = getattr(node, "schemaname", None)
        table = getattr(node, "relname", None)

        if schema and schema.lower() in BLOCKED_SCHEMAS:
            self.errors.append(f"Access to system schema blocked: {schema}")
            return

        if not table:
            return

        if table.lower() in self.blocked_tables:
            self.errors.append(f"Access to sensitive table blocked: {table}")
            return

        # A reference to a name the query itself bound in a WITH clause. It is
        # not a table, so the allowlist has nothing to say about it. Checked
        # after the schema and block lists, and only when unqualified, so
        # `WITH auth_user AS (...)` cannot be used to reach the real one.
        if not schema and table.lower() in self.cte_names:
            return

        if self.allowed_tables:
            bare = table.lower()
            if schema:
                # Schema named explicitly — match it literally. Falling back to
                # the bare name here would let "public.orders" in the allowlist
                # admit `other_schema.orders`, which is a different table.
                permitted = f"{schema.lower()}.{bare}" in self.allowed_tables
                shown = f"{schema.lower()}.{bare}"
            else:
                # No schema — `FROM orders` is the ordinary way to write the
                # query, and it means whatever the search_path resolves. Accept
                # it against a bare or a qualified entry.
                permitted = bare in self.allowed_tables or bare in self._allowed_bare_names
                shown = bare

            if not permitted:
                self.errors.append(f"Table not exposed to agent: {shown}")

    def _check_function(self, node) -> None:
        """Block calls to functions that reach outside the query."""
        parts = []
        for item in getattr(node, "funcname", None) or ():
            value = getattr(item, "sval", None)
            if value is None:
                value = getattr(item, "val", None)
            if value:
                parts.append(str(value).lower())

        if not parts:
            return

        # Checked on the bare name as well as the qualified one:
        # `pg_catalog.pg_sleep(10)` parses to a two-part funcname and would
        # miss a blocklist keyed on "pg_sleep" alone.
        candidates = {".".join(parts), parts[-1]}
        blocked = candidates & DANGEROUS_FUNCTIONS
        if blocked:
            self.errors.append(f"Dangerous function blocked: {sorted(blocked)[0]}()")
