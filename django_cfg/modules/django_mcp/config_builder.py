"""
MCP Configuration Builder

Simple declarative API for configuring agent access in ONE place.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from functools import wraps

from django_cfg.modules.django_mcp import (
    ALL_TOOLS,
    PUBLIC_TOOLS,
    DjangoMCPModuleConfig,
    IntrospectionConfig,
    AppMCPConfig,
    ModelMCPConfig,
    CommandMCPConfig,
    MCPProfile,
    MCPTargetConfig,
)
from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry
from django_cfg.modules.django_mcp.services.context import MCPContext


#: Where the operator surface lives. Read from the model so the builder and the
#: config cannot disagree about the default.
DEFAULT_ENDPOINT_PATH = DjangoMCPModuleConfig.model_fields["endpoint_path"].default


class ProfileBuilder:
    """Collects one profile's settings inside a ``with`` block.

    Used through :meth:`MCPConfigBuilder.profile`. The context-manager shape is
    deliberate: an indented block makes it visible which surface each call
    belongs to, and a settings call that drifts outside the block is a syntax
    the reader notices rather than a silent reassignment to the wrong profile.
    """

    def __init__(self, name: str, path: str, access: str):
        self._name = name
        self._path = path
        self._access = access
        self._access_key: Optional[str] = None
        self._service_username: Optional[str] = None
        self._tools: List[str] = []
        self._exposures: Dict[str, ModelExposure] = {}
        self._introspection: Optional[IntrospectionConfig] = None
        self._rate_limit: str = "100/minute"
        self._public_info: Optional[bool] = None

    def set_access_key(
        self, key: str, service_username: Optional[str] = None
    ) -> "ProfileBuilder":
        self._access_key = key
        self._service_username = service_username
        return self

    def tools(self, *names: str) -> "ProfileBuilder":
        """Name the tools this profile serves, or ``"*"`` for all.

        ``"*"`` is deliberately ugly to write out: serving every registered tool
        is a real choice with real consequences and should read like one.
        """
        self._tools.extend(names)
        return self

    def expose(
        self,
        model: str,
        read_only: bool = True,
        hidden_fields: Optional[List[str]] = None,
        max_results: int = 100,
        operations: Optional[List[str]] = None,
    ) -> "ProfileBuilder":
        app_label, model_name = model.split(".")
        self._exposures[model] = ModelExposure(
            app_label=app_label,
            model_name=model_name.lower(),
            read_only=read_only,
            hidden_fields=hidden_fields or [],
            max_results=max_results,
            operations=operations
            or (
                ["list", "retrieve"]
                if read_only
                else ["list", "retrieve", "create", "update", "delete"]
            ),
        )
        return self

    def enable_introspection(
        self, expose_urls: bool = False, expose_code: bool = False, max_depth: int = 3
    ) -> "ProfileBuilder":
        self._introspection = IntrospectionConfig(
            enabled=True,
            expose_urls=expose_urls,
            expose_code=expose_code,
            max_depth=max_depth,
        )
        return self

    def set_rate_limit(self, limit: str = "100/minute") -> "ProfileBuilder":
        self._rate_limit = limit
        return self

    def set_public_info(self, public: bool) -> "ProfileBuilder":
        """Override whether ``<path>info/`` lists tools without a credential."""
        self._public_info = public
        return self

    def build(self) -> MCPProfile:
        """Validated here, so a bad profile fails where it was written."""
        return MCPProfile(
            name=self._name,
            path=self._path,
            access=self._access,
            access_key=self._access_key,
            service_username=self._service_username,
            tools=self._tools,
            exposures={
                key: ModelMCPConfig(
                    enabled=True,
                    read_only=exposure.read_only,
                    hidden_fields=exposure.hidden_fields,
                    max_results=exposure.max_results,
                    allowed_operations=exposure.operations,
                )
                for key, exposure in self._exposures.items()
            },
            introspection=self._introspection,
            rate_limit=self._rate_limit,
            public_info=self._public_info,
        )

    def __enter__(self) -> "ProfileBuilder":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


@dataclass
class ModelExposure:
    """Configuration for exposing a single model."""
    app_label: str
    model_name: str
    read_only: bool = True
    hidden_fields: List[str] = field(default_factory=list)
    max_results: int = 100
    operations: List[str] = field(default_factory=lambda: ["list", "retrieve"])
    description: str = ""


class MCPConfigBuilder:
    """
    Simple builder for MCP configuration.

    All agent access is configured here in ONE place.
    Place this in project_root/mcp/__init__.py

    Example:
        from django_cfg.modules.django_mcp import MCPConfigBuilder

        mcp = MCPConfigBuilder()

        # Expose models
        mcp.expose("profiles.UserProfile")
        mcp.expose("accounts.User", hidden_fields=["password", "secret_key"])
        mcp.expose("orders.Order", operations=["list", "retrieve", "create"])

        # Allow commands
        mcp.allow_command("clearsessions")
        mcp.allow_command("update_stats", staff_only=True)

        # Custom tools
        @mcp.tool(name="get_user_stats", description="Get user statistics")
        def get_user_stats(ctx, user_id: str) -> str:
            return f"Stats for user {user_id}"

        # Enable introspection
        mcp.enable_introspection(expose_urls=True)

        # Build final config
        mcp_config = mcp.build()
    """

    def __init__(self):
        self._models: Dict[str, ModelExposure] = {}
        self._commands: List[str] = []
        self._staff_commands: List[str] = []
        self._introspection: IntrospectionConfig = IntrospectionConfig()
        self._custom_tools: List[MCPTool] = []
        self._enabled: bool = True
        self._access_key: Optional[str] = None
        self._service_username: Optional[str] = None
        self._targets: Dict[str, MCPTargetConfig] = {}
        self._rate_limit: str = "100/minute"
        self._llm_model: str = "openai/gpt-4.1-nano"
        self._profiles: Dict[str, ProfileBuilder] = {}
        self._public_profile: Optional[Dict[str, Any]] = None

    def enable_public_profile(
        self,
        path: str = "/mcp/",
        rate_limit: str = "20/minute",
        expose: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "MCPConfigBuilder":
        """Serve an anonymous, read-only surface beside the operator one.

            mcp.set_access_key(key, service_username=user)
            mcp.enable_public_profile()

        It serves whatever declares ``public = True`` on its tool class — the
        project never restates the list, so adding a tool cannot silently
        change what is public in either direction.

        The flat settings above become the ``operator`` profile automatically;
        that is why this does not trip the "profiles must not be mixed with
        flat settings" rule, which exists for a *hand-written* profile leaving
        flat calls stranded.

        ``rate_limit`` defaults tighter than the operator's: an anonymous
        caller has no key to revoke, so the rate is the only lever.
        """
        self._public_profile = {
            "path": path,
            "rate_limit": rate_limit,
            "expose": expose or {},
        }
        return self

    def profile(self, name: str, path: str, access: str) -> ProfileBuilder:
        """Declare one MCP surface.

            with mcp.profile("public", path="/mcp/", access="anonymous") as p:
                p.tools("catalog_search", "catalog_get")
                p.set_rate_limit("20/minute")

        Declaring any profile means the flat ``set_access_key`` /
        ``enable_introspection`` / ``set_rate_limit`` calls no longer describe a
        surface — profiles do, entirely. Mixing the two would leave a reader
        guessing which one governs a given endpoint, so :meth:`build` rejects it.
        """
        if name in self._profiles:
            raise ValueError(f"MCP profile {name!r} is declared twice.")
        builder = ProfileBuilder(name=name, path=path, access=access)
        self._profiles[name] = builder
        return builder

    def expose(
        self,
        model_path: str,
        *,
        read_only: bool = True,
        hidden_fields: Optional[List[str]] = None,
        max_results: int = 100,
        operations: Optional[List[str]] = None,
        description: str = "",
    ) -> "MCPConfigBuilder":
        """
        Expose a Django model to MCP agents.

        Args:
            model_path: "app.Model" or "app_label.ModelName" (e.g., "profiles.UserProfile")
            read_only: If True, only read operations allowed
            hidden_fields: Fields to hide from agents (e.g., passwords)
            max_results: Maximum number of records returned per query
            operations: Allowed operations: list, retrieve, create, update, delete
            description: Optional description for the model
        """
        parts = model_path.split(".")
        if len(parts) != 2:
            raise ValueError(f"Invalid model path: '{model_path}'. Use 'app.Model' format.")

        app_label, model_name = parts[0], parts[1]

        if read_only and operations is None:
            operations = ["list", "retrieve"]

        self._models[model_path.lower()] = ModelExposure(
            app_label=app_label,
            model_name=model_name.lower(),
            read_only=read_only,
            hidden_fields=hidden_fields or [],
            max_results=max_results,
            operations=operations or ["list", "retrieve"],
            description=description,
        )
        return self

    def allow_command(self, command_name: str, staff_only: bool = False) -> "MCPConfigBuilder":
        """
        Allow agents to execute a management command.

        Args:
            command_name: Django management command name
            staff_only: If True, only staff users can execute this command
        """
        if staff_only:
            self._staff_commands.append(command_name)
        else:
            self._commands.append(command_name)
        return self

    def enable_introspection(
        self,
        expose_urls: bool = False,
        expose_code: bool = False,
        max_depth: int = 3,
    ) -> "MCPConfigBuilder":
        """
        Enable Django structure discovery for agents.

        Args:
            expose_urls: Expose URL patterns to agents
            expose_code: Expose view source code (NEVER in production!)
            max_depth: Maximum depth of relationship traversal
        """
        self._introspection = IntrospectionConfig(
            enabled=True,
            expose_urls=expose_urls,
            expose_code=expose_code,
            max_depth=max_depth,
        )
        return self

    def tool(self, name: str, description: str, input_schema: Optional[Dict[str, Any]] = None):
        """
        Decorator to define a custom tool for agents.

        Usage:
            @mcp.tool(name="get_stats", description="Get system statistics")
            def get_stats(ctx: MCPContext) -> str:
                return "Stats here"
        """
        if input_schema is None:
            input_schema = {"type": "object", "properties": {}}

        def decorator(func: Callable):
            class DecoratedTool(MCPTool):
                def __init__(self):
                    self.name = name
                    self.description = description
                    self.input_schema = input_schema
                    self.func = func

                def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
                    return self.func(context, **arguments)

            tool = DecoratedTool()
            tool_registry.register(tool)
            self._custom_tools.append(tool)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def set_access_key(
        self, key: str, *, service_username: Optional[str] = None
    ) -> "MCPConfigBuilder":
        """Set static access key for agents. REQUIRED for all requests.

        Args:
            key: The value callers send in ``X-MCP-Access-Key``.
            service_username: Bind the key to a real Django account. Omitted
                (the default), a valid key authenticates as ``AnonymousUser``,
                so any tool gated on ``user.is_staff`` refuses it — which is
                the safe default and usually the right one.

                Set it only when tools genuinely need a staff identity. It
                grants that account's permissions to every holder of the key,
                so the key must then be treated as that user's password: not
                committed, and rotated with the account.
        """
        self._access_key = key
        self._service_username = service_username
        return self

    def add_target(
        self,
        kind: str,
        *env_files: str,
        url: Optional[str] = None,
        access_key: Optional[str] = None,
        server_name: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> "MCPConfigBuilder":
        """Declare a deployment ``manage.py mcp_install --<kind>`` can register.

        A target names a **deployment**, described by the dotenv files that
        configure it. Everything else is derived from those files:

        ==============  ====================================================
        endpoint        ``APP__API_URL`` + this module's ``endpoint_path``
        access key      ``MCP__ACCESS_KEY``
        registration    ``<project>_<kind>``
        ==============  ====================================================

        So the usual declaration is one line per deployment::

            mcp.add_target("local")                        # this process
            mcp.add_target("prod", "../../deploy/.env")    # somewhere else

        ``local`` takes no files because for it the *running process is the
        target*: its own config already answers both questions.

        Remote targets cannot work that way, and the reason is the whole point
        of this method: ``mcp_install --prod`` runs on a laptop configured by
        ``.env.local``, where ``get_current_config()`` holds the **development**
        URL and the **development** key. Registering those against production
        yields a client that connects, lists every tool, and 401s on the first
        real call — inside an assistant, where nobody sees the status code. The
        files are the only place the target deployment's own values exist.

        Args:
            kind: The flag that selects this target ("local", "prod", "staging").
            *env_files: Dotenv files configuring that deployment, highest
                priority first; relative paths resolve against ``BASE_DIR``.
            url: Endpoint override. Only needed when the deployment's URL is not
                in its dotenv as ``APP__API_URL``.
            server_name: Registration-name override. Set it to **keep an
                existing registration**: changing the derived name orphans the
                old entry in the assistant rather than updating it.
            profile: Which profile this target registers. Needed only when the
                deployment serves more than one — the URL is built from that
                profile's path, so a public subdomain registered without it
                points at the operator path and lists the operator tools.
        """
        self._targets[kind] = MCPTargetConfig(
            env_files=list(env_files),
            url=url,
            access_key=access_key,
            server_name=server_name,
            profile=profile,
        )
        return self

    def set_llm_model(self, model: str) -> "MCPConfigBuilder":
        """
        Set default LLM model for agents (OpenRouter format).
        Example: 'openai/gpt-4.1-nano', 'anthropic/claude-3.5-haiku'
        """
        self._llm_model = model
        return self

    def set_rate_limit(self, limit: str = "100/minute") -> "MCPConfigBuilder":
        """Set rate limit for MCP requests."""
        self._rate_limit = limit
        return self

    def disable(self) -> "MCPConfigBuilder":
        """Disable MCP module entirely."""
        self._enabled = False
        return self

    def build(self) -> Optional[DjangoMCPModuleConfig]:
        """
        Build the final DjangoMCPModuleConfig.

        Returns None if MCP is disabled.
        """
        if not self._enabled:
            return None

        if self._public_profile is not None and not self._profiles:
            # `enable_public_profile()` — turn the flat settings into the
            # operator profile and add the anonymous one beside it, so the
            # project states its intent once instead of writing both out.
            spec = self._public_profile
            if not self._access_key:
                # The operator profile requires a key; without one there is
                # nothing to protect and a public-only server is not what
                # `enable_public_profile` means.
                raise ValueError(
                    "enable_public_profile() needs an operator access key. Call "
                    "set_access_key() first: without it the operator surface "
                    "would be anonymous too, which is not what this asks for."
                )
            with self.profile(
                "operator", path=DEFAULT_ENDPOINT_PATH, access="key"
            ) as op:
                op.set_access_key(self._access_key, self._service_username)
                op.tools(ALL_TOOLS)
                op._introspection = self._introspection
                op.set_rate_limit(self._rate_limit)
                for model_key, exposure in self._models.items():
                    op.expose(
                        model_key,
                        read_only=exposure.read_only,
                        hidden_fields=exposure.hidden_fields,
                        max_results=exposure.max_results,
                        operations=exposure.operations,
                    )
            with self.profile("public", path=spec["path"], access="anonymous") as pub:
                pub.tools(PUBLIC_TOOLS)
                pub.set_rate_limit(spec["rate_limit"])
                for model_key, kwargs in spec["expose"].items():
                    pub.expose(model_key, **{"read_only": True, **kwargs})

            # Moved, not copied. Left in place they would trip the mixing check
            # below — and, worse, remain as a second declaration of settings the
            # profiles now own.
            self._access_key = None
            self._service_username = None
            self._introspection = IntrospectionConfig()

        if self._profiles:
            # Declaring profiles means profiles describe every surface. A flat
            # `set_access_key` alongside them would apply to no endpoint while
            # looking like it protects one — the exact "configured but not
            # enforced" shape this feature exists to remove.
            #
            # Not reached via `enable_public_profile()`: that path moves the
            # flat settings onto the operator profile rather than stranding
            # them, and clears them below.
            conflicting = [
                name
                for name, value in (
                    ("set_access_key", self._access_key),
                    ("enable_introspection", self._introspection.enabled),
                )
                if value
            ]
            if conflicting:
                raise ValueError(
                    "MCP config mixes profiles with the flat "
                    f"{', '.join(conflicting)} call(s). Move them onto a profile: "
                    "with profiles declared, the flat settings govern no endpoint."
                )

        # Group models by app
        exposed_apps: Dict[str, AppMCPConfig] = {}
        for model_key, exposure in self._models.items():
            app_label = exposure.app_label
            model_name = exposure.model_name

            if app_label not in exposed_apps:
                exposed_apps[app_label] = AppMCPConfig(
                    enabled=True,
                    models={},
                )

            exposed_apps[app_label].models[model_name] = ModelMCPConfig(
                enabled=True,
                read_only=exposure.read_only,
                hidden_fields=exposure.hidden_fields,
                max_results=exposure.max_results,
                allowed_operations=exposure.operations,
            )

        # All commands (staff + non-staff)
        all_commands = list(set(self._commands + self._staff_commands))

        return DjangoMCPModuleConfig(
            enabled=self._enabled,
            access_key=self._access_key,
            service_username=self._service_username,
            rate_limit=self._rate_limit,
            llm_model=self._llm_model,
            introspection=self._introspection,
            install_targets=self._targets,
            profiles={name: b.build() for name, b in self._profiles.items()},
            exposed_apps=exposed_apps,
            commands=CommandMCPConfig(
                enabled=len(all_commands) > 0,
                allowed_commands=all_commands,
                timeout_seconds=30,
            ),
        )
