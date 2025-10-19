'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';
import { profileLogger } from '../../../utils/logger';

import {
  Button,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
  Label,
  PhoneInput,
} from '@djangocfg/ui/components';
import { 
  useAccountsContext,
  PatchedUserProfileUpdateRequestSchema,
  type PatchedUserProfileUpdateRequest
} from '@djangocfg/api/cfg/contexts';
import { useAuth } from '../../../auth';

export const ProfileForm = () => {
  const { user } = useAuth();
  const accounts = useAccountsContext();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const form = useForm<PatchedUserProfileUpdateRequest>({
    resolver: zodResolver(PatchedUserProfileUpdateRequestSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      company: '',
      position: '',
      phone: '',
    },
  });

  // Load user data
  useEffect(() => {
    if (user) {
      form.reset({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        company: user.company || '',
        position: user.position || '',
        phone: user.phone || '',
      });
    }
  }, [user, form]);

  const handleSubmit = async (data: PatchedUserProfileUpdateRequest) => {
    setIsSaving(true);
    try {
      await accounts.partialUpdateProfile(data);
      toast.success('Profile updated successfully');
      setIsEditing(false);
    } catch (error: any) {
      profileLogger.error('Profile update error:', error);
      if (error?.response?.data) {
        const fieldErrors = error.response.data;
        Object.entries(fieldErrors).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof PatchedUserProfileUpdateRequest, {
              type: 'server',
              message: messages[0],
            });
          }
        });
        toast.error('Please fix the validation errors');
      } else {
        toast.error('Failed to update profile');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    form.clearErrors();
    if (user) {
      form.reset({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        company: user.company || '',
        position: user.position || '',
        phone: user.phone || '',
      });
    }
  };

  const onSubmit = form.handleSubmit(handleSubmit);

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={user?.email || ''} disabled className="bg-muted" />
          </div>

          <FormField
            control={form.control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First Name</FormLabel>
                <FormControl>
                  <Input {...field} disabled={!isEditing} placeholder="Enter first name" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Last Name</FormLabel>
                <FormControl>
                  <Input {...field} disabled={!isEditing} placeholder="Enter last name" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="company"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Company</FormLabel>
                <FormControl>
                  <Input {...field} disabled={!isEditing} placeholder="Enter company name" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="position"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Position</FormLabel>
                <FormControl>
                  <Input {...field} disabled={!isEditing} placeholder="Enter position" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="phone"
            render={({ field }) => (
              <FormItem className="md:col-span-2">
                <FormLabel>Phone</FormLabel>
                <FormControl>
                  <PhoneInput
                    value={field.value}
                    onChange={field.onChange}
                    disabled={!isEditing}
                    placeholder="Enter phone number"
                    defaultCountry="US"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4">
          {isEditing ? (
            <div className="flex items-center gap-2">
              <Button type="submit" disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
              <Button type="button" variant="outline" onClick={handleCancel}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button type="button" onClick={() => setIsEditing(true)}>
              Edit Profile
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
};

