"""MCP Module Configuration."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ModelMCPConfig(BaseModel):
    """Configuration for exposing a single Django model to MCP."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Whether this model is exposed to MCP",
    )
    read_only: bool = Field(
        default=True,
        description="If True, only read operations are allowed",
    )
    hidden_fields: List[str] = Field(
        default_factory=list,
        description="Fields to exclude from MCP responses (e.g., password, secret_key)",
    )
    max_results: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records returned per query",
    )
    allowed_operations: List[str] = Field(
        default_factory=lambda: ["list", "retrieve"],
        description="Allowed CRUD operations: list, retrieve, create, update, delete",
    )


class AppMCPConfig(BaseModel):
    """Configuration for exposing a Django app to MCP."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Whether this app's models are exposed to MCP",
    )
    models: Dict[str, ModelMCPConfig] = Field(
        default_factory=dict,
        description="Per-model configuration. Key is model name (lowercase)",
    )
    max_results: int = Field(
        default=100,
        description="Default max_results for all models in this app",
    )


class IntrospectionConfig(BaseModel):
    """Configuration for Django introspection capabilities."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Allow agents to discover app structure",
    )
    expose_urls: bool = Field(
        default=False,
        description="Expose URL patterns to agents",
    )
    expose_code: bool = Field(
        default=False,
        description="Expose view source code snippets (dev only!)",
    )
    max_depth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum depth of relationship traversal",
    )


class CommandMCPConfig(BaseModel):
    """Configuration for management command execution."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Allow agents to execute management commands",
    )
    allowed_commands: List[str] = Field(
        default_factory=list,
        description="Whitelist of allowed command names",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum execution time per command",
    )


class RedactionConfig(BaseModel):
    """Configuration for automatic PII redaction."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=True,
        description="Enable automatic PII redaction",
    )
    mode: str = Field(
        default="REDACT",
        pattern="^(NONE|REDACT|BLOCK)$",
        description="NONE=pass, REDACT=mask, BLOCK=reject",
    )
    custom_patterns: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional regex patterns to redact. Name -> pattern",
    )


class MCPTargetConfig(BaseModel):
    """One endpoint an assistant can be registered against.

    Declared by the *project*, because only the project knows that production is
    ``api.example.com`` and that its key lives in ``deploy/.env``. django_cfg
    owns the machinery in ``install/``; hardcoding hostnames there would make
    the framework know about one product.

    Targets are separate **registrations**, not one setting with a flag. They
    carry distinct ``server_name``s so both can be installed at once: sharing a
    name, they silently replace each other, and an assistant then reports
    ConnectionRefused for a server nobody touched.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    url: Optional[str] = Field(
        default=None,
        description=(
            "This deployment's base URL or full MCP endpoint. Pass the value "
            "from your own environment config, exactly as you pass `api_url` "
            "to DjangoConfig. Omit it for the local target — the running "
            "process is that deployment, so its own api_url answers."
        ),
    )
    access_key: Optional[str] = Field(
        default=None,
        repr=False,
        description=(
            "This deployment's MCP access key. Pass it from your environment "
            "config alongside `url`.\n\n"
            "It must be given explicitly for a REMOTE target, and the reason is "
            "the bug this whole field exists to prevent: `manage.py "
            "mcp_install --prod` runs on a laptop, where the loaded environment "
            "is the *development* one. Falling back to the running process's "
            "key there registers the dev key against production — the client "
            "connects, lists every tool, and 401s on the first real call, "
            "inside an assistant where nobody sees the status code.\n\n"
            "Omit it for the local target, where the process IS the deployment."
        ),
    )
    env_files: List[str] = Field(
        default_factory=list,
        description=(
            "Fallback: dotenv files to read `url`/`access_key` from when they "
            "are not passed directly, highest priority first; relative paths "
            "resolve against BASE_DIR. Useful when a deployment's secrets live "
            "outside the Django project (a compose `.env`, say) and so are "
            "never loaded into this process at all."
        ),
    )
    server_name: Optional[str] = Field(
        default=None,
        description=(
            "Registration name override. Normally omitted — it is derived as "
            "<project>_<target>. Set it to keep an existing registration: "
            "changing this name orphans the old entry rather than updating it."
        ),
    )
    profile: Optional[str] = Field(
        default=None,
        description=(
            "Which MCP profile this target registers. Omitted (the default) "
            "means the module's `endpoint_path`, which is right for a "
            "single-surface deployment.\n\n"
            "Name it when a deployment serves more than one profile: the URL is "
            "built from the PROFILE's path, and a target that ignored it would "
            "register the public subdomain against the operator path. That "
            "failure is quiet — the client connects to a real endpoint and "
            "lists real tools, just the wrong set."
        ),
    )

    @field_validator("url")
    @classmethod
    def _must_be_http(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.startswith(("http://", "https://")):
            raise ValueError(f"target url must be http(s), got {value!r}")
        # 'localhost' resolves to IPv6 ::1 first on macOS while runserver binds
        # IPv4 only, so the assistant reports ConnectionRefused against a server
        # curl reaches without trouble. Caught here rather than in support.
        if "//localhost" in value:
            raise ValueError(
                "use 127.0.0.1 rather than 'localhost': on macOS the name "
                "resolves to IPv6 ::1 first, but runserver binds IPv4 only, so "
                "assistants report ConnectionRefused against a working server"
            )
        return value


#: Serve every registered tool. Spelled as a value in ``tools`` rather than a
#: separate flag, because two fields can contradict each other and one cannot.
ALL_TOOLS = "*"

#: Serve every tool that declares ``public = True``.
#:
#: The alternative — naming tools in the project's config — keeps the decision
#: in a second place that drifts: add a tool, forget the list, and it is either
#: missing from the public surface or, with a denylist, published by default.
#: Here the tool's own class is the single source, and a profile asks for the
#: set rather than restating it.
PUBLIC_TOOLS = "public"


class MCPProfile(BaseModel):
    """One MCP surface: who it is for, what it serves, where it is mounted.

    A profile binds three things that must never be set independently::

        profile = (access rule, tool set, mount path)

    Binding them is the point. When they are separable, "no key configured"
    silently becomes "public server" — the endpoint answers 200 to anyone, and
    the four situations that produce it are indistinguishable:

        "I want a public server"      access_key is None
        forgot the env var in prod    access_key is None
        typo in the variable name     access_key is None
        secret never reached the pod  access_key is None

    Three of those are accidents with identical logs. A profile makes the
    deliberate case a named choice, so the accidents keep failing.

    This is **not** a return of ``allow_unauthenticated`` (removed above). That
    flag was a second way to say "open" that could contradict the first:
    ``allow_unauthenticated=False`` plus an empty key served everything
    anonymously. Here anonymity is stated once, on the profile, and validated
    against what the profile exposes.
    """
    model_config = ConfigDict(extra="forbid", frozen=False)

    name: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$",
        description="Profile identifier, e.g. 'operator' or 'public'.",
    )
    path: str = Field(
        pattern=r"^/[^\s]+$",
        description="URL path this profile is mounted at.",
    )
    access: str = Field(
        pattern="^(key|anonymous)$",
        description=(
            "How a caller proves they may use this profile. 'key' requires "
            "X-MCP-Access-Key; 'anonymous' requires nothing and MUST be stated "
            "deliberately — it is never inferred from a missing key."
        ),
    )
    access_key: Optional[str] = Field(
        default=None,
        repr=False,
        description="Required when access='key', forbidden when 'anonymous'.",
    )
    service_username: Optional[str] = Field(
        default=None,
        description="Username the key acts as. See DjangoMCPModuleConfig.",
    )
    tools: List[str] = Field(
        default_factory=list,
        description=(
            "Tool names this profile serves, or ['*'] for all. Defaults to "
            "EMPTY, never to all: a default of 'everything' is how an operator "
            "tool reaches a public endpoint by omission."
        ),
    )
    exposures: Dict[str, ModelMCPConfig] = Field(
        default_factory=dict,
        description="Model exposures scoped to this profile, keyed by 'app.Model'.",
    )
    introspection: Optional[IntrospectionConfig] = Field(
        default=None,
        description="Introspection for this profile. Forbidden when anonymous.",
    )
    rate_limit: str = Field(
        default="100/minute",
        description="Rate limit for this profile's endpoints.",
    )
    public_info: Optional[bool] = Field(
        default=None,
        description=(
            "Whether <path>info/ lists tools without a credential. None (the "
            "default) follows `access`: a key profile keeps its listing behind "
            "the key, an anonymous one serves it."
        ),
    )

    @property
    def serves_all_tools(self) -> bool:
        return ALL_TOOLS in self.tools

    def serves(self, tool) -> bool:
        """Whether this profile exposes ``tool``.

        Accepts a tool object or a bare name. The object form is required to
        resolve ``PUBLIC_TOOLS``, which reads the tool's own ``public`` flag —
        the point being that the tool declares its own exposure instead of a
        config file restating it.

        Used at execution as well as listing: filtering the listing alone is
        cosmetic, since a caller who learned an operator tool name elsewhere
        could still invoke it against a public endpoint.
        """
        if self.serves_all_tools:
            return True

        name = getattr(tool, "name", tool)
        if name in self.tools:
            return True

        if PUBLIC_TOOLS in self.tools:
            # A bare name cannot answer this — without the object there is no
            # flag to read, and guessing would be the drift this replaces.
            return bool(getattr(tool, "public", False)) if tool is not name else False

        return False

    @property
    def public_info_effective(self) -> bool:
        if self.public_info is not None:
            return self.public_info
        return self.access == "anonymous"

    @field_validator("rate_limit")
    @classmethod
    def _validate_rate_limit(cls, v: str) -> str:
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError("Rate limit must be in format: 'count/period' (e.g., '10/minute')")
        if int(parts[0]) < 1:
            raise ValueError("Rate limit count must be positive")
        if parts[1] not in ("second", "minute", "hour", "day"):
            raise ValueError("Period must be one of: second, minute, hour, day")
        return v

    @model_validator(mode="after")
    def _access_must_be_coherent(self) -> "MCPProfile":
        if self.access == "key" and not self.access_key:
            raise ValueError(
                f"MCP profile {self.name!r} declares access='key' but no key is "
                "configured. An empty key does not disable the endpoint — it "
                "would serve every anonymous request. Set access_key, or "
                "declare access='anonymous' if that is what you mean."
            )
        if self.access == "anonymous" and self.access_key:
            raise ValueError(
                f"MCP profile {self.name!r} is anonymous but carries an access "
                "key. The key would never be checked; remove it, or set "
                "access='key' so it is enforced."
            )
        if self.access == "anonymous" and self.service_username:
            raise ValueError(
                f"MCP profile {self.name!r} is anonymous but names a service "
                "user. service_username binds a KEY to an account; with no key "
                "to bind it grants that account's privileges to everyone."
            )
        return self

    @classmethod
    def _legacy_default(cls, **kwargs) -> "MCPProfile":
        """Build the implicit `default` profile from the flat config fields.

        **Bypasses the anonymous-profile restrictions, deliberately.** Those
        exist for a profile a project *declares*: they make an unsafe public
        endpoint hard to express. The legacy default is not a declaration — it
        is today's behaviour rendered in the new shape, and today a deployment
        with no key serves every tool anonymously. That is the documented
        local-development case (`_access_key_required` returns False when no key
        is configured), and a framework upgrade must not start refusing to boot
        for it.

        The restrictions arrive with the opt-in: a project that writes
        ``.profile(access="anonymous")`` is stating an intent, and gets checked.
        """
        return cls.model_construct(**kwargs)

    @model_validator(mode="after")
    def _anonymous_profiles_stay_narrow(self) -> "MCPProfile":
        """An anonymous profile must not be able to describe or change anything.

        These are the properties a reviewer would otherwise have to check by
        reading the project's config. Checked here so an unsafe public endpoint
        is hard to express rather than merely discouraged.
        """
        if self.access != "anonymous":
            return self

        if self.introspection is not None and self.introspection.enabled:
            raise ValueError(
                f"MCP profile {self.name!r} is anonymous with introspection "
                "enabled. Introspection describes internal URLs, models and "
                "schemas to whoever asks."
            )
        if self.serves_all_tools:
            raise ValueError(
                f"MCP profile {self.name!r} is anonymous and serves ALL tools. "
                "List the tools it should serve: an anonymous endpoint that "
                "inherits every registered tool publishes the operator surface "
                "the moment one is added."
            )
        for key, exposure in self.exposures.items():
            if not exposure.read_only:
                raise ValueError(
                    f"MCP profile {self.name!r} is anonymous and exposes {key!r} "
                    "for writes."
                )
        return self


class DjangoMCPModuleConfig(BaseModel):
    """
    Global configuration for the Model Context Protocol module.

    This module transforms Django into an MCP server, enabling AI agents
    to discover and interact with application data through a standardized protocol.
    """
    model_config = ConfigDict(extra="forbid", frozen=False)

    enabled: bool = Field(
        default=False,
        description="Master switch for MCP module",
    )
    endpoint_path: str = Field(
        default="/cfg/mcp/",
        pattern=r"^/[^\s]+$",
        description="URL path for MCP endpoint",
    )
    # LLM Configuration for AI agents
    llm_model: str = Field(
        default="openai/gpt-4.1-nano",
        description="Default LLM model for MCP agents (OpenRouter format)",
    )

    access_key: Optional[str] = Field(
        default=None,
        description="Static access key for agents (passed via X-MCP-Access-Key header). Required.",
        repr=False,
    )
    service_username: Optional[str] = Field(
        default=None,
        description=(
            "Username the access key acts as. When None (the default) a valid "
            "key authenticates to AnonymousUser, so tools gated on "
            "`user.is_staff` refuse. Set this to bind the key to a real, "
            "auditable service account instead of widening those gates."
        ),
    )
    rate_limit: str = Field(
        default="100/minute",
        description="Rate limit for MCP requests",
    )
    public_info: bool = Field(
        default=False,
        description=(
            "Whether GET <endpoint>/info/ lists tools without a credential. "
            "Default False: the listing is a capability map — tool names, "
            "descriptions and full input schemas — and a deployment that "
            "requires a key for JSON-RPC should not hand that map to anonymous "
            "callers. Has no effect when no access_key is configured; there is "
            "nothing to require. Set True to restore the pre-2.3 behaviour."
        ),
    )
    # REMOVED: allow_unauthenticated - use access_key instead

    install_targets: Dict[str, MCPTargetConfig] = Field(
        default_factory=dict,
        description=(
            "Endpoints `manage.py mcp_install --<name>` can register, keyed by "
            "the flag that selects them (e.g. 'local', 'prod'). Empty means the "
            "command only accepts an explicit --url."
        ),
    )

    profiles: Dict[str, MCPProfile] = Field(
        default_factory=dict,
        description=(
            "MCP surfaces this process serves, keyed by profile name. Empty "
            "(the default) means the flat fields above describe a single "
            "implicit surface — every existing deployment. Declare profiles to "
            "serve more than one, e.g. an operator endpoint behind a key plus "
            "an anonymous public one."
        ),
    )

    @model_validator(mode="after")
    def _synthesise_default_profile(self) -> "DjangoMCPModuleConfig":
        """Represent the flat fields as one profile named ``default``.

        Every deployment that never declares a profile still has exactly one
        surface; giving it a name means the request path can read a profile
        unconditionally instead of branching on whether profiles exist.

        ``access`` mirrors today's rule — a key is required when one is
        configured, and its absence is open. That is deliberately the *inferred*
        openness this whole feature exists to replace, and it stays inferred
        here: changing it would break every local deployment on upgrade. The
        replacement is opt-in, not retroactive.
        """
        if not self.profiles:
            self.profiles = {
                "default": MCPProfile._legacy_default(
                    name="default",
                    path=self.endpoint_path,
                    access="key" if self.access_key else "anonymous",
                    access_key=self.access_key,
                    service_username=self.service_username,
                    tools=[ALL_TOOLS],
                    exposures={},
                    introspection=None,
                    rate_limit=self.rate_limit,
                    public_info=self.public_info,
                )
            }
        return self

    @model_validator(mode="after")
    def _targets_must_name_a_real_profile(self) -> "DjangoMCPModuleConfig":
        """A target naming an unknown profile would fall back to `endpoint_path`.

        Silently: the registration succeeds, the client connects, and it lists
        the operator tool set from a URL meant to be public. Caught here, where
        the typo is.
        """
        for kind, target in (self.install_targets or {}).items():
            named = getattr(target, "profile", None)
            if named and named not in self.profiles:
                known = ", ".join(sorted(self.profiles)) or "none declared"
                raise ValueError(
                    f"MCP install target {kind!r} names profile {named!r}, which "
                    f"does not exist (known: {known})."
                )
        return self

    @model_validator(mode="after")
    def _profile_paths_must_be_unique(self) -> "DjangoMCPModuleConfig":
        """Two profiles on one path is one profile silently shadowing another.

        Mounting is by URL, so the second registration would never be reached —
        and which one wins depends on dict ordering, not on anything a reader
        could see. An anonymous profile shadowed by a key-protected one looks
        like a broken public endpoint; the reverse silently publishes the
        operator surface.
        """
        seen: Dict[str, str] = {}
        for name, profile in self.profiles.items():
            path = profile.path.rstrip("/") or "/"
            if path in seen:
                raise ValueError(
                    f"MCP profiles {seen[path]!r} and {name!r} are both mounted "
                    f"at {profile.path!r}. One would shadow the other."
                )
            seen[path] = name
        return self

    @field_validator("install_targets")
    @classmethod
    def _server_names_must_be_unique(
        cls, targets: Dict[str, "MCPTargetConfig"]
    ) -> Dict[str, "MCPTargetConfig"]:
        """Two targets sharing a server_name is a silent uninstall.

        Both write the same key in the assistant's config, so installing the
        second removes the first without a word — and the failure surfaces later
        as a connection error against an endpoint nobody changed.
        """
        seen: Dict[str, str] = {}
        for kind, target in targets.items():
            if target.server_name is None:
                # Derived names are <project>_<kind> and unique by construction.
                continue
            if (previous := seen.get(target.server_name)) is not None:
                raise ValueError(
                    f"targets {previous!r} and {kind!r} share server_name "
                    f"{target.server_name!r}; installing one would silently "
                    "deregister the other"
                )
            seen[target.server_name] = kind
        return targets

    # Introspection
    introspection: IntrospectionConfig = Field(
        default_factory=IntrospectionConfig,
        description="Django structure discovery settings",
    )

    # App-level exposure
    exposed_apps: Dict[str, AppMCPConfig] = Field(
        default_factory=dict,
        description="Per-app MCP configuration",
    )

    # Management commands
    commands: CommandMCPConfig = Field(
        default_factory=CommandMCPConfig,
        description="Management command execution settings",
    )

    # Data protection
    redaction: RedactionConfig = Field(
        default_factory=RedactionConfig,
        description="Automatic PII redaction settings",
    )

    # Advanced
    protocol_version: str = Field(
        default="2025-03-26",
        description="MCP protocol version to support",
    )
    server_name: str = Field(
        default="django-cfg-mcp",
        description="Server name reported in initialize handshake",
    )
    server_version: str = Field(
        default="1.0.0",
        description="Server version reported in initialize handshake",
    )
    enable_streaming: bool = Field(
        default=False,
        description="Enable SSE streaming for agent responses",
    )
    enable_audit_log: bool = Field(
        default=True,
        description="Log all MCP operations for security auditing",
    )

    @field_validator("rate_limit")
    @classmethod
    def validate_rate_limit(cls, v: str) -> str:
        """Validate rate limit format: 'count/period'."""
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError("Rate limit must be in format: 'count/period' (e.g., '10/minute')")
        count = int(parts[0])
        period = parts[1]
        if count < 1:
            raise ValueError("Rate limit count must be positive")
        if period not in ("second", "minute", "hour", "day"):
            raise ValueError(f"Period must be one of: second, minute, hour, day")
        return v

    def is_model_exposed(self, app_label: str, model_name: str) -> bool:
        """Check if a specific model is exposed to MCP."""
        app_config = self.exposed_apps.get(app_label)
        if not app_config or not app_config.enabled:
            return False
        model_config = app_config.models.get(model_name.lower())
        return model_config is not None and model_config.enabled

    def get_model_config(self, app_label: str, model_name: str) -> Optional[ModelMCPConfig]:
        """Get configuration for a specific model."""
        app_config = self.exposed_apps.get(app_label)
        if not app_config:
            return None
        return app_config.models.get(model_name.lower())

    def is_command_allowed(self, command_name: str) -> bool:
        """Check if a management command is whitelisted."""
        return (
            self.commands.enabled
            and command_name in self.commands.allowed_commands
        )
