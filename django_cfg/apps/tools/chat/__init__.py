"""The ready assistant chat: the thin installable layer (an app label for migrations) over `django_llm.agent.chat`.

Turn it on with `chat = ChatConfig()` in the project's `DjangoConfig`. Everything it does comes from the library; this
package holds the concrete tables, the default kind, the service built from config, the URLs, the admin and the two tasks.
"""
