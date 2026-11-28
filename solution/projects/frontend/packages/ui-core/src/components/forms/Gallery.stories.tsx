import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Bell, Mail, Search, Settings2 } from 'lucide-react';
import {
  Button,
  ButtonGroup,
  ButtonGroupSeparator,
  Checkbox,
  CheckboxGroup,
  CheckboxGroupItem,
  CheckboxGroupList,
  DateField,
  DateTimeField,
  DownloadButton,
  Editable,
  EditableInput,
  EditablePreview,
  Field,
  FieldDescription,
  FieldLabel,
  Input,
  InputAffix,
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
  Label,
  MaskInput,
  MoneyField,
  OTPInput,
  PhoneInput,
  PopoverActionButton,
  RadioGroup,
  RadioGroupItem,
  SegmentedInput,
  SettingRow,
  SettingsBlock,
  Slider,
  Switch,
  TagsInput,
  TagsInputInput,
  TagsInputItem,
  TagsInputItemDelete,
  TagsInputItemText,
  Textarea,
  TimeField,
  TimePicker,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Forms/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every form control in `ui-core`, side by side. Pick by the shape of the ' +
          'answer you are collecting: **free text**, **a constrained string** ' +
          '(phone, money, code, date), **a choice**, **an on/off**, or the ' +
          '**wrappers** that give any of them a label and an error slot. ' +
          'Selects live on their own page — see *UI Core/Select/Gallery*.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

// ── Free text ────────────────────────────────────────────────────────────────

function EditableText() {
  const [value, setValue] = useState('Click to edit');
  return (
    <Editable value={value} onValueChange={setValue}>
      <EditablePreview />
      <EditableInput />
    </Editable>
  );
}

function Tags() {
  const [value, setValue] = useState<string[]>(['react', 'django']);
  return (
    <TagsInput value={value} onChange={setValue}>
      {value.map((tag) => (
        <TagsInputItem key={tag} value={tag}>
          <TagsInputItemText />
          <TagsInputItemDelete />
        </TagsInputItem>
      ))}
      <TagsInputInput placeholder="Add tag…" />
    </TagsInput>
  );
}

// ── Constrained strings ──────────────────────────────────────────────────────

function Money() {
  const [minorUnits, setMinorUnits] = useState(1999);
  return <MoneyField value={minorUnits / 100} onValueChange={setMinorUnits} currency="USD" />;
}

function Masked() {
  const [value, setValue] = useState('');
  return <MaskInput mask="(000) 000-0000" value={value} onChange={setValue} />;
}

function Phone() {
  const [value, setValue] = useState<string | undefined>();
  return <PhoneInput value={value} onChange={setValue} defaultCountry="US" />;
}

function Segmented() {
  const [value, setValue] = useState('');
  return <SegmentedInput length={6} value={value} onChange={setValue} />;
}

function Otp() {
  const [value, setValue] = useState('');
  return <OTPInput length={6} value={value} onChange={setValue} />;
}

function Date_() {
  const [value, setValue] = useState('2026-09-08');
  return <DateField value={value} onChange={setValue} aria-label="Date" />;
}

function Time() {
  const [value, setValue] = useState('09:30');
  return <TimeField value={value} onChange={setValue} aria-label="Time" />;
}

function DateTime() {
  const [value, setValue] = useState('2026-09-08T09:30');
  return <DateTimeField value={value} onChange={setValue} aria-label="Date and time" />;
}

function LegacyTime() {
  const [value, setValue] = useState('09:30');
  return <TimePicker value={value} onChange={setValue} />;
}

// ── Choice ───────────────────────────────────────────────────────────────────

function Checks() {
  const [value, setValue] = useState<string[]>(['react']);
  return (
    <CheckboxGroup value={value} onValueChange={setValue}>
      <CheckboxGroupList>
        <CheckboxGroupItem value="react">React</CheckboxGroupItem>
        <CheckboxGroupItem value="vue">Vue</CheckboxGroupItem>
      </CheckboxGroupList>
    </CheckboxGroup>
  );
}

function Radios() {
  const [value, setValue] = useState('daily');
  return (
    <RadioGroup value={value} onValueChange={setValue}>
      <div className="flex items-center gap-2">
        <RadioGroupItem value="daily" id="gallery-daily" />
        <Label htmlFor="gallery-daily">Daily</Label>
      </div>
      <div className="flex items-center gap-2">
        <RadioGroupItem value="weekly" id="gallery-weekly" />
        <Label htmlFor="gallery-weekly">Weekly</Label>
      </div>
    </RadioGroup>
  );
}

function Range() {
  const [value, setValue] = useState([40]);
  return <Slider value={value} onValueChange={setValue} max={100} step={1} />;
}

// ── Toggles ──────────────────────────────────────────────────────────────────

function SingleCheckbox() {
  const [checked, setChecked] = useState(true);
  return (
    <div className="flex items-center gap-2">
      <Checkbox
        id="gallery-terms"
        checked={checked}
        onCheckedChange={(v) => setChecked(v === true)}
      />
      <Label htmlFor="gallery-terms">Accept terms</Label>
    </div>
  );
}

function SingleSwitch() {
  const [checked, setChecked] = useState(true);
  return (
    <div className="flex items-center gap-2">
      <Switch id="gallery-notify" checked={checked} onCheckedChange={setChecked} />
      <Label htmlFor="gallery-notify">Notifications</Label>
    </div>
  );
}

function Setting() {
  const [checked, setChecked] = useState(true);
  return (
    <SettingRow
      label="Email digest"
      description="Once a week"
      toggle
      checked={checked}
      onToggle={setChecked}
    />
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by the shape of the value being collected rather than alphabetically,
 * which would file `MaskInput` next to `MoneyField` for no reason and separate
 * `Checkbox` from `Switch`, the two that actually compete.
 */
export const AllForms: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Free text">
        <Gallery>
          <GalleryItem name="Input" hint="One line of anything.">
            <Input placeholder="Full name" />
          </GalleryItem>
          <GalleryItem name="Textarea" hint="Several lines; grows on demand.">
            <Textarea placeholder="Notes…" />
          </GalleryItem>
          <GalleryItem name="InputAffix" hint="Input with static prefix or suffix.">
            <InputAffix prefix="https://" suffix=".com" placeholder="djangocfg" />
          </GalleryItem>
          <GalleryItem name="InputGroup" hint="Input plus icons or inline buttons.">
            <InputGroup>
              <InputGroupAddon>
                <Search className="h-4 w-4" />
              </InputGroupAddon>
              <InputGroupInput placeholder="Search…" />
            </InputGroup>
          </GalleryItem>
          <GalleryItem name="Editable" hint="Reads as text until clicked.">
            <EditableText />
          </GalleryItem>
          <GalleryItem name="TagsInput" hint="Many short strings as chips.">
            <Tags />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Constrained strings">
        <Gallery>
          <GalleryItem name="MoneyField" hint="Amount in, minor units out.">
            <Money />
          </GalleryItem>
          <GalleryItem name="MaskInput" hint="Any fixed pattern you can spell.">
            <Masked />
          </GalleryItem>
          <GalleryItem name="PhoneInput" hint="Country picker plus E.164 output.">
            <Phone />
          </GalleryItem>
          <GalleryItem name="SegmentedInput" hint="Fixed-length code, one box per char.">
            <Segmented />
          </GalleryItem>
          <GalleryItem name="OTPInput" hint="SegmentedInput plus validation and auto-submit.">
            <Otp />
          </GalleryItem>
          <GalleryItem name="DateField" hint="Typeable date, optional calendar popover.">
            <Date_ />
          </GalleryItem>
          <GalleryItem name="TimeField" hint="Typeable time of day.">
            <Time />
          </GalleryItem>
          <GalleryItem name="DateTimeField" hint="Both at once, one value.">
            <DateTime />
          </GalleryItem>
          <GalleryItem name="TimePicker" hint="Click-only legacy; prefer TimeField.">
            <LegacyTime />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Choice">
        <Gallery>
          <GalleryItem name="CheckboxGroup" hint="Several options, any number chosen.">
            <Checks />
          </GalleryItem>
          <GalleryItem name="RadioGroup" hint="Several options, exactly one.">
            <Radios />
          </GalleryItem>
          <GalleryItem name="Slider" hint="A number on a continuous range.">
            <Range />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="On / off">
        <Gallery>
          <GalleryItem name="Checkbox" hint="Opt-in that applies on submit.">
            <SingleCheckbox />
          </GalleryItem>
          <GalleryItem name="Switch" hint="Setting that applies immediately.">
            <SingleSwitch />
          </GalleryItem>
          <GalleryItem name="SettingRow" hint="Labelled row for a settings screen.">
            <Setting />
          </GalleryItem>
          <GalleryItem name="SettingsBlock" hint="Groups SettingRows under a title.">
            <SettingsBlock title="Preferences">
              <SettingRow label="Sound" toggle checked onToggle={() => {}} />
              <SettingRow label="Vibrate" toggle onToggle={() => {}} />
            </SettingsBlock>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Actions">
        <Gallery>
          <GalleryItem name="Button" hint="The default action trigger.">
            <Button>Save changes</Button>
          </GalleryItem>
          <GalleryItem name="ButtonGroup" hint="Related actions welded together.">
            <ButtonGroup>
              <Button variant="outline">Copy</Button>
              <ButtonGroupSeparator />
              <Button variant="outline">Paste</Button>
            </ButtonGroup>
          </GalleryItem>
          <GalleryItem name="DownloadButton" hint="Authenticated fetch with progress states.">
            <DownloadButton url="/example.csv" filename="example.csv">
              Export CSV
            </DownloadButton>
          </GalleryItem>
          <GalleryItem name="PopoverActionButton" hint="Row-shaped action inside a popover.">
            <div className="w-full max-w-[14rem] rounded-md border p-1">
              <PopoverActionButton icon={<Mail className="h-4 w-4" />}>
                Send email
              </PopoverActionButton>
              <PopoverActionButton icon={<Settings2 className="h-4 w-4" />}>
                Settings
              </PopoverActionButton>
            </div>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Wrappers">
        <Gallery>
          <GalleryItem name="Label" hint="Bare label bound to one control.">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="gallery-email">Email</Label>
              <Input id="gallery-email" type="email" placeholder="you@example.com" />
            </div>
          </GalleryItem>
          <GalleryItem name="Field" hint="Label, description and error in one.">
            <Field>
              <FieldLabel htmlFor="gallery-alerts">Alerts</FieldLabel>
              <Input id="gallery-alerts" placeholder="Threshold" />
              <FieldDescription>Notify above this value.</FieldDescription>
            </Field>
          </GalleryItem>
          <GalleryItem name="Field" hint="Horizontal, for toggle rows.">
            <Field orientation="horizontal">
              <Bell className="text-muted-foreground h-4 w-4" />
              <FieldLabel htmlFor="gallery-push">Push alerts</FieldLabel>
              <Switch id="gallery-push" defaultChecked />
            </Field>
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};

/**
 * The same controls, disabled.
 *
 * A disabled control is the state most likely to be wrong and least likely to
 * be checked — it is off the happy path in every individual story.
 */
export const DisabledStates: Story = {
  render: () => (
    <GalleryPage>
      <Gallery>
        <GalleryItem name="Input">
          <Input placeholder="Disabled" disabled />
        </GalleryItem>
        <GalleryItem name="Textarea">
          <Textarea placeholder="Disabled" disabled />
        </GalleryItem>
        <GalleryItem name="InputAffix">
          <InputAffix prefix="https://" placeholder="Disabled" disabled />
        </GalleryItem>
        <GalleryItem name="Editable">
          <Editable defaultValue="Disabled" disabled>
            <EditablePreview />
            <EditableInput />
          </Editable>
        </GalleryItem>
        <GalleryItem name="MoneyField">
          <MoneyField defaultValue={19.99} currency="USD" disabled />
        </GalleryItem>
        <GalleryItem name="MaskInput">
          <MaskInput mask="(000) 000-0000" disabled />
        </GalleryItem>
        <GalleryItem name="PhoneInput">
          <PhoneInput defaultCountry="US" disabled />
        </GalleryItem>
        <GalleryItem name="SegmentedInput">
          <SegmentedInput length={4} disabled />
        </GalleryItem>
        <GalleryItem name="OTPInput">
          <OTPInput length={4} disabled />
        </GalleryItem>
        <GalleryItem name="DateField">
          <DateField defaultValue="2026-09-08" disabled aria-label="Date" />
        </GalleryItem>
        <GalleryItem name="TimeField">
          <TimeField defaultValue="09:30" disabled aria-label="Time" />
        </GalleryItem>
        <GalleryItem name="TimePicker">
          <TimePicker defaultValue="09:30" disabled />
        </GalleryItem>
        <GalleryItem name="CheckboxGroup">
          <CheckboxGroup defaultValue={['react']} disabled>
            <CheckboxGroupList>
              <CheckboxGroupItem value="react">React</CheckboxGroupItem>
              <CheckboxGroupItem value="vue">Vue</CheckboxGroupItem>
            </CheckboxGroupList>
          </CheckboxGroup>
        </GalleryItem>
        <GalleryItem name="RadioGroup">
          <RadioGroup defaultValue="daily" disabled>
            <div className="flex items-center gap-2">
              <RadioGroupItem value="daily" id="gallery-daily-off" />
              <Label htmlFor="gallery-daily-off">Daily</Label>
            </div>
          </RadioGroup>
        </GalleryItem>
        <GalleryItem name="Slider">
          <Slider defaultValue={[40]} max={100} disabled />
        </GalleryItem>
        <GalleryItem name="Checkbox">
          <Checkbox defaultChecked disabled />
        </GalleryItem>
        <GalleryItem name="Switch">
          <Switch defaultChecked disabled />
        </GalleryItem>
        <GalleryItem name="SettingRow">
          <SettingRow label="Email digest" toggle checked onToggle={() => {}} disabled />
        </GalleryItem>
        <GalleryItem name="Button">
          <Button disabled>Save changes</Button>
        </GalleryItem>
        <GalleryItem name="DownloadButton">
          <DownloadButton url="/example.csv" disabled>
            Export CSV
          </DownloadButton>
        </GalleryItem>
      </Gallery>
    </GalleryPage>
  ),
};
