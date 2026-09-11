# 01 — Talking to an agent

A tool's caller is a model deciding what to do next from one payload. It cannot
ask you what you meant, and it will not call a second tool to disambiguate the
first unless your answer told it to.

Everything on this page follows from that.

## An empty result must be loud

A bare `[]` reads as *"nothing is wrong, there is simply none of this"*. That
is the wrong conclusion whenever the filter was too narrow, the pipeline is
broken, or the caller reached for the wrong instrument — and only the tool can
tell those apart.

So every empty path returns three things:

| Key | Answers |
|---|---|
| `filters_applied` | what was actually asked, empty values stripped |
| `empty_reason` | why nothing came back |
| `hint` | what to try next |

The default hint names the distinction the caller cannot make alone: *either
the filters are too narrow or there is no such data yet — these are different
situations; widen the filters to tell them apart.*

**A specific hint is worth far more than a generic one**, because it can name
the next *instrument* rather than the next filter: "run the health check before
concluding nobody paid" sends the agent somewhere useful; "try different
filters" sends it in a circle.

## The description is a routing decision

It is read by a model choosing between thirty tools, not by a developer reading
your module. Write what question it answers and what its answer means — and,
when a result carries a mode or a caveat the caller must not miss, say so *in
the description*, because that is the only text guaranteed to be read before
the call.

## Never let the caller mistake a limit for the world

Three different failures share one shape — the answer looks complete and is
not:

- **A silent truncation.** If you drop fields or rows to fit a budget, say so
  in the payload and name the tool that serves the full version. An
  unannounced trim becomes a fact about the world.
- **A mode the caller cannot see.** If a search ran one lane instead of two,
  the result is not "no matches" — it is "no matches *by this method*". Return
  the mode.
- **A silently ignored argument.** Answering a different question than the one
  asked, successfully, is worse than refusing. Reject the value and say which.

## Refusal and emptiness are different facts

"You may not" and "there is none" produce opposite next moves: an agent that
confuses them either retries forever or concludes the data does not exist. Keep
them structurally distinct — an `error` key with a hint, versus the empty shape
above.

Never put an exception string in either. It is caller-facing text, not a log
line.

## Serialisation is part of the contract

Datetimes, UUIDs and decimals are pervasive in real data, and a serialiser that
cannot render them does not fail politely — it raises *inside* the call, where
the agent sees a transport error and cannot distinguish "the tool is broken"
from "the data is bad". Make the fallback explicit in one shared dump helper
rather than per tool.
