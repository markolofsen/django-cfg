"""Facts the mail path observes but does not own.

One signal, for one reason: the gateway learns something about a recipient that
django-cfg has nowhere to put.

When a provider refuses an address as permanently suppressed, the gateway reports
it in ``result.permanent_bounces`` — explicitly, per its own source, "so the
caller records it instead of retrying". django-cfg has no suppression table of
its own, and it should not grow one: a project that keeps a suppression list
already has the schema, the vocabulary and the admin for it (in cmdop that is
``crm_email_suppressions``, whose ``hard_bounce`` reason means exactly this), and
a second copy in the framework would be a second owner of one fact.

So the framework **reports**, the project **records**. If nothing is listening,
nothing happens — the correct behaviour for a library, and why this is a signal
rather than an import of some optional model.

Why not ``EmailLog``
--------------------
It would be the obvious place and it is the wrong one. That model's docstring
draws the line deliberately: it records the **attempt**, not delivery, "which is
why the status vocabulary stops at ``sent``". A permanent bounce is a *delivery*
verdict from the provider, so filing it there would breach the one distinction
the model exists to keep. ``EmailLog`` still tells the truth about the attempt —
the message is recorded as not-sent — and this signal carries the reason.
"""

from __future__ import annotations

import django.dispatch

#: Sent once per message whose gateway response listed permanently-bounced
#: recipients, from inside the sending thread, after the response is parsed.
#:
#: Arguments:
#:     sender: the backend class that observed it.
#:     addresses: list[str] — the refused addresses, exactly as the gateway
#:         echoed them. NOT normalised here: a receiver writing to its own
#:         suppression table normalises to that table's rule, and lower-casing on
#:         the way out would hide a provider echoing a different case than we
#:         sent, which is worth being able to see.
#:     subject: str — the message subject, for correlating with ``EmailLog``.
#:     remaining: list[str] — recipients of the same message that were NOT
#:         refused. Present because a partial refusal is still a send, and a
#:         receiver that assumed "bounced ⇒ the whole message failed" would be
#:         wrong.
#:
#: Receivers must not raise: this fires on the send path, and an exception here
#: would surface as an unrelated "background email task failed". The emitter
#: guards for that, but a receiver that handles its own errors is still better.
email_permanently_bounced = django.dispatch.Signal()
