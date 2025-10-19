/**
 * Form Components Configuration
 */

import React from 'react';
import {
  Button,
  Input,
  Checkbox,
  Label,
  RadioGroup,
  RadioGroupItem,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
  Switch,
  Slider,
} from '@djangocfg/ui';
import type { ComponentConfig } from './types';

export const FORM_COMPONENTS: ComponentConfig[] = [
  {
    name: 'Button',
    category: 'forms',
    description: 'Interactive button with multiple variants and sizes',
    importPath: "import { Button } from '@djangocfg/ui';",
    example: `<Button variant="default">Click me</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>`,
    preview: (
      <div className="flex flex-wrap gap-3">
        <Button variant="default">Click me</Button>
        <Button variant="destructive">Delete</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button size="sm">Small</Button>
        <Button size="lg">Large</Button>
      </div>
    ),
  },
  {
    name: 'Input',
    category: 'forms',
    description: 'Text input field with validation support',
    importPath: "import { Input } from '@djangocfg/ui';",
    example: `<Input type="text" placeholder="Enter text..." />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" disabled />`,
    preview: (
      <div className="space-y-3 max-w-sm">
        <Input type="text" placeholder="Enter text..." />
        <Input type="email" placeholder="Email" />
        <Input type="password" placeholder="Password" disabled />
      </div>
    ),
  },
  {
    name: 'Checkbox',
    category: 'forms',
    description: 'Checkbox with label support',
    importPath: "import { Checkbox, Label } from '@djangocfg/ui';",
    example: `<div className="flex items-center gap-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Accept terms and conditions</Label>
</div>`,
    preview: (
      <div className="flex items-center gap-2">
        <Checkbox id="terms" />
        <Label htmlFor="terms">Accept terms and conditions</Label>
      </div>
    ),
  },
  {
    name: 'RadioGroup',
    category: 'forms',
    description: 'Radio button group for single selection',
    importPath: "import { RadioGroup, RadioGroupItem, Label } from '@djangocfg/ui';",
    example: `<RadioGroup defaultValue="option1">
  <div className="flex items-center gap-2">
    <RadioGroupItem value="option1" id="opt1" />
    <Label htmlFor="opt1">Option 1</Label>
  </div>
  <div className="flex items-center gap-2">
    <RadioGroupItem value="option2" id="opt2" />
    <Label htmlFor="opt2">Option 2</Label>
  </div>
</RadioGroup>`,
    preview: (
      <RadioGroup defaultValue="option1">
        <div className="flex items-center gap-2">
          <RadioGroupItem value="option1" id="opt1" />
          <Label htmlFor="opt1">Option 1</Label>
        </div>
        <div className="flex items-center gap-2">
          <RadioGroupItem value="option2" id="opt2" />
          <Label htmlFor="opt2">Option 2</Label>
        </div>
      </RadioGroup>
    ),
  },
  {
    name: 'Select',
    category: 'forms',
    description: 'Dropdown select component',
    importPath: "import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@djangocfg/ui';",
    example: `<Select>
  <SelectTrigger className="w-[200px]">
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
    <SelectItem value="2">Option 2</SelectItem>
    <SelectItem value="3">Option 3</SelectItem>
  </SelectContent>
</Select>`,
    preview: (
      <Select>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Select option" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Option 1</SelectItem>
          <SelectItem value="2">Option 2</SelectItem>
          <SelectItem value="3">Option 3</SelectItem>
        </SelectContent>
      </Select>
    ),
  },
  {
    name: 'Textarea',
    category: 'forms',
    description: 'Multi-line text input',
    importPath: "import { Textarea } from '@djangocfg/ui';",
    example: `<Textarea placeholder="Enter your message..." rows={4} />`,
    preview: (
      <Textarea placeholder="Enter your message..." rows={4} className="max-w-sm" />
    ),
  },
  {
    name: 'Switch',
    category: 'forms',
    description: 'Toggle switch component',
    importPath: "import { Switch, Label } from '@djangocfg/ui';",
    example: `<div className="flex items-center gap-2">
  <Switch id="notifications" />
  <Label htmlFor="notifications">Enable notifications</Label>
</div>`,
    preview: (
      <div className="flex items-center gap-2">
        <Switch id="notifications" />
        <Label htmlFor="notifications">Enable notifications</Label>
      </div>
    ),
  },
  {
    name: 'Slider',
    category: 'forms',
    description: 'Range slider input',
    importPath: "import { Slider } from '@djangocfg/ui';",
    example: `<Slider defaultValue={[50]} max={100} step={1} className="w-[200px]" />`,
    preview: (
      <Slider defaultValue={[50]} max={100} step={1} className="w-[200px]" />
    ),
  },
];
