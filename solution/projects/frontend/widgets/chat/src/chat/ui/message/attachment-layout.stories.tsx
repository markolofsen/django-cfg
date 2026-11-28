import type { Meta, StoryObj } from "@storybook/react-vite";

import type { ChatMessage, MessagePart } from "../../core/conversation/parts";
import { ChatMessageFrame, MessageProse } from "./message";
import { MessageContent } from "../../primitives/parts/message";
import { PartRegistryProvider, type PartRegistry } from "../../primitives/parts/part-registry";
import { AttachmentRenderer } from "../renderers/attachment";

const renderers: PartRegistry = {
  text: ({ part }) => (part.type === "text" ? <p className="m-0 whitespace-pre-wrap">{part.text}</p> : null),
  attachment: AttachmentRenderer,
};

/**
 * How attachments sit in a message: one picture, a grid by count, a file between pictures, expired, with text.
 * Pictures are inline SVG data URLs so the stories need no network.
 */
const tile = (n: number, w = 400, h = 300) =>
  `data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect width="100%" height="100%" fill="hsl(${n * 67},55%,62%)"/><text x="50%" y="50%" font-size="48" fill="white" text-anchor="middle" dominant-baseline="middle">${n}</text></svg>`,
  )}`;

const image = (n: number, w?: number, h?: number): MessagePart => ({
  id: `p${n}`,
  type: "attachment",
  attachment: { id: `a${n}`, name: `photo-${n}.png`, mime: "image/png", size: 1000, kind: "image", url: tile(n, w, h) },
});
const file = (n: number): MessagePart => ({
  id: `f${n}`,
  type: "attachment",
  attachment: { id: `fa${n}`, name: `report-${n}.pdf`, mime: "application/pdf", size: 120000, kind: "document", url: "/media/x.pdf" },
});
const text = (value: string): MessagePart => ({ id: "t", type: "text", text: value } as MessagePart);

const message = (parts: MessagePart[], role: ChatMessage["role"] = "user"): ChatMessage => ({
  id: "m",
  role,
  parts,
  status: { state: "complete" },
  createdAt: 0,
});

const meta = {
  title: "Widgets/Chat/Attachment layout",
  component: ChatMessageFrame,
  args: { message: message([]), children: null },
  decorators: [
    (Story) => (
      <PartRegistryProvider renderers={renderers}>
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-2 bg-background p-6">
          <Story />
        </div>
      </PartRegistryProvider>
    ),
  ],
} satisfies Meta<typeof ChatMessageFrame>;
export default meta;
type Story = StoryObj<typeof meta>;

const show = (parts: MessagePart[]): Story => ({
  render: () => {
    const m = message(parts);
    return (
      <ChatMessageFrame message={m}>
        <MessageContent message={m} />
      </ChatMessageFrame>
    );
  },
});

export const One: Story = show([text("что тут?"), image(1)]);
export const Tall: Story = show([image(2, 300, 900)]);
export const Two: Story = show([image(1), image(2)]);
export const Three: Story = show([text("три фото"), image(1), image(2), image(3)]);
export const Four: Story = show([image(1), image(2), image(3), image(4)]);
export const SixWithMore: Story = show([image(1), image(2), image(3), image(4), image(5), image(6)]);
export const FileBetween: Story = show([image(1), image(2), file(1), image(3)]);
export const LongTextUnderMedia: Story = show([
  image(1),
  text("Длинный текст под картинкой. ".repeat(40)),
]);

export const Unused: Story = { render: () => <MessageProse>unused</MessageProse> };
