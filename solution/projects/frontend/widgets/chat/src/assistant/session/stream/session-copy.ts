import type { ChatHttpError } from '../../wire/transport';
import type { SessionCopy } from './use-session';
import type { AssistantCopy } from '../../../i18n/assistant/types';

/** The one plain sentence per refusal (see the chat contract, "Auth and errors"). */
function rejectedText(copy: AssistantCopy, error: ChatHttpError): string {
  switch (error.code) {
    case 'unauthorized':
      return copy.errAuth;
    case 'busy':
      return copy.errBusy;
    case 'invalid':
      return copy.errInvalid;
    case 'too_large':
      return copy.errTooLarge;
    case 'unsupported_type':
      return copy.errUnsupportedFile;
    case 'rate_limited':
      return copy.errRate.replace('{{seconds}}', String(error.retryAfter ?? 30));
    case 'unavailable':
      return copy.errUnavailable;
    default:
      return copy.failed;
  }
}

/** What a session says (refusals, progress labels, a failed turn) in the dictionary's language. */
export function sessionCopyFor(copy: AssistantCopy): SessionCopy {
  return {
    messages: { rejected: (error) => rejectedText(copy, error), streamError: () => copy.failed, failed: copy.failed },
    status: { thinking: copy.statusThinking, searching: copy.statusSearching, answering: copy.statusAnswering },
    failedText: copy.failed,
  };
}
