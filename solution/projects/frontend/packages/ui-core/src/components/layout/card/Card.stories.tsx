import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
  Label,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Card',
  component: Card,
  tags: ['autodocs'],
} satisfies Meta<typeof Card>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Card className="w-80">
      <CardHeader>
        <CardTitle>djangocfg storybook</CardTitle>
        <CardDescription>
          Canonical playground for every workspace package.
        </CardDescription>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        Toggle the theme to see how every utility maps onto our token
        palette.
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        <Button variant="ghost">Cancel</Button>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  ),
};

export const LoginCard: Story = {
  render: () => (
    <Card className="w-80">
      <CardHeader>
        <CardTitle>Login</CardTitle>
        <CardDescription>Enter your credentials to continue.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="login-email">Email</Label>
          <Input id="login-email" type="email" placeholder="you@example.com" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="login-pass">Password</Label>
          <Input id="login-pass" type="password" placeholder="••••••••" />
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline">Cancel</Button>
        <Button>Login</Button>
      </CardFooter>
    </Card>
  ),
};

export const ProductCard: Story = {
  render: () => (
    <Card className="w-72 overflow-hidden">
      <div className="aspect-video bg-muted" />
      <CardHeader>
        <CardTitle>Product Name</CardTitle>
        <CardDescription>$99.99</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Brief description of the product with key features.
        </p>
      </CardContent>
      <CardFooter>
        <Button className="w-full">Add to Cart</Button>
      </CardFooter>
    </Card>
  ),
};

export const StatsCards: Story = {
  render: () => (
    <div className="grid w-[720px] grid-cols-3 gap-4">
      {[
        { d: 'Total Revenue', t: '$45,231.89', f: '+20.1% from last month' },
        { d: 'Subscriptions', t: '+2,350', f: '+180.1% from last month' },
        { d: 'Active Now', t: '+573', f: '+201 since last hour' },
      ].map((c) => (
        <Card key={c.d}>
          <CardHeader className="pb-2">
            <CardDescription>{c.d}</CardDescription>
            <CardTitle className="text-2xl">{c.t}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">{c.f}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  ),
};

export const SimpleCard: Story = {
  render: () => (
    <Card className="w-96 p-6">
      <p>A simple card with just content and padding.</p>
    </Card>
  ),
};

export const Grid: Story = {
  render: () => (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {['ui-core', 'ui-tools', 'layouts'].map((name) => (
        <Card key={name}>
          <CardHeader>
            <CardTitle>@djangocfg/{name}</CardTitle>
            <CardDescription>Package — see sidebar.</CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            One of the workspace packages indexed by this Storybook.
          </CardContent>
        </Card>
      ))}
    </div>
  ),
};
