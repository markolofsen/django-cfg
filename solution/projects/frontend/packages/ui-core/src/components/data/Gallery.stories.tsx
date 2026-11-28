import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { AlignCenter, AlignLeft, Bold, TrendingUp, Users } from 'lucide-react';
import {
  Avatar,
  AvatarFallback,
  AvatarGroup,
  Badge,
  BadgeOverflow,
  BalancedText,
  Calendar,
  Card,
  CardContent,
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  CircularProgressCombined,
  DatePicker,
  DateRangePicker,
  Progress,
  RelativeTimeCard,
  Stat,
  StatDescription,
  StatIndicator,
  StatLabel,
  StatTrend,
  StatValue,
  Status,
  StatusIndicator,
  StatusLabel,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Toggle,
  ToggleGroup,
  ToggleGroupItem,
  type DateRange,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Data/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every data-display component in `ui-core`, side by side. Pick by what the ' +
          'value *is*: **a person**, **a label on something**, **one number**, ' +
          '**a moment in time**, **many rows**, or **prose**. The last section holds ' +
          'the two controls that live here because they present state rather than ' +
          'collect it. Charts ship from the `@djangocfg/ui-core/chart` subpath and ' +
          'have their own page.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

const PEOPLE = ['AB', 'CD', 'EF', 'GH', 'IJ'];

const STACK = ['React', 'TypeScript', 'Tailwind', 'Django', 'Postgres', 'Redis', 'Docker'];

// ── Time ─────────────────────────────────────────────────────────────────────

const NOW = Date.now();

function PickDate() {
  const [date, setDate] = useState<Date | undefined>(new Date(NOW));
  return <DatePicker value={date} onChange={setDate} />;
}

function PickRange() {
  const [range, setRange] = useState<DateRange | undefined>({
    from: new Date(NOW),
    to: new Date(NOW + 6 * 24 * 60 * 60 * 1000),
  });
  return <DateRangePicker value={range} onChange={setRange} />;
}

function MonthGrid() {
  const [date, setDate] = useState<Date | undefined>(new Date(NOW));
  return (
    <Calendar
      mode="single"
      selected={date}
      onSelect={setDate}
      className="rounded-md border border-border"
    />
  );
}

// ── State-presenting controls ────────────────────────────────────────────────

function BoldToggle() {
  const [on, setOn] = useState(true);
  return (
    <Toggle pressed={on} onPressedChange={setOn} aria-label="Bold">
      <Bold className="h-4 w-4" />
    </Toggle>
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by what is being displayed rather than alphabetically, which files
 * `Progress` next to `RelativeTimeCard` and splits the three progress
 * components that actually compete with each other.
 */
export const AllData: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="People">
        <Gallery>
          <GalleryItem name="Avatar" hint="One person, image with initials fallback.">
            <Avatar>
              <AvatarFallback>AB</AvatarFallback>
            </Avatar>
          </GalleryItem>
          <GalleryItem name="AvatarGroup" hint="Several people, stacked with a +N.">
            <AvatarGroup max={3}>
              {PEOPLE.map((p) => (
                <Avatar key={p}>
                  <AvatarFallback>{p}</AvatarFallback>
                </Avatar>
              ))}
            </AvatarGroup>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Labels on a thing">
        <Gallery>
          <GalleryItem name="Badge" hint="Static tag or count.">
            <div className="flex flex-wrap gap-2">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
            </div>
          </GalleryItem>
          <GalleryItem name="BadgeOverflow" hint="Too many badges for the width.">
            <BadgeOverflow
              items={STACK}
              lineCount={1}
              renderBadge={(item) => <Badge variant="secondary">{item}</Badge>}
            />
          </GalleryItem>
          <GalleryItem name="Status" hint="Live state, with a pulsing dot.">
            <div className="flex flex-wrap gap-2">
              <Status variant="success">
                <StatusIndicator />
                <StatusLabel>Online</StatusLabel>
              </Status>
              <Status variant="error">
                <StatusIndicator />
                <StatusLabel>Failed</StatusLabel>
              </Status>
            </div>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="One number">
        <Gallery>
          <GalleryItem name="Stat" hint="Headline metric with label and trend.">
            <Stat>
              <StatLabel>Active users</StatLabel>
              <StatIndicator variant="icon" color="success">
                <Users />
              </StatIndicator>
              <StatValue>2,350</StatValue>
              <StatTrend trend="up">
                <TrendingUp />
                +12.5% this month
              </StatTrend>
              <StatDescription>Compared to last month</StatDescription>
            </Stat>
          </GalleryItem>
          <GalleryItem name="Progress" hint="Linear completion; fits inside a row.">
            <Progress value={65} />
          </GalleryItem>
          <GalleryItem name="CircularProgress" hint="Same, compact, with the number inside.">
            <CircularProgressCombined value={65} />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Time">
        <Gallery>
          <GalleryItem name="RelativeTimeCard" hint="Read-only “3 hours ago”, self-updating.">
            <RelativeTimeCard date={new Date(NOW - 3 * 60 * 60 * 1000)} />
          </GalleryItem>
          <GalleryItem name="DatePicker" hint="Pick one date from a popover.">
            <PickDate />
          </GalleryItem>
          <GalleryItem name="DateRangePicker" hint="Pick a from/to span.">
            <PickRange />
          </GalleryItem>
          <GalleryItem name="Calendar" hint="Always-open month grid; the two above wrap it.">
            <MonthGrid />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Collections">
        <Gallery min="24rem">
          <GalleryItem name="Table" hint="Rows and columns you can scan.">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell>Invoice #1</TableCell>
                  <TableCell>
                    <Badge variant="secondary">Paid</Badge>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Invoice #2</TableCell>
                  <TableCell>
                    <Badge variant="outline">Pending</Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </GalleryItem>
          <GalleryItem name="Carousel" hint="One item at a time, paged sideways.">
            <Carousel>
              <CarouselContent>
                {[1, 2, 3].map((n) => (
                  <CarouselItem key={n}>
                    <Card>
                      <CardContent className="flex aspect-[16/9] items-center justify-center text-3xl font-semibold">
                        {n}
                      </CardContent>
                    </Card>
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious />
              <CarouselNext />
            </Carousel>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Prose">
        <Gallery min="24rem">
          <GalleryItem name="BalancedText" hint="Even line lengths in a heading.">
            <BalancedText as="h3" maxWidth={360} className="text-xl font-semibold leading-tight">
              Deterministic line breaks that hold across every browser
            </BalancedText>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="State-presenting controls">
        <Gallery>
          <GalleryItem name="Toggle" hint="One independent on/off button.">
            <BoldToggle />
          </GalleryItem>
          <GalleryItem name="ToggleGroup" hint="Toggles sharing one value.">
            <ToggleGroup type="single" defaultValue="left" aria-label="Alignment">
              <ToggleGroupItem value="left" aria-label="Align left">
                <AlignLeft className="h-4 w-4" />
              </ToggleGroupItem>
              <ToggleGroupItem value="center" aria-label="Align center">
                <AlignCenter className="h-4 w-4" />
              </ToggleGroupItem>
            </ToggleGroup>
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};

/**
 * Every component that has an empty, zero or indeterminate state, in it.
 *
 * These are the states a real dashboard hits first — before any data loads —
 * and the ones individual stories almost never cover.
 */
export const EmptyStates: Story = {
  render: () => (
    <GalleryPage>
      <Gallery>
        <GalleryItem name="Avatar" hint="No image: initials only.">
          <Avatar>
            <AvatarFallback>?</AvatarFallback>
          </Avatar>
        </GalleryItem>
        <GalleryItem name="AvatarGroup" hint="One member, no overflow badge.">
          <AvatarGroup max={3}>
            <Avatar>
              <AvatarFallback>AB</AvatarFallback>
            </Avatar>
          </AvatarGroup>
        </GalleryItem>
        <GalleryItem name="BadgeOverflow" hint="Nothing to lay out.">
          <BadgeOverflow items={[]} renderBadge={(item: string) => <Badge>{item}</Badge>} />
        </GalleryItem>
        <GalleryItem name="Stat" hint="Zero still needs a shape.">
          <Stat>
            <StatLabel>Active users</StatLabel>
            <StatValue>0</StatValue>
            <StatDescription>No activity yet</StatDescription>
          </Stat>
        </GalleryItem>
        <GalleryItem name="Progress" hint="Nothing done yet.">
          <Progress value={0} />
        </GalleryItem>
        <GalleryItem name="CircularProgress" hint="No value: spins indeterminately.">
          <CircularProgressCombined />
        </GalleryItem>
        <GalleryItem name="DatePicker" hint="Unset: placeholder, not today.">
          <DatePicker placeholder="Pick a date" />
        </GalleryItem>
        <GalleryItem name="DateRangePicker" hint="Unset span.">
          <DateRangePicker placeholder="Pick a range" />
        </GalleryItem>
        <GalleryItem name="Table" hint="Header survives an empty body.">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell colSpan={2} className="text-muted-foreground text-center">
                  No records
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </GalleryItem>
        <GalleryItem name="Toggle" hint="Off.">
          <Toggle aria-label="Bold">
            <Bold className="h-4 w-4" />
          </Toggle>
        </GalleryItem>
        <GalleryItem name="ToggleGroup" hint="Nothing selected.">
          <ToggleGroup type="single" aria-label="Alignment">
            <ToggleGroupItem value="left" aria-label="Align left">
              <AlignLeft className="h-4 w-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="center" aria-label="Align center">
              <AlignCenter className="h-4 w-4" />
            </ToggleGroupItem>
          </ToggleGroup>
        </GalleryItem>
      </Gallery>
    </GalleryPage>
  ),
};
