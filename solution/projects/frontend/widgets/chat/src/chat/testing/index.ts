// Test doubles: mock adapter, chat factory, chunk builders.
//
// Exported under the "./testing" subpath so consumers can drive a chat in their
// own tests. Never re-exported from the package root.
//
// Stories use these too, and that is the reason they live in `src/` rather than
// beside the story files: a second scripted adapter inside the Storybook app
// would drift from the chunk vocabulary it imitates, and a story passing
// against a private mock proves nothing about the shipped adapter contract.

export { mockAdapter, tokenize } from "./mock-adapter";
export type { MockOptions } from "./mock-adapter";
export { mockVoice } from "./mock-voice";
export type { MockVoiceOptions } from "./mock-voice";
export { MOCK_TOOL_CATALOGUE, MOCK_TOOL_CATALOGUE_NO_STT } from "./mock-tools";
export { assertChatClient, chatClientProblems, ChatClientDriftError } from "./assert-chat-client";
export type { ChatClientOptions, ChatClientProblem } from "./assert-chat-client";
