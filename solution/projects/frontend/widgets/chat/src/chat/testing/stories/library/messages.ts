import { scenario } from "../scenario";
import { LONG_WORD, WIDE_TABLE } from "./payloads";

export const plainAnswer = scenario({ id: "plain-answer", title: "Streaming answer", note: "Words arrive token by token: a heading, a list, code, a quote.", group: "messages", prompt: "How do I convert dates to timestamps?" })
  .say("## Converting dates\n\nThere are **two** shapes to handle:\n\n1. Text such as `2026-11-10`\n2. Numbers that are already timestamps\n\n")
  .say("```ts\nconst toTimestamp = (value: string | number) =>\n  typeof value === 'number' ? value : Date.parse(value);\n```\n\n")
  .say("> Parse once, at the edge, and keep timestamps everywhere else.\n")
  .finish()
  .build();

export const longContent = scenario({ id: "long-content", title: "Long content", note: "A very long word and a wide table: the bubble must not grow wider than its column.", group: "messages", prompt: "Show me the pricing table." })
  .say(`Here is the table. One unbroken string follows: ${LONG_WORD}\n\n${WIDE_TABLE}\n`)
  .finish()
  .build();
