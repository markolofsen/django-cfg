import type { Meta, StoryObj } from '@storybook/react-vite';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/Form',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'react-hook-form integration primitives. Combine `Form` (FormProvider), `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormDescription`, `FormMessage` to wire RHF state, accessibility ids and validation messages.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

// ---------- Basic ----------
const basicSchema = z.object({
  username: z.string().min(2, 'Must be at least 2 characters'),
});

function BasicForm() {
  const form = useForm<z.infer<typeof basicSchema>>({
    resolver: zodResolver(basicSchema),
    defaultValues: { username: '' },
  });
  const onSubmit = (values: z.infer<typeof basicSchema>) => {
     
    console.log('submit', values);
  };
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-80 space-y-4">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}

export const Basic: Story = { render: () => <BasicForm /> };

// ---------- WithValidation ----------
const validationSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

function ValidationForm() {
  const form = useForm<z.infer<typeof validationSchema>>({
    resolver: zodResolver(validationSchema),
    defaultValues: { email: '', password: '' },
    mode: 'onBlur',
  });
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(() => {})} className="w-80 space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="you@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" placeholder="••••••••" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Sign in</Button>
      </form>
    </Form>
  );
}

export const WithValidation: Story = { render: () => <ValidationForm /> };

// ---------- WithDescription ----------
const descSchema = z.object({
  bio: z.string().max(160, 'Keep it under 160 characters').optional(),
});

function DescriptionForm() {
  const form = useForm<z.infer<typeof descSchema>>({
    resolver: zodResolver(descSchema),
    defaultValues: { bio: '' },
  });
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(() => {})} className="w-80 space-y-4">
        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Input placeholder="Tell us a little about yourself" {...field} />
              </FormControl>
              <FormDescription>
                Shown on your public profile. Maximum 160 characters.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Save</Button>
      </form>
    </Form>
  );
}

export const WithDescription: Story = { render: () => <DescriptionForm /> };

// ---------- WithDefaults ----------
const defaultsSchema = z.object({
  firstName: z.string().min(1, 'Required'),
  lastName: z.string().min(1, 'Required'),
});

function DefaultsForm() {
  const form = useForm<z.infer<typeof defaultsSchema>>({
    resolver: zodResolver(defaultsSchema),
    defaultValues: { firstName: 'Ada', lastName: 'Lovelace' },
  });
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(() => {})} className="w-80 space-y-4">
        <FormField
          control={form.control}
          name="firstName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>First name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="lastName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Last name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Continue</Button>
      </form>
    </Form>
  );
}

export const WithDefaults: Story = { render: () => <DefaultsForm /> };
