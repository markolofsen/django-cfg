---
title: Code Organization and Naming
status: current
version: "3.0"
audience: frontend, agents
last_reviewed: 2026-09-01
---

# Code Organization and Naming

[Architecture and ownership](./architecture-and-ownership.md) decides which
PACKAGE owns a thing. This page owns what happens inside one: which folder a
file goes in, what it is called, when a file must be split, and where an event
bus lives.

The failure this prevents is measurable. An application shell reached **50 files
at one level**, of which 15 belonged to no named group; one feature directory
held **20 files flat, 2832 lines**, one of them 549. Nothing was wrong with any
single file. The directory became unreadable one correct addition at a time,
because no rule said where the next file went.

## 1. A folder is a claim about ownership

**MUST**: every directory answers "what job is done here" in one phrase. If the
honest answer needs "and", it is two directories.

**MUST**: a file at the top level of a package or feature directory is either
(a) the entry point, (b) a config the tooling requires there, or (c) a member
of a group that directory names. Anything else goes in a subdirectory.

**MUST**: when a directory reaches **8 source files** (tests and stories not
counted), group them before adding the ninth. Eight is not a magic number; it
is the point past which a listing stops being scannable, and it is early enough
that grouping is still a rename rather than an untangling.

**SHOULD**: name subdirectories after the JOB, not the artifact kind. A name
like `ask/`, `wire/` or `bindings/` says what the code is FOR. `components/`,
`hooks/`, `utils/`, `types/` say only what the code IS — every feature has all
four, so the split carries no information and every change touches four
directories.

The one exception: a package's PUBLIC layers may be artifact-shaped when the
layering is the contract. Where a layer test enforces the direction of imports
between `core/`, `store/`, `primitives/` and `ui/`, those are import boundaries,
not filing cabinets.

**AVOID**: a directory holding exactly one file. Either it is going to hold
more this week, or it is a file with a longer path — one such directory held a
single helper for months and cost every importer six extra characters.

Two things that look like this rule and are not. A one-file directory whose file
is `index.ts` may be a **declared subpath boundary** — check the package's
`exports` map before touching it. And a single file that is 400+ lines across
several jobs is an **unsplit file**, not a filing accident: one held nine
exports covering three unrelated concerns, and folding it up a level satisfies
this rule while saying nothing about §3, which is the rule it was actually
breaking.

**An exemption covers the directory that earns it, never what nests inside.** A
declared subpath is not bound by the 8-file limit — but that does not license
the one-file directories underneath it, and reading the exemption as covering
the subtree leaves both in place.

**AVOID**: `misc/`, `common/`, `shared/`, `helpers/`, `lib/` inside a feature.
They are where files go when nobody decided — which is the state this page
exists to prevent. If two features share something, it moves DOWN a layer, not
sideways into a bucket.

### The fix for a bad directory name is often a name

What is banned is a name carrying no information, not the grouping under it.
Three different repairs, and the import graph picks between them:

| The directory is | Fix |
|---|---|
| a real job with a filing-cabinet name | **rename it** to the job |
| files with nothing in common | **dissolve it** into job-named subgroups |
| one file | **make it a file** one level up |

Reaching for the dissolve every time is its own error. Dissolving a six-file
`components/` whose files were all frames for one wizard would have put the
parent at 14 files — trading a bad name for a violation of the 8-file rule —
and those six genuinely shared a job, so the grouping was never the problem.
The rename was the whole fix.

**A dissolve promotes what was underneath it into view.** Expect the census to
find directories that were legal only because a wrapper hid them, and re-run
the check after each round rather than trusting the list you started with.

### A directory may be over because it holds a file that belongs elsewhere

**MUST**: before inventing a subdirectory, check whether some file in the
directory is doing a different job. One file filed under authentication imported
only the generated wire contract, was imported by no file in that directory, and
was consumed by the transport module and the generated client — both reaching
past the barrel. It recognised one server refusal shape across two client
implementations, which is transport's job, and at its call sites it decided
"server-broken" versus "invalid" — a server-health verdict, not an auth one.
Moving it down beside transport was the repair; the count falling to 8 was a
side effect, not the goal.

The tell is an import graph with an isolated node: no edges to its neighbours,
and every consumer outside the directory. Grouping such a file with the
neighbours it does not touch buries the mismatch under a plausible name.

**MUST**: test a proposed seam against the import graph before moving anything.
Two seams that filenames made obvious were both wrong: a component and a file
named as its view-model read as a pair, but the component never imports the
model — its real consumers are in two sibling directories. Grouping on the name
would have invented a coupling that does not exist.

### Counting: put the rule's own exclusions in the command

**MUST**: a census excludes tests and stories, because the limit above does.
Counting them found four directories "over" at 9 that were at 8, and hand-editing
the result afterwards dropped five that were genuinely over. Both errors came
from the same place — a definition living in the reader's head instead of the
command.

Exclude build artifacts, generated mirrors, and the scenario workbench too. A
build-output directory is full of stale paths; a generated mirror may not be
edited at the census site at all; and a workbench folder's harness files carry
no story suffix in their names, so they count as product code unless the
directory itself is excluded — which is the same mistake the gates made.

**A census built from a SYMPTOM finds only cases that already had a witness.**
Four artifact-named `types.ts` files were found by looking for files whose TEST
names disagreed with them — two subject-named tests both pointing at one
730-line `types.ts`. That worked, and it was reported as "four". The same
package held **32 more**, which the method could not see, because a `types.ts`
nobody happened to test by subject leaves no trace of the kind being searched
for. The number measured the reach of the detector, not the size of the problem.
State which one you have.

The converse also holds: not every case the symptom misses is a defect. A
`types.ts` holding ONE cohesive schema is correctly named and needs a rename at
most — so a follow-up sweep starts by reading exports, never by splitting.

**MUST**: print the FILENAMES, not the count, before acting on a census. A
corrected command was trusted on its own output, and four directories were
written off as "at 9 only because a story was counted" — all four held nine
genuine sources with no story among them. A count is a claim; the listing is the
evidence, and it costs one flag to see.

**MUST**: reconcile a census against its written disposition by NAME, in both
directions. A plan recorded a flat-directory table and declared the count
criterion PASSED; the live census returned 18 directories over the limit and the
table appeared to cover them. Matching the two by name found **two it never
mentioned** — one of which had been over the limit the whole time. The table was
not stale in the usual way (no row pointed at a directory that had moved); it
was simply incomplete, and nothing about its length said so.

Do not automate that reconciliation with a substring search either. A matcher
looking for a directory's leaf name anywhere in the document scored a real
directory as UNCOVERED because its row used brace elision to list four siblings
at once — and would equally score a directory as covered on an unrelated mention
of the same word. Brace elision and prose are both invisible to it. Use the
mechanical pass to narrow the list, then read the candidate rows.

**A test is excluded from the COUNT and included in the MOVE.** The same
directory listing cannot answer both questions: a test whose subject relocates
and which stays behind imports a deleted path. Derive the move set from the
subject, never from the threshold command's output.

**MUST**: make a bulk edit assert that it found its inputs. A script that
matched nothing reports the same "no problems" as one that matched everything
and found nothing wrong. A pass removing 21 orphaned keys from seventeen
translation catalogues printed `locales: 0 removals: 0 expected: 0` and read as
success — the glob had matched nothing, because a previous command's `cd` left
the shell elsewhere. One line makes that impossible:

```python
files = sorted(glob.glob(pattern))
assert files, "glob found nothing — wrong cwd"
```

Better still, assert the ARITHMETIC: `17 × 21 = 357 removals` is a control that
also proves no catalogue was missing a key or carrying an extra. And prefer a
language with real quoting for a probe whose result you will act on — a shell
loop counting per-key consumers reported every key as orphaned because broken
quoting left the count variable empty in every iteration, which would have
deleted five keys that live UI still renders.

### The workbench gets its own folder once it needs a harness

Where the repository has a scenario workbench, its files live beside their
subject (§2) until the point where they stop being files and become a SUBSYSTEM
— a shared harness, mock adapters, fixture builders. Then they move to a
`stories/` folder inside the directory they exercise, and the harness files go
with them.

**SHOULD**: split the workbench out when it acquires a file that is not itself a
scenario. One scenario file beside a component is an example. A harness those
scenarios import is a second thing living in the product's directory, competing
for the same eight slots and reading as ordinary source to anything that scans
by filename.

**MUST**: when the workbench moves, re-key every gate that exempted it onto the
PATH SEGMENT, never the filename. One directory exempted its harness by an exact
filename pattern, with a comment saying the pattern was "narrow on purpose,
because a rename is all it would take to widen" — and then the harness crossed a
line budget, half of it was split into a new file, and the new file kept none of
the name and therefore none of the exemption. A path segment cannot be escaped
that way: the next split lands in the same folder.

**MUST**: exclude the workbench from line budgets. A scenario measured against a
shipped component's limit does not get restrained, it gets fragmented — the file
above was cut out of its harness for a reason no reader of a scenario cares
about, and the seam it produced had to be re-justified afterwards on its own
merits.

That folder is the one directory name allowed to describe an artifact kind
rather than a job, and the exception is narrow: what binds these files is **the
workbench's own file glob**, which is a real shared consumer. `components/`,
`hooks/` and `utils/` have no such consumer, which is why §1 rejects them.

## 2. Naming

**MUST**: one convention per artifact kind, across the whole repository.

| Artifact | File name |
|---|---|
| Component | one case convention, chosen once and applied everywhere |
| Hook | `use-kebab-case.ts` |
| Pure module | `kebab-case.ts` |
| Test | `<subject>.test.ts(x)` beside its subject |
| Scenario | `<subject>.stories.tsx` beside its subject, or in `stories/` once a harness exists (§1) |
| Scenario harness | `kebab-case.tsx` inside `stories/`, prefix dropped |
| Barrel | `index.ts` |

Where an existing repository carries two component conventions in different
trees, that is a real inconsistency: it is grandfathered, not endorsed. Match
the directory you are in, and never introduce a third.

**MUST**: the file name states the SUBJECT. A file whose default export is
`Foo` is called `foo`. `renderers.ts` naming a registry of renderers says less
than `registry.ts` inside `parts/`, because the folder already said "parts".

**MUST**: when a folder carries a prefix, the files inside drop it.
`ask/projection.ts`, not `ask/ask-projection.ts`.

**A test whose name is not its subject's name is one of three things, and only
one is a rename.** 79 such tests were found in one tree; classified by what each
IMPORTS rather than by its name, 42 sat beside exactly one local subject. Those
42 were still not one defect:

1. **Several tests slicing one oversized subject.** One 1091-line module carried
   four; one 934-line module carried eleven. The names are not wrong — they are
   evidence the SUBJECT wants splitting, and renaming them all onto
   `index.test.ts` would collide and destroy the distinction. Split the subject
   and each test gets a real subject to sit beside.
2. **An artifact-named subject.** Six tests named for real subjects all pointed
   at one `types.ts`. The tests were right and the subject was misfiled.
3. **A genuine misnaming**, where the subject sits right beside it under a
   different name.

Only the third is a rename job, and even there a behaviour name sometimes
carries meaning a subject name cannot; where it does, fold the assertion into
the subject's own test instead. **Classify by imports, not by filename** — a
name-shaped heuristic (counting hyphens to tell a sentence from a symbol) put a
descriptive test name and an ordinary two-word module on the same side and
produced a 75/4 split that was pure noise.

**AVOID**: `-utils`, `-helpers`, `-manager`, `-service`, `-handler` in a file
name. They describe a shape, not a subject, and they attract unrelated code:
once `chat-utils.ts` exists, the next helper has a home regardless of whether
it belongs there.

**AVOID**: a leading `_` to mean "private". Two such directories were both read
as "do not look here" and both accumulated dead code — one held an entire
adapter for a UI that had been deleted. Privacy is expressed by not exporting
from the barrel, which the typechecker enforces; an underscore only discourages
reading.

**AVOID**: a `__tests__/` (or `tests/`) directory. A test belongs beside its
subject, per the table above, and the bucket is the one form of that rule being
broken. It is tempting for a real reason — a listing where sources and tests
alternate is harder to scan — but that is a listing problem, and it costs three
things that are not:

1. **It is an artifact-shaped directory**, which §1 rejects for the same reason
   it rejects `components/` and `hooks/`: "here are the tests" says what the
   files ARE, never what job is done there.
2. **It hides the signal "Where dead code hides" depends on.** A file whose
   only importer is its own test is visible in one line when they sit together.
   One such bucket held two tests exercising other packages entirely, which had
   gone unnoticed inside it.
3. **It buys no isolation that already exists.** Tests are excluded from the
   build by extension, not by location: no `.test.` file reaches the bundle, and
   test runners select by filename glob.

## 3. Decomposition

**MUST**: a file has ONE reason to exist. The test is whether you can name it
without "and".

**SHOULD**: keep a source file under **300 lines**, and a component under
**150**. Past that, look for the seam — there almost always is one, and it is
usually a hook.

**MUST**: extract a hook when a component holds a block of state plus the
effects that maintain it. Signals that the seam is real:

- a `useState` whose every writer is inside one `useEffect`/`useCallback` pair
- a `useMemo` over one input with no other coupling
- a group of values that are always read together

The 549-line screen named at the top of this page held five such blocks — data
loading, a roster, a capability object, a fallback ladder, and the composed
subtree. Each was already self-contained; nothing had to be redesigned to lift
them out.

**AVOID**: extracting for line count alone. A hook used once, that takes six
arguments and returns six values, has not decomposed anything — it has moved
the same coupling behind a call. If the extraction does not shorten the
argument list or narrow the surface, leave it.

**MUST**: read the DEPENDENCY ARRAY before proposing to extract a `useMemo` or
`useCallback`. React writes the argument list of the function you are about to
extract, in the source, already enumerated. A handler whose array holds six
names becomes a hook with six parameters; a memo whose array runs past ten
becomes a function with ten. **A long dependency array IS the anti-pattern,
stated in advance** — no judgement needed, just arithmetic.

**But read what each dependency IS before pricing the extraction.** The array
OVERSTATES the argument list whenever a dep is itself a hook call or a module
import: those move WITH the code and are re-read inside it. One callback listed
six deps, of which five were hook calls, a store selector and a private helper.
The extracted hook takes **one** argument. The array is where to start counting,
not where to stop.

The test is the same either way, and it cuts both directions: **does the
extracted unit take fewer inputs than the locals it replaces.** A pure function
with fifteen parameters fails it as surely as an impure one — purity is not the
test, the argument list is. And when a component comes out holding **zero
`useState` and zero `useRef`**, the seam was real: the state left with the code
that owned it.

Two things that look like seams under this test and are not:

- **A shared store or module singleton.** Four exported facade interfaces looked
  like four files until the state was read: one store whose single object
  carried every facade's mutation field, written by 20 update calls, plus a
  module-level port reached 19 times from one block. Splitting means exporting
  private state for three files to mutate. **The export list is what a file
  OFFERS; the store is what it IS** — when they disagree, the state decides,
  because a facade is a view onto state and views do not separate what state has
  joined.
- **"Computed before the return" does not mean "contains no JSX".** A block
  documented as *everything JSX needs, computed before the return* was proposed
  as a pure projection worth its own module; it builds nodes. That comment is
  about data-before-JSX ordering, a different claim entirely. Presentational
  assembly belongs beside what renders it.

**MUST**: check the directory's COUNT before extracting. A split adds a file, and
§1's limit is eight. One directory sat at exactly eight, well-decomposed, with a
genuine seam in its 786-line store — extracting would have bought a 12%
reduction (still twice the limit) at the price of a §1 breach, with no grouping
available to absorb it. **A split that trades a §1 breach for a §3 near-miss
makes the tree worse in two places.** Where the extracted files DO share a job,
group them — that is what makes the trade payable.

**MUST**: give a long file a verdict, SPLIT or LEAVE-FLAT, with the reason
named. Length is a prompt to look for a seam, never evidence that one exists.
Measured over the twelve largest files in one tree, **five had no seam to take**:
a route registry whose 61 records and derived union stop being exhaustive once
separated; a boot wiring point whose ~45 attachment calls are ORDERED, and the
order is what the boot tests assert; a catalogue of 57 pure projections that all
take the same type and serve the same three consumers, so the coupling survives
the move; a 15-arm dispatch table over one wire contract; and one store whose
every action mutates the same map. A plan driven by the count alone would have
split all five.

**A stated diagnostic can fail to fire, and that is not a verdict.** The largest
file measured — 1385 lines — holds **one** `useState`, **one** `useEffect` and
no `useRef`, against nine `useMemo` and fifteen `useCallback`. The signal above
finds almost nothing in it; its mass is three render closures each capturing ~15
locals, and extracting those is exactly the six-arguments-six-values move this
section forbids. When the diagnostic does not fire, the answer is neither "no
problem" nor "extract anyway" — the file needs a different question asked, and
saying so beats producing the anti-pattern to hit a number.

**A deferred count decays like a stale comment.** Two sibling tracks both
recorded "55 over-length files" and neither re-measured, because a number nobody
acts on is never checked; the real figure was 121. It stayed plausible for
months — 55 was still exactly one package's share. Re-measure a deferred count
when you pick the work up, before planning against it.

**AVOID**: a `utils.ts` that grows. Each helper belongs beside the thing it
serves, or one layer down if two features need it.

## 4. Event buses

An event bus is the mechanism for "this just happened" — [Events and
notifications](./events-and-notifications.md) owns WHEN to use one and the
three tests a prop must pass first. This section owns WHERE the code lives.

### There is no shared bus directory, and there must not be one

**MUST**: a bus is declared **in the package that emits its events**, beside
the state it announces. The package that owns a conversation declares the
conversation's event map; the transport package declares the bus interface it
bridges server push into.

A single `buses/` or `events/` directory collecting every domain's bus is
wrong for three reasons, in increasing order of cost:

1. **It inverts dependencies.** A package that emits its own events would have
   to import a shared module to talk to itself — and a package must not take a
   transport dependency to talk to itself. Model your bus on an existing one;
   do not import it across a boundary the package otherwise does not have.
2. **It invites a singleton.** One directory of buses becomes one bus per name,
   module-scoped — and then two instances of the same surface open side by side
   hear each other's events, which is unfixable without splitting them again.
3. **It hides the ownership question.** "Where does this event live" is the
   same question as "who owns this fact", and answering it with a filing
   location skips it.

**MUST**: one bus per **unit of isolation**, created by ref beside its store —
not per package, and never module-scoped. Two instances of one surface must not
hear each other.

**SHOULD**: a bus that outgrows one file splits by ROLE, next to itself:

```text
core/
  events.ts          ← the map, the types, the factory
  events.test.ts     ← delivery, unsubscribe, the mid-dispatch case
```

Not by event name, and not into a sibling `events/` folder — the map is one
type and splitting it hides which names exist.

**MUST**: when a second domain in the same package needs events, add a second
NAMED map rather than widening the first. Two domains are two vocabularies;
merging them gives every subscriber autocomplete over events it can never
receive.

**AVOID**: routing a bus through props to reach a subscriber. If a component
takes `events` only to pass it down, the subscriber should read it from the
provider the emitter already mounts.

## 5. Barrels

**MUST**: a package's public surface is its `index.ts`. Consumers import from
the package name or a declared subpath, never through a deep path into `src/`.

**SHOULD**: a feature-internal folder gets a barrel only when three or more
files outside it import from it. Below that the barrel is indirection with a
maintenance cost — it goes stale silently, because an export naming a deleted
file only fails when something imports it.

**MUST**: when you delete a file, grep the barrel. A barrel is the one place a
dead reference survives a delete, and the error surfaces in whichever unrelated
package next imports the barrel.

**MUST**: grep `package.json`'s `exports` map too, and treat it as the worse
case. One package advertised a subpath for a file deleted when its role moved
elsewhere; a comment beside the entry even said that subpath was "deliberately
gone", which was true of the file and had never been made true of the entry. A
dead barrel line is at least type-checked; a dead subpath is data in a JSON file
that nothing reads until someone imports it, and the error then names a package
rather than the delete that caused it.

Removing a subpath that RESOLVES is a contract change — decide it as one, or
re-point it, as two packages' hook subpaths both were when their single file
moved. Removing one that resolves to nothing is just a delete: no consumer can
be relying on it, and leaving it misleads the next reader of the map.

## 6. What breaks when a file moves

The typechecker repairs imports and nothing else. Several mechanisms key on the
PATH, and each stops matching when a file moves — so what was frozen becomes a
fresh violation and what was asserted stops being asserted.

They fail in BOTH directions, and the loud one is the easier to misread. A dead
key in a baseline turns a gate RED, listing untouched strings as if they were
just written; the honest diagnosis is a filing artifact, but it looks exactly
like new debt, and "fix the findings" is then the wrong response. A dead
`readFileSync` path or a lapsed lint glob does the opposite and says nothing at
all. Before acting on a gate that changed colour during a reorganization,
establish whether its KEYS still resolve.

**MUST**: make the key check PRINT what it counted. "Do the keys still resolve"
is the right question, and a script answering it can return a confident zero
having examined nothing. One existence assertion reported `entries=2 dead=0` on
a baseline holding 83 paths — the file keys on two top-level fields, so the loop
tested two literal strings and found their absence from disk irrelevant. The
count was real; it counted the wrong thing. **A zero from a probe whose SHAPE
assumption is wrong is indistinguishable from a clean result**, so print the
number of paths examined beside the number dead, and sanity-check the first
against what the file is supposed to hold.

The same assertion, once correct, earns its place: it caught a dead entry left
by a deletion made minutes earlier in the same session and already forgotten.
**Re-keying is not a step at the end of a reorganization; it belongs in the same
command as the move**, because the window in which you remember the move is
shorter than the window in which the stale key survives.

**MUST**: check that a path-keyed mechanism actually FIRED before explaining a
red gate with it. The mechanisms above are real and this section describes them
accurately, which is precisely what makes them attractive as explanations for a
gate that changed colour during a reorganization. One gate was explained twice,
wrongly, in ways that both felt earned: first as another session's feature work,
then — after the history showed **30 of 36 flagged files had been renamed by the
reorganization itself** — as baseline drift from those renames.

Both were wrong, and the second is the instructive one, because every fact it
rested on was true. The renames happened; the sequence was right; this page
names that exact failure. It still did not apply, and three checks said so:

- the baseline had **zero dead entries** — a path-keyed baseline broken by
  renames is full of them;
- seven of the flagged files **already had frozen entries at their current
  paths**;
- the renames were an **ancestor** of the last baseline write.

The debt had simply never been frozen. One file settled it: a flagged expression
**byte-identical before and after its rename**, with no baseline entry at either
path — old expression, real violation, unrelated to the move.

**Confirming that a mechanism EXISTS is not confirming that it FIRED.** The test
for firing is different from the test for plausibility, and only the first one
settles anything. Ask what the mechanism REQUIRES — a dead key, a lapsed glob, a
stale path — and go look for that, not for the story.

Three traps, in the order they fire:

- **"Last touched" is not provenance.** `git log -1` returns today for nearly
  every file when two sessions have been editing all day. It cannot separate
  *introduced here* from *moved here*. `--follow --diff-filter=A` can, and
  `--name-status` names the rename.
- **"Unknown to the baseline" is not "new".** A classifier bucketing violations
  as *new expression / moved basename / new file* puts every renamed file in the
  last bucket, because the baseline never held the new path. The bucket name
  asserted a conclusion the test could not reach — a claim disguised as a
  measurement.
- **A piped gate reports the pager's exit code.** `node check.mjs | tail` prints
  a zero status while the gate exits 1. Run it unpiped or read `PIPESTATUS`;
  two RED gates have already been reported as green this way.

**MUST**: after moving a file, grep its basename across build scripts, JSON
config and test sources — not only for `import`. Three real cases, all from one
reorganization:

- **A lint exemption naming a file.** A config listed four exempted paths; two
  had moved and a third no longer existed. The exemption stops applying, so a
  file that was green turns red for a reason unrelated to the change.
- **A baseline keyed by path.** A debt baseline freezes existing violations per
  file. A move makes the frozen entry dead AND reports the same untouched
  strings as new debt; 27 keys were stale across four separate groupings.
- **A test that reads source with `readFileSync`.** These assert on COMMENTS —
  that a doc still says what it promises — which no behavioural test and no
  typecheck can observe. One broke three phases before it was noticed.

**MUST**: enumerate those reads by the READ CALL, never by a basename. A path
breaks when either end of it moves, and a basename search only ever finds one
end — the one whose subject you moved. It cannot see a test that was itself
carried into a subfolder and now reaches `./neighbour.tsx` for a file that
stayed put, or `../store/x.ts` for a layer that is suddenly two levels up.

```bash
grep -rn 'read("\.\|new URL("\.' --include='*.test.ts' --include='*.test.tsx' .
```

Measured on one reorganization: eleven paths of the kind a basename search
finds, six of the kind it cannot, and one of those six named no moved file at
all — a test reading a sibling that had never moved, invisible to every
filename-shaped search. Both kinds throw when the suite runs, so the risk is
bounded; the cost of the wrong census is that you believe you are done.

**MUST NOT** decide where an import should point from a FIXED-SIZE window of it.
`grep -B3` on a seven-line `import { … }` block shows its last three lines and
hides the rest, and a multi-symbol import is exactly the construct a line budget
truncates. One such view showed a type import while concealing two value imports
above it; the resulting blanket rewrite sent a consumer to the half of a split
that declares neither, and fifteen tests failed. **A truncated view of a
construct reads exactly like the whole construct** — nothing in the output says
a line was withheld.

When a split divides a file's exports, verify by SYMBOL rather than by path:
parse the whole import block and check each named symbol against the file that
declares it. That is a few lines of script, it cannot be fooled by a window
size, and it answers the question the grep only appeared to.

```bash
grep -n -A20 '^import {' path/to/file.ts   # if you must grep, bound the END, not the start
```

**MUST**: split a TEST when its subject splits. A test file covering symbols
that now live in two files belongs in two files — the same adjacency rule as
§2, applied after the fact. Keep the assertion count as the control: 15 tests in
must be 15 tests out.

**MUST**: fix the imports pointing OUT of the moved file, not only those
pointing at it. A file that changes depth breaks its own relative specifiers,
and the grep above looks the other way — at consumers. Three folds in one round
each shipped this: a `../x` import from a file now sitting beside `x`, a
`../../y` from a file now one level shallower, and two tests importing their own
former names.

The typechecker catches all of these, which is exactly why they escaped: the
workspace typecheck was already red for an unrelated package under concurrent
edit, and the first symptom was the dev server failing at runtime on an open
screen. **A red gate belonging to someone else hides your own.** Resolve every
relative specifier against the filesystem instead — a second, cheap check that
does not care who else broke the build. Walk the source roots, extract every
relative specifier, and try each candidate extension and `/index` form; anything
that resolves to nothing is a real break. The repository profile can carry the
script and the list of known-good exceptions.

**SHOULD**: express an exemption as a glob over the property that earns it
(`**/hosts/*.tsx`, `status/*Item.tsx`), not as a list of names. A glob states the
RULE; a list states today's instances of it.

**MUST NOT**: repair a path inside a dated record — a shipped audit, an
evidence file, a completed track's plan. Those describe where a file sat when
the work happened, and "fixing" them destroys the only account of that. The
grep after a move will hit them; the correct action is to leave them and say
you did. A live mechanism keys on a path to DO something, and that is what
needs repairing.

**MUST**: change a key by editing the KEY, never by re-serializing the file. A
baseline is shared state — other agents and other tracks have entries in it —
and a whole-file rewrite touches every one of them. Dumping one baseline back
out through a JSON serializer with different escaping rewrote punctuation
escapes across **33 unrelated entries** while renaming two keys. Nothing failed;
the values were equivalent. It was still 33 lines of another track's diff,
authored silently. Verify with `git diff --numstat` afterwards: a two-key rename
is a two-line diff, and any larger number is the rewrite showing itself.

**MUST**: when re-keying a path-keyed entry, match by CONTENT, using the tool's
own notion of equality rather than a substring test. Both directions have
already failed: a file carrying the right NAME and none of the strings
(re-keying to it would freeze debt that no longer exists), and four strings that
a naive substring check reported absent because three had been re-wrapped across
JSX lines and one had its interpolation normalized. Most checkers can print what
they currently find; diff against that.

**MUST**: treat a zero from a search as "I could not see" until a control in the
SAME command proves otherwise. Four times in one reorganization a zero meant
the query was wrong, never the data — each wearing a different disguise, and
each plausible enough to have been acted on:

| The search | Read as | Actually true |
|---|---|---|
| a baseline probed for the flagged COPY | "none of these strings are frozen" | keyed by PATH; the strings are the values |
| consumers, with the file's own directory excluded | "this hook is dead" | its consumer imports through the BARREL, which lives in the excluded directory |
| `grep -c` for a dotted key in nested JSON | "this key is gone" | the dotted path never appears on one line |
| `grep -r --include=*.ts` with the glob UNQUOTED | "no file imports this" | the shell expanded the glob first; grep never got the flag. Quoted, the same probe returned 50 |

The fourth is the one to fear, because it announced itself and was believed
anyway: `no matches found: --include=*.ts` printed above every zero, and the
zeros still went into a table. **An error line above a result invalidates the
result** — read the whole output, not the number at the end.

Two habits close the other three. **Probe for something the source certainly
contains** in the same command — if that also scores zero, the query is broken,
not the data. And **check what your filter removed**: excluding a directory to
suppress self-references also hides the barrel inside it, which is how most
consumers actually reach a file. Search for the SYMBOL across the whole tree and
discount the self-references by reading them, rather than filtering first.

Without a control, "absent" and "invisible to this query" produce identical
output, and the wrong reading is the one that looks like a finding.

## 7. Where dead code hides

Every one of these was found in the state described:

- **A barrel export with no consumer.** Delete the export first; the file's
  real reachability becomes visible immediately. One barrel published 14 symbols
  of which **12 had no importer anywhere** — four panel sections, a tone chip
  and an entire formatting surface, all public API that nothing reached for. It
  now publishes 3.

  **MUST NOT count exported symbols with a line-oriented grep.** Both attempts
  were wrong, in opposite directions. `grep -c '^export '` returned 9, because
  one `export { … }` block spanned nine lines and counts once. A brace-matching
  `grep -oE '\{[^}]*\}'` then returned 8, because `[^}]*` cannot cross a newline
  and so skipped that block's seven symbols entirely. The arithmetic is the
  control, and it has to balance: **removed + added + kept = before**. Run that
  and a miscount cannot survive — the first attempt gave 12 + 1 + 2 ≠ 9 and said
  so.

  **Two probes are needed, and each is blind to what the other finds.** Asking
  "who imports this SYMBOL" finds dead exports but misses a consumer that
  bypasses the barrel: one symbol scored zero and yet a page imported it
  directly by path. Asking "who names this PATH" finds that reach-through and
  says nothing about which exports are dead. Run both, and use `\b` word
  boundaries — an unbounded probe let a same-named function in an unrelated
  feature read as three consumers of this one.

  **The typecheck cannot substitute for the second probe.** Deleting an export
  does not break an importer that never used the barrel, so narrowing a barrel
  to its reached symbols left both the package and the app typechecking green
  while a page still reached through to the internal path. A green build after a
  narrowing is evidence about the barrel, not about the boundary.

  And a reach-through is not a licence to keep the symbol private — it is a
  consumer the barrel was failing to serve. Export it and repoint the import;
  hiding it would leave the same dependency, spelled worse.
- **A file whose only importer is its own test.** The test proves the code
  parses, not that anything needs it.
- **A scenario for a component the product no longer mounts.** It renders, so it
  looks alive — and it is the reason a deleted UI keeps its dependency.
- **A helper pair that only calls each other.** Two modules imported each other
  and nothing imported either.
- **A one-line re-export shim of another package.** One file was a single
  `export { x } from "<package>"` and nothing imported it. A shim looks like
  architecture — a seam, a local name for a shared thing — but a seam with no
  consumer is a file. Collapse it into the barrel; whether the SYMBOL then
  survives is a separate question the collapse makes visible.
- **An `_`-prefixed or archive directory.** Excluded from the typechecker's
  project, so it never reports the rot.

**SHOULD**: when a deletion leaves a file with one remaining export, ask whether
that export belongs where it now sits. One file kept its name after losing the
hook it was named for.
