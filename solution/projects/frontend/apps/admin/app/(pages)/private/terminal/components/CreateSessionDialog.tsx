'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Button,
  Input,
  Label,
} from '@djangocfg/ui-nextjs';
import { Plus } from 'lucide-react';
import type { TerminalSessionCreateRequest } from '@/api/generated/terminal/_utils/schemas/TerminalSessionCreateRequest.schema';

interface CreateSessionDialogProps {
  onSubmit: (data: TerminalSessionCreateRequest) => Promise<void>;
}

export function CreateSessionDialog({ onSubmit }: CreateSessionDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState('');
  const [shell, setShell] = useState('');
  const [workingDirectory, setWorkingDirectory] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit({
        name: name || undefined,
        shell: shell || undefined,
        working_directory: workingDirectory || undefined,
      });
      setOpen(false);
      setName('');
      setShell('');
      setWorkingDirectory('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Session
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Terminal Session</DialogTitle>
            <DialogDescription>
              Start a new terminal session. All fields are optional.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Session Name</Label>
              <Input
                id="name"
                placeholder="My Session"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="shell">Shell</Label>
              <Input
                id="shell"
                placeholder="/bin/bash"
                value={shell}
                onChange={(e) => setShell(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="workingDirectory">Working Directory</Label>
              <Input
                id="workingDirectory"
                placeholder="/home/user"
                value={workingDirectory}
                onChange={(e) => setWorkingDirectory(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Session'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
