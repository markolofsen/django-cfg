# 05 — Verifying a tool

The rule this page exists for: **registering is not working.**

A tool can import cleanly, register, and appear in `tools/list` for its whole
life while raising on every single call. Nothing about the import path proves
the call path. Finish by calling the tool.

## The ladder, cheapest first

1. **It imports.** Catches a syntax error and a bad import, nothing else.
2. **It is listed.** `tools/list` shows the name and the schema you intended,
   with the ceiling that will actually be enforced.
3. **It answers.** Call it with realistic arguments and read the payload.
4. **It answers when there is nothing.** Call it with filters that match no
   rows and confirm you get the three keys from 01, not `[]`.
5. **It answers badly-formed arguments.** `limit="lots"`, a null, a missing
   key, an absurd number. Every one should clamp, not raise.
6. **A real client can use it.** See below.

## `curl` does not verify the protocol

`curl` sends whatever JSON you type. A real client negotiates a session,
respects the transport's framing, and reads the response the way the protocol
specifies. Bugs pass a complete `curl` pass and fail every real client —
recorded twice in this project's history.

So the last step is a real MCP client — the assistant you intend people to use
— not another shell command.

## Measure the answer, not only its correctness

A payload that is right and too large has failed (see 02). When a tool returns
a list, look at the size of what came back, not just its contents. The cheapest
possible check is the length of the serialised result.

## Two shapes that look like success

- **A plausible count.** A filter returning 202 rows where 1 829 exist looks
  entirely reasonable until compared against the unfiltered total. When a
  filtered result feels small, check it against the whole before concluding the
  filter works.
- **A green test over an empty fixture.** A count or an iteration asserted
  against no data proves the code runs, not that it is right. Where a query is
  shaped by optimisations belonging to a different caller — a prefetch, a
  select-related, a slice — the failure needs real rows to appear, and the unit
  suite stays green while production raises.

## Say what you measured

A verification that reports "works" is not one. Report the arguments, the shape
of what came back, and the number — a count, a size, a duration. Anything else
is an assertion that the next person has to redo.
