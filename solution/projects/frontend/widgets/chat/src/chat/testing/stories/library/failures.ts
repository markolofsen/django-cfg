import { scenario } from "../scenario";

export const errorAfterPartial = scenario({ id: "error-after-partial", title: "Failed after a partial answer", note: "The words that arrived stay; one plain sentence says what happened.", group: "failures", prompt: "Summarise the contract." })
  .say("The contract runs for twelve months and renews automatically unless either side gives ")
  .fail("failed", "The assistant could not finish. Try again.")
  .build();

export const interrupted = scenario({ id: "interrupted", title: "Connection lost mid-answer", note: "No final frame: the turn reads as interrupted, not failed. The server may still hold the full answer.", group: "failures", prompt: "Summarise the contract." })
  .say("The contract runs for twelve months and renews automatically unless either side gives notice ")
  .lost()
  .build();

export const offline = scenario({ id: "offline", title: "Offline", note: "Nothing reached a server: one failed turn and one sentence.", group: "failures", prompt: "Hello" })
  .offline()
  .build();
