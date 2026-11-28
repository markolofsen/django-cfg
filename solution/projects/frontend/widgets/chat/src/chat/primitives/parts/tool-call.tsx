import { createContext, useContext, type ReactNode } from "react";

import { subagentMessages, type ChatMessage, type ToolPart } from "../../core/conversation/parts";
import { MessageContent } from "./message";

/**
 * A tool call, as composed parts.
 *
 * The root takes `part` and `children` and nothing else. Everything that would
 * have been `showInput` / `showOutput` / `inputLabel` is a component the host
 * either renders or does not — AI Elements' shape, and the concrete cure for
 * "a boolean prop is a component someone declined to write".
 */

const ToolPartContext = createContext<ToolPart | null>(null);

function useToolPart(): ToolPart {
  const part = useContext(ToolPartContext);
  if (part === null) throw new Error("tool-call parts must render inside <ToolCall>");
  return part;
}

export interface ToolCallProps {
  readonly part: ToolPart;
  readonly children: ReactNode;
  readonly className?: string;
  /**
   * Disclosure state, as DATA on the root. The host owns the rule; this only
   * publishes the answer, so a stylesheet can turn the chevron without the
   * primitive knowing a chevron exists.
   */
  readonly open?: boolean;
}

export function ToolCall({ part, children, className, open }: ToolCallProps) {
  return (
    <ToolPartContext.Provider value={part}>
      <div
        className={className}
        data-tool={part.toolName}
        data-state={part.toolState.state}
        // Absent rather than `false`: CSS selects on presence, and
        // `data-open="false"` matches `[data-open]` just as well as "true".
        data-open={open === true ? "" : undefined}
      >
        {children}
      </div>
    </ToolPartContext.Provider>
  );
}

export interface ToolCallHeaderProps {
  readonly className?: string;
  /** Receives the live state so a host can label it without reading context. */
  readonly children?: (part: ToolPart) => ReactNode;
}

export function ToolCallHeader({ className, children }: ToolCallHeaderProps) {
  const part = useToolPart();
  return (
    <div className={className}>{children === undefined ? part.toolName : children(part)}</div>
  );
}

export interface ToolCallInputProps {
  readonly className?: string;
  readonly children?: (input: unknown, streaming: boolean) => ReactNode;
}

/**
 * Arguments, including while they stream in.
 *
 * During `input-streaming` the payload is a PARTIAL JSON string, not an object.
 * Handing a host `JSON.parse`d garbage — or throwing — is how a tool card
 * breaks the whole transcript mid-turn, so the raw text is passed through with
 * `streaming` true and the host decides what to show.
 */
export function ToolCallInput({ className, children }: ToolCallInputProps) {
  const { toolState } = useToolPart();
  const streaming = toolState.state === "input-streaming";
  const input = streaming ? toolState.inputText : toolState.input;
  if (children !== undefined) return <div className={className}>{children(input, streaming)}</div>;
  return <div className={className}>{typeof input === "string" ? input : JSON.stringify(input)}</div>;
}

export interface ToolCallOutputProps {
  readonly className?: string;
  readonly children?: (output: unknown) => ReactNode;
  /** Rendered instead when the call failed. Absent ⇒ the error text is shown. */
  readonly error?: (message: string) => ReactNode;
}

export function ToolCallOutput({ className, children, error }: ToolCallOutputProps) {
  const { toolState } = useToolPart();

  if (toolState.state === "output-error") {
    return (
      <div className={className} data-error="">
        {error === undefined ? toolState.error : error(toolState.error)}
      </div>
    );
  }
  // Nothing to show yet is NOT an empty output: rendering an empty box while a
  // tool runs reads as "it returned nothing".
  if (toolState.state !== "output-available") return null;

  const { output } = toolState;
  if (children !== undefined) return <div className={className}>{children(output)}</div>;
  return (
    <div className={className}>{typeof output === "string" ? output : JSON.stringify(output)}</div>
  );
}

export interface SubagentThreadProps {
  readonly className?: string;
  readonly children?: (message: ChatMessage) => ReactNode;
}

/**
 * The subagent's own conversation, nested and read-only.
 *
 * Read-only is a property of the data, not a flag: these messages live inside a
 * completed tool call, so there is no composer and nothing to send. Renders
 * nothing when the tool ran no subagent, which is the ordinary case.
 *
 * Part renderers are inherited from the enclosing registry — see
 * `part-registry.tsx`. A nested thread that had to re-register them would
 * silently lose whichever the host forgot.
 */
export function SubagentThread({ className, children }: SubagentThreadProps) {
  const messages = subagentMessages(useToolPart());
  if (messages === undefined) return null;

  return (
    <div className={className} data-subagent="">
      {messages.map((message) =>
        children === undefined ? (
          <MessageContent key={message.id} message={message} />
        ) : (
          <div key={message.id}>{children(message)}</div>
        ),
      )}
    </div>
  );
}
