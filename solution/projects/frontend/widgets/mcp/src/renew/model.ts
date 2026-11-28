/** The renew section's rules that need no React: `{placeholders}` and the confirm step. */

/** `{name}` placeholders of a dictionary string. */
export function fillText(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (whole, key: string) => (key in values ? String(values[key]) : whole));
}

/** The inline two-step ("Renew" -> "Are you sure?" -> done): ask, then confirm or keep; a failure returns to the first step with a message. */
export type Step = 'idle' | 'asking' | 'busy' | 'failed';
export type StepEvent = 'ask' | 'keep' | 'start' | 'done' | 'fail';

export function nextStep(step: Step, event: StepEvent): Step {
  switch (event) {
    case 'ask':
      return step === 'idle' || step === 'failed' ? 'asking' : step;
    case 'keep':
      return step === 'asking' ? 'idle' : step;
    case 'start':
      return step === 'asking' ? 'busy' : step;
    case 'done':
      return step === 'busy' ? 'idle' : step;
    case 'fail':
      return step === 'busy' ? 'failed' : step;
  }
}
