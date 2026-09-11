---
title: Nested Apps and Super-Apps
status: current
version: "1.0"
audience: backend, platform, agents
last_reviewed: 2026-09-04
---

# Nested Apps and Super-Apps

A **super-app** is one package that groups several Django apps beneath it: an
umbrella that owns composition — registration, routing, admin loading — while
each child owns its models, label, migrations, and tests.

Use it when a product surface has grown several domains that ship together,
share a URL prefix and an audience, but must not share a migration history.
Everything below assumes the umbrella contains a sub-package of child apps.

This page is about the *shape*. Which surfaces are built this way, and where
their registry lives, is in [`../custom/`](../custom/README.md).

## When a super-app is the right shape

Reach for it only when **all** of these hold:

- Several domains share one external prefix, one audience, and one release.
- Each domain owns durable state that deserves its own migration history.
- The domains are cohesive enough that a reader expects to find them together.

**AVOID** it for a single domain that is merely large. Nesting one app inside
an umbrella buys nothing and costs every trap on this page. Split by *what owns
which facts*, never by file count.

**AVOID** it as a staging area for code you have not decided how to place.
An umbrella whose children have no common audience is a directory, not an
architecture.

## The umbrella owns composition, never state

**MUST**: keep the umbrella model-free. It owns registration, the URL surface,
and the admin barrel. A model on the umbrella gives one super-app two migration
histories at different depths, and no reader can predict which one a change
lands in.

**MUST**: give every child its own `AppConfig`, its own explicit label, and its
own migrations directory. This is the whole point of the shape — see
[Architecture and ownership](./architecture-and-ownership.md).

**MUST NOT**: flatten a child's models or migrations into the umbrella later.
Merging two migration histories is not reversible by editing code.

Children are siblings, not a hierarchy. A child **MUST NOT** import another
child's private helpers; cross-child needs go through a public service, exactly
as they would between unrelated apps. Their proximity in the tree is not a
license to couple them.

## The trap that defines the shape

**A sub-package of child apps shadows the umbrella's conventional `apps.py`
module.** A package directory and a module of the same name cannot coexist, so
the umbrella's `AppConfig` cannot live where every Django reader looks for it.

This has exactly two working resolutions. Pick one per project and apply it
everywhere — the failure mode is silence, so consistency is what makes it
reviewable.

**Declare the umbrella `AppConfig` in the umbrella's `__init__.py`**, and
register it by its **explicit class path**. Registering the package path alone
makes Django look for the shadowed module and fall back to a base no-op config.

**Or re-export that class from the child sub-package's `__init__.py`.** Django
resolves a bare package path by importing `<package>.apps` and scanning *that
namespace* — not the parent's `__init__.py`. Where the sub-package is what
carries the name, the re-export is what makes discovery succeed.

**MUST**: state which resolution is in use, and why, in a docstring at the
declaration site. The next reader's first instinct is to "fix" the odd location
by moving the class to `apps.py`, which reintroduces the shadowing.

**The failure is silent, and that is the danger.** Django does not raise when it
cannot find your `AppConfig`. It installs a base one, and the system starts
clean: `ready()` never runs, so every signal receiver stays unregistered and
every side-effect import never happens. Nothing is logged. The symptom appears
later and far away — a pipeline that quietly does nothing.

**MUST**: verify `ready()` actually runs after touching umbrella registration.
Assert an observable effect of it — a registered receiver, a loaded admin — not
that the process boots. Booting proves nothing here.

Do not restore a removed framework mechanism to solve this. A module-level
config hint that a modern framework version ignores is not a fallback; it is a
line that reads like insurance and provides none.

## Autodiscovery stops at registered apps

Admin autodiscovery scans each **registered** app's `admin` module. It does not
walk into the children of an unregistered parent.

So a super-app needs an **admin barrel** on the umbrella that imports every
child's admin, and an umbrella `ready()` that imports the barrel.

**MUST**: extend the barrel in the same change that adds a child. A missing line
loses that child's entire admin surface with no error at any layer.

This generalizes past admin: any registry populated by import side effects needs
the same deliberate barrel. Proximity in the tree registers nothing.

## Registration is per app, not per umbrella

**MUST**: register the umbrella **and** every child in the project's app
registry. Registering only the umbrella leaves the children's models invisible
to migrations, and registering only the children skips the umbrella's `ready()`.

The registry is the truth about what is active. A child present on disk and
absent from the registry imports, tests, and defines models perfectly well —
while shipping nothing.

## Labels are a global namespace

A child's label is global to the project, not scoped by its umbrella. Two
umbrellas each holding a plausible generic name collide, and the loser is
whichever loads second.

**MUST**: prefix a child's label with its umbrella. A collision surfaces as a
startup error at best, and as migrations attributed to the wrong app at worst.

**Renaming a label after its migrations are applied is a migration-state
change, not a text edit.** The recorded history keys on the old label, so the
new one reads as an app with nothing applied and the initial migration is
attempted again on live tables.

It is still doable, and worth doing where the namespace matters. What decides
the cost is whether the label leaked into anything physical:

- **Cheap** where every model declares an explicit `db_table`, so no table is
  named after the label and nothing is renamed on disk.
- **Expensive** where tables were auto-named from the label, which turns the
  rename into real DDL against live data.

Either way the code change is only half of it. A rename **MUST** also repoint
the recorded migration history and the content types — the latter is what
admin permissions and generic relations resolve through — in one transaction,
once per installation, verifying the migration graph before it commits.

**MUST**: rewrite every reference to the old label in the same change. They
hide in more places than a search for the app's name suggests: migration
dependencies (including ones a formatter split across lines), `to=` targets
inside migrations, string-form relations in model code, `get_model()` calls,
and signal receivers connected by a lazy `sender=` string. A missed one fails
at system-check time, not at import — so run the checks, not just the tests.

> **Retracted.** An earlier version of this page said a label with applied
> migrations **MUST NOT** be renamed, and to prefix only new ones. That was too
> strong: it left a project permanently stuck with whatever names it started
> with. The rename is a migration-state change to plan for, not a prohibition.

Give each child a `verbose_name` that names its umbrella too. An operator
reading an admin index sees labels from every app in one flat list.

## One URL owner per super-app

**SHOULD**: let the umbrella own the routing surface, importing views from
children and mounting them under one prefix. Children then expose views and no
`urls.py` of their own. One file answers "what does this surface serve", and
route conflicts are visible in the diff that causes them.

The alternative — each child owning a `urls.py` that the umbrella includes —
is legitimate where children are genuinely independent. It is a real trade:
better isolation, at the cost that no single file shows the whole surface.

**MUST**: pick one per super-app and keep it. Half-and-half is how a route gets
served twice under two names that drift apart.

**MUST NOT**: also register a super-app's routes by hand wherever the project
mounts its API. Where the framework mounts a group automatically, a second
manual mount produces duplicate routes and a duplicated generated client.

Order routes so a permissive pattern cannot shadow a literal sibling: a
catch-all path segment placed above a fixed one silently swallows it.

Keep reverse names unique across the whole super-app by prefixing them with it.
Children share one namespace once the umbrella wires them together.

## Documentation and tests follow ownership

**SHOULD**: give the umbrella a README that lists every child, its
responsibility and its label, and states which resolutions above are in use.
That table is how a reader learns what is *supposed* to be registered — the
fastest way to spot a child that quietly is not.

**MUST**: give each child its own tests, runnable alone. A super-app whose
suite only runs as a whole hides which child broke, and slows the loop that
would have told you.

## Review checklist

- Does the umbrella own composition only, with no models of its own?
- Does every child have its own `AppConfig`, prefixed label, and migrations?
- Is the umbrella's `AppConfig` reachable despite the shadowed module — and is
  the resolution explained where it is declared?
- Was `ready()` verified by an observable effect, not by a clean boot?
- Are the umbrella and every child registered?
- Does the admin barrel list every child?
- Does exactly one layer own routing, with no hand-registered duplicate mount?
- Can each child's tests run on their own?
