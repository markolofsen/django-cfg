import type { Meta, StoryObj } from "@storybook/react-vite";
import { Sparkles, TriangleAlert, Info } from "lucide-react";

import {
  ComposerBanner,
  ComposerBannerAction,
  ComposerBannerActions,
  ComposerBannerBody,
  ComposerBannerDescription,
  ComposerBannerDismiss,
  ComposerBannerIcon,
  ComposerBannerTitle,
} from "../tray/banner";

/**
 * The notice block that sits ABOVE the composer box.
 *
 * Composed parts rather than a component with a prop per feature — the shape
 * `vercel/ai-elements` uses throughout, and the reason is visible in the last
 * story: a caller wanting a second description line writes one, where the
 * predecessor's seven-prop surface would have needed an eighth.
 *
 * Every string here is passed IN. The package holds no dictionary entry for a
 * banner, because a banner's words are always about the host's own situation —
 * an allowance, a plan, a quota this package knows nothing about.
 *
 * Check across themes: the surface is deliberately neutral (`bg-muted/60`) and
 * only the ICON carries tone, so a warning must read as a warning without the
 * block turning red.
 */
const meta = {
  title: "Widgets/Chat/Composer/Banner",
  component: ComposerBanner,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ComposerBanner>;

export default meta;
type Story = StoryObj<typeof meta>;

const noop = () => undefined;

/**
 * The upgrade prompt at the SOFT threshold — the allowance is close, work is
 * still flowing.
 *
 * Dismissible, and that is the point of the pair: this one is about the future
 * and can be waved off.
 */
export const ApproachingLimit: Story = {
  args: {
    children: (
      <>
        <ComposerBannerIcon tone="upgrade">
          <Sparkles />
        </ComposerBannerIcon>
        <ComposerBannerBody>
          <ComposerBannerTitle>
            You&rsquo;re close to today&rsquo;s AI limit
          </ComposerBannerTitle>
          <ComposerBannerDescription>
            Upgrade to keep working without interruptions.
          </ComposerBannerDescription>
        </ComposerBannerBody>
        <ComposerBannerActions>
          <ComposerBannerAction onClick={noop}>Manage plan</ComposerBannerAction>
        </ComposerBannerActions>
        <ComposerBannerDismiss onDismiss={noop} label="Dismiss" />
      </>
    ),
  },
};

/**
 * At the wall — spent, and NOT dismissible.
 *
 * Hiding this would leave a product that has stopped answering with no stated
 * cause, which reads as broken rather than as limited. The action is filled
 * here and outlined above: before the wall this is an aside, at it the thing
 * the person came to do.
 */
export const Exhausted: Story = {
  args: {
    children: (
      <>
        <ComposerBannerIcon tone="upgrade">
          <Sparkles />
        </ComposerBannerIcon>
        <ComposerBannerBody>
          <ComposerBannerTitle>Today&rsquo;s AI limit is used up</ComposerBannerTitle>
          <ComposerBannerDescription>
            Resets at 3:00 (in 6 hours). Upgrade to keep going today.
          </ComposerBannerDescription>
        </ComposerBannerBody>
        <ComposerBannerActions>
          <ComposerBannerAction onClick={noop} variant="primary">
            Upgrade plan
          </ComposerBannerAction>
        </ComposerBannerActions>
      </>
    ),
  },
};

/** The warning tone. Only the icon changes — verify the surface stays calm. */
export const Warning: Story = {
  args: {
    children: (
      <>
        <ComposerBannerIcon tone="warning">
          <TriangleAlert />
        </ComposerBannerIcon>
        <ComposerBannerBody>
          <ComposerBannerTitle>You are offline</ComposerBannerTitle>
          <ComposerBannerDescription>
            Messages will be queued until it reconnects.
          </ComposerBannerDescription>
        </ComposerBannerBody>
      </>
    ),
  },
};

/**
 * Title only, no actions — the smallest honest banner.
 *
 * Included because a shape that only works fully-populated is a template, not
 * a component.
 */
export const TitleOnly: Story = {
  args: {
    children: (
      <>
        <ComposerBannerIcon>
          <Info />
        </ComposerBannerIcon>
        <ComposerBannerBody>
          <ComposerBannerTitle>Read-only session</ComposerBannerTitle>
        </ComposerBannerBody>
      </>
    ),
  },
};

/**
 * Long copy and two actions, in a narrow column.
 *
 * The layout test: `min-w-0` on the body must let the text truncate rather than
 * push the buttons off the row, and a long unbroken token must not widen the
 * banner past its container.
 */
export const LongCopyAndTwoActions: Story = {
  args: {
    className: "max-w-md",
    children: (
      <>
        <ComposerBannerIcon tone="upgrade">
          <Sparkles />
        </ComposerBannerIcon>
        <ComposerBannerBody>
          <ComposerBannerTitle>
            Your workspace plan renews on the first of next month
          </ComposerBannerTitle>
          <ComposerBannerDescription>
            Usage this period is higher than the included allowance, so the next
            invoice will differ from the last one.
          </ComposerBannerDescription>
          <ComposerBannerDescription>
            A second line, written by the caller — the reason this is composed
            rather than a `description` prop.
          </ComposerBannerDescription>
        </ComposerBannerBody>
        <ComposerBannerActions>
          <ComposerBannerAction onClick={noop}>Details</ComposerBannerAction>
          <ComposerBannerAction onClick={noop} variant="primary">
            Review
          </ComposerBannerAction>
        </ComposerBannerActions>
        <ComposerBannerDismiss onDismiss={noop} label="Dismiss" />
      </>
    ),
  },
};
