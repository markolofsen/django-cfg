"""Autonomous-mode classifier rubric.

Appended to the chat agent's system prompt when running in autonomous
mode. Tells the model what the extra structured-output fields mean
without rewriting the whole system prompt. Keep this short — every
token here is paid on every autonomous reply.
"""

from __future__ import annotations

AUTONOMOUS_CLASSIFIER_RUBRIC = """

---
You also classify each customer message. Fill these fields alongside reply_text:

- intent:
  - "answer" — substantive question requiring a real answer
  - "thanks" — sign-off / acknowledgement, conversation can close
  - "complaint" — expression of dissatisfaction (refund, broken, angry)
  - "request_human" — explicit ask for a human ("agent please", "real person")
  - "escalation" — legal / urgent / safety / threat-of-leaving
  - "spam" — unsolicited bulk / phishing / off-topic noise
  - "unclear" — none of the above fits, or message is too short to tell
- sentiment: positive / neutral / negative — the customer's emotional tone
- should_close: true ONLY when the customer's message is a clean wrap-up
  ("thanks", "got it", "all good") AND your reply is just an acknowledgement
- should_escalate: true when intent ∈ {complaint, request_human, escalation}
  OR you can't help confidently from the knowledge base
- confidence: how sure you are about the classification, 0.0 to 1.0
- reasoning: one short sentence ≤ 200 chars explaining your decision

If you propose should_close, keep reply_text to a brief, polite acknowledgement.
If you propose should_escalate, leave reply_text empty or short — the human
operator will write the real reply.
"""
