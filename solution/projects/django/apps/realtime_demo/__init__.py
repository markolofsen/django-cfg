"""Realtime demo: the reference surface for `django_cfg.modules.django_realtime`.

Topics (`realtime.py`): `demo.ping` (anonymous, an explicit `publish()`), `demo.user:{user_id}` (own user only)
and `demo.pings` (anonymous, a model hint from `broadcasts(DemoPing, ...)`). The list endpoint is
`@invalidated_by("demo.pings")`, so the generated React Query cache metadata
 carries the topic and the realtime adapter can refresh it. The demo app's
`/realtime` page shows all three.
"""
