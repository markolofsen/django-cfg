/**
 * CommandsTab Component
 *
 * Displays Django management commands:
 * - Commands summary with statistics
 * - Paginated commands list
 * - Command categorization (Core/Custom/Third Party)
 * - Search and filter capabilities
 */

'use client';

import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Badge,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Button,
  ScrollArea,
} from '@djangocfg/ui';
import { Terminal, Package, Filter, Play } from 'lucide-react';
import { useDashboardCommandsContext } from '@/contexts/dashboard';
import { CommandExecutionDialog } from '../components/dialogs';

export function CommandsTab() {
  const {
    commands,
    isLoadingCommands,
    summary,
    isLoadingSummary,
  } = useDashboardCommandsContext();

  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');

  // Command execution dialog state
  const [executionDialogOpen, setExecutionDialogOpen] = useState(false);
  const [selectedCommand, setSelectedCommand] = useState<{ name: string; args: string[] } | null>(null);

  const handleExecuteCommand = (commandName: string) => {
    setSelectedCommand({ name: commandName, args: [] });
    setExecutionDialogOpen(true);
  };

  // Filter commands based on search and category
  const filteredCommands = React.useMemo(() => {
    if (!commands || !Array.isArray(commands)) return [];

    return commands.filter((cmd: any) => {
      const matchesSearch = !searchQuery ||
        cmd.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cmd.help.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = filterCategory === 'all' ||
        (filterCategory === 'core' && cmd.is_core) ||
        (filterCategory === 'custom' && cmd.is_custom) ||
        (filterCategory === 'third-party' && !cmd.is_core && !cmd.is_custom);

      return matchesSearch && matchesCategory;
    });
  }, [commands, searchQuery, filterCategory]);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        {isLoadingSummary ? (
          <>
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-16" />
                </CardHeader>
              </Card>
            ))}
          </>
        ) : summary ? (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Commands
                </CardTitle>
                <div className="text-3xl font-bold">{summary.total_commands}</div>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Core Commands
                </CardTitle>
                <div className="text-3xl font-bold">{summary.core_commands}</div>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Custom Commands
                </CardTitle>
                <div className="text-3xl font-bold">{summary.custom_commands}</div>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Categories
                </CardTitle>
                <div className="text-3xl font-bold">{summary.categories?.length || 0}</div>
              </CardHeader>
            </Card>
          </>
        ) : null}
      </div>

      {/* Commands List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Terminal className="h-5 w-5" />
                Django Management Commands
              </CardTitle>
              <CardDescription>
                All available management commands
              </CardDescription>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 mt-4">
            <div className="flex-1">
              <Input
                placeholder="Search commands..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="max-w-sm"
              />
            </div>
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Commands</SelectItem>
                <SelectItem value="core">Core Only</SelectItem>
                <SelectItem value="custom">Custom Only</SelectItem>
                <SelectItem value="third-party">Third Party Only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent>
          {isLoadingCommands ? (
            <div className="space-y-2">
              {Array.from({ length: 10 }).map((_, i) => (
                <Skeleton key={i} className="w-full h-16" />
              ))}
            </div>
          ) : filteredCommands.length > 0 ? (
            <>
              <ScrollArea className="h-[70vh]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Command</TableHead>
                      <TableHead>App</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead className="max-w-md">Help</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCommands.map((cmd: any) => (
                      <TableRow key={`${cmd.app}-${cmd.name}`}>
                        <TableCell>
                          <code className="relative rounded bg-muted px-2 py-1 font-mono text-sm">
                            {cmd.name}
                          </code>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            <Package className="h-3 w-3 mr-1" />
                            {cmd.app}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {cmd.is_core && (
                              <Badge variant="default">Core</Badge>
                            )}
                            {cmd.is_custom && (
                              <Badge variant="secondary">Custom</Badge>
                            )}
                            {!cmd.is_core && !cmd.is_custom && (
                              <Badge variant="outline">Third Party</Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="max-w-md text-sm text-muted-foreground truncate">
                          {cmd.help || 'No description available'}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleExecuteCommand(cmd.name)}
                            className="gap-1.5"
                          >
                            <Play className="h-3.5 w-3.5" />
                            Execute
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>

              {/* Commands count */}
              {commands && commands.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-muted-foreground">
                    Showing {filteredCommands.length} of {commands.length} commands
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <Filter className="h-12 w-12 mx-auto text-muted-foreground/50" />
              <p className="mt-2 text-muted-foreground">
                No commands found matching your filters
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Command Execution Dialog */}
      <CommandExecutionDialog
        open={executionDialogOpen}
        onOpenChange={setExecutionDialogOpen}
        commandName={selectedCommand?.name || ''}
        commandArgs={selectedCommand?.args || []}
      />
    </div>
  );
}
