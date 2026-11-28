/** The line above the composer when the connection dropped or an answer stalled; each value is the copy key it reads (`reconnecting`, `stalled`). */
export type SessionNotice = Extract<keyof AssistantCopy, 'reconnecting' | 'stalled'>;

/** Every string the assistant draws itself, in one language. The dictionaries are bundled (`locales/`), so a host passes a language and nothing else. `{{name}}` marks a value to fill. */
export interface AssistantCopy {
  /** Panel and sheet. */
  close: string;
  resize: string;
  /** A viewer who cannot write yet. */
  lockedTitle: string;
  lockedBody: string;
  lockedComposer: string;
  signIn: string;
  /** The floating button's teaser. */
  hint: string;
  /** What the assistant is doing while an answer streams. */
  statusThinking: string;
  statusSearching: string;
  statusAnswering: string;
  /** One plain sentence per refusal or failure. */
  errAuth: string;
  errBusy: string;
  errInvalid: string;
  /** A file the server refused: over the size limit, or a type it does not take. */
  errTooLarge: string;
  errUnsupportedFile: string;
  /** `{{seconds}}`: how long to wait. */
  errRate: string;
  errUnavailable: string;
  failed: string;
  /** The line above the composer when the connection drops or an answer stalls, and its action. */
  reconnecting: string;
  stalled: string;
  retry: string;
  /** Sessions: start a new chat, the list of earlier ones, and its empty line. */
  newChat: string;
  sessions: string;
  sessionsEmpty: string;
  /** The history screen: the search field, the line for a search with no hit, and the control that returns to the chat. */
  sessionsSearch: string;
  sessionsNoMatch: string;
  sessionsBack: string;
  loadError: string;
  /** The "Help" link under the composer and its list of keys. */
  helpLabel: string;
  helpDictate: string;
  helpToggle: string;
  /** Name and tooltip of the floating button. */
  fabLabel: string;
  helpSend: string;
  helpStop: string;
  helpRecall: string;
  helpNewline: string;
  /** The composer's model switch: the three starter aliases and what each is for (`useModelAliases`). */
  modelAuto: string;
  modelAutoHint: string;
  modelFast: string;
  modelFastHint: string;
  modelSmart: string;
  modelSmartHint: string;
}
