'use client';

import { AlertCircle, CheckCircle2, Inbox, Info, Rocket, Shield, Zap } from 'lucide-react';
import { useState } from 'react';

import {
    Accordion, AccordionContent, AccordionItem, AccordionTrigger, Alert, AlertDescription,
    AlertTitle, Avatar, AvatarFallback, AvatarImage, Badge, Button, Card, CardContent,
    CardDescription, CardFooter, CardHeader, CardTitle, Checkbox, Dialog, DialogContent,
    DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, Empty, EmptyContent,
    EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle, Input, JsonTree, Label, Progress, Select,
    SelectContent, SelectItem, SelectTrigger, SelectValue, Separator, Skeleton, Slider, Spinner,
    Switch, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Tabs, TabsContent,
    TabsList, TabsTrigger, Textarea, Tooltip, TooltipContent, TooltipProvider, TooltipTrigger
} from '@djangocfg/ui-nextjs';

import type { Metadata } from 'next';
/**
 * UI Components Demo Page
 *
 * Showcases various @djangocfg/ui components
 */
export default function DemoPage() {
  const [progress, setProgress] = useState(45);
  const [switchValue, setSwitchValue] = useState(false);
  const [sliderValue, setSliderValue] = useState([50]);
  const [loading, setLoading] = useState(false);

  const sampleData = {
    user: {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      roles: ['admin', 'developer'],
      profile: {
        bio: 'Software engineer',
        location: 'San Francisco',
        interests: ['coding', 'music', 'travel'],
      },
    },
    settings: {
      theme: 'dark',
      notifications: true,
      language: 'en',
    },
  };

  const tableData = [
    { id: 1, name: 'Project Alpha', status: 'Active', progress: 75 },
    { id: 2, name: 'Project Beta', status: 'Pending', progress: 30 },
    { id: 3, name: 'Project Gamma', status: 'Completed', progress: 100 },
  ];

  return (
    <div className="container mx-auto py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">UI Components Demo</h1>
        <p className="text-muted-foreground">
          Showcase of @djangocfg/ui components - 100+ components available
        </p>
      </div>

      <Separator />

      {/* Tabs for Categories */}
      <Tabs defaultValue="forms" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="forms">Forms</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
          <TabsTrigger value="layout">Layout</TabsTrigger>
          <TabsTrigger value="data">Data Display</TabsTrigger>
          <TabsTrigger value="overlay">Overlay</TabsTrigger>
        </TabsList>

        {/* Forms Tab */}
        <TabsContent value="forms" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Buttons */}
            <Card>
              <CardHeader>
                <CardTitle>Buttons</CardTitle>
                <CardDescription>Various button variants and states</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                <Button variant="default">Default</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="destructive">Destructive</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="link">Link</Button>
                <Button loading>Loading</Button>
                <Button disabled>Disabled</Button>
              </CardContent>
            </Card>

            {/* Inputs */}
            <Card>
              <CardHeader>
                <CardTitle>Inputs</CardTitle>
                <CardDescription>Text inputs and textarea</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="Enter your email" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="message">Message</Label>
                  <Textarea id="message" placeholder="Type your message..." rows={3} />
                </div>
              </CardContent>
            </Card>

            {/* Select & Checkbox */}
            <Card>
              <CardHeader>
                <CardTitle>Select & Checkbox</CardTitle>
                <CardDescription>Selection components</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Choose option</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select option" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="option1">Option 1</SelectItem>
                      <SelectItem value="option2">Option 2</SelectItem>
                      <SelectItem value="option3">Option 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox id="terms" />
                  <Label htmlFor="terms">Accept terms and conditions</Label>
                </div>
              </CardContent>
            </Card>

            {/* Switch & Slider */}
            <Card>
              <CardHeader>
                <CardTitle>Switch & Slider</CardTitle>
                <CardDescription>Toggle and range inputs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center gap-4">
                  <Switch
                    checked={switchValue}
                    onCheckedChange={setSwitchValue}
                    id="notifications"
                  />
                  <Label htmlFor="notifications">
                    Enable notifications: {switchValue ? 'On' : 'Off'}
                  </Label>
                </div>
                <div className="space-y-2">
                  <Label>Volume: {sliderValue[0]}%</Label>
                  <Slider
                    value={sliderValue}
                    onValueChange={setSliderValue}
                    max={100}
                    step={1}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Feedback Tab */}
        <TabsContent value="feedback" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Alerts */}
            <Card>
              <CardHeader>
                <CardTitle>Alerts</CardTitle>
                <CardDescription>Information and warning messages</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>Info</AlertTitle>
                  <AlertDescription>
                    This is an informational message.
                  </AlertDescription>
                </Alert>
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>
                    Something went wrong. Please try again.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>

            {/* Badges */}
            <Card>
              <CardHeader>
                <CardTitle>Badges</CardTitle>
                <CardDescription>Status indicators</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                <Badge>Default</Badge>
                <Badge variant="secondary">Secondary</Badge>
                <Badge variant="destructive">Destructive</Badge>
                <Badge variant="outline">Outline</Badge>
              </CardContent>
            </Card>

            {/* Progress */}
            <Card>
              <CardHeader>
                <CardTitle>Progress</CardTitle>
                <CardDescription>Progress indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} />
                </div>
                <div className="flex gap-4 items-center">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setProgress(Math.max(0, progress - 10))}
                  >
                    -10%
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setProgress(Math.min(100, progress + 10))}
                  >
                    +10%
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Spinner & Loading */}
            <Card>
              <CardHeader>
                <CardTitle>Loading States</CardTitle>
                <CardDescription>Spinners and skeletons</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <Spinner />
                  <Spinner className="size-6" />
                  <Spinner className="size-8" />
                </div>
                <Separator />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[250px]" />
                  <Skeleton className="h-4 w-[200px]" />
                  <Skeleton className="h-4 w-[150px]" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Empty State */}
          <Card>
            <CardHeader>
              <CardTitle>Empty State</CardTitle>
              <CardDescription>When there's no data</CardDescription>
            </CardHeader>
            <CardContent>
              <Empty>
                <EmptyHeader>
                  <EmptyMedia variant="icon">
                    <Inbox className="size-6" />
                  </EmptyMedia>
                  <EmptyTitle>No messages</EmptyTitle>
                  <EmptyDescription>
                    You don't have any messages yet. Start a conversation!
                  </EmptyDescription>
                </EmptyHeader>
                <EmptyContent>
                  <Button>Compose Message</Button>
                </EmptyContent>
              </Empty>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Layout Tab */}
        <TabsContent value="layout" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Cards */}
            <Card>
              <CardHeader>
                <CardTitle>Card Component</CardTitle>
                <CardDescription>Container for content</CardDescription>
              </CardHeader>
              <CardContent>
                <p>Cards can contain any content including text, images, and actions.</p>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="ghost">Cancel</Button>
                <Button>Save</Button>
              </CardFooter>
            </Card>

            {/* Avatar */}
            <Card>
              <CardHeader>
                <CardTitle>Avatars</CardTitle>
                <CardDescription>User profile images</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center gap-4">
                <Avatar>
                  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
                  <AvatarFallback>CN</AvatarFallback>
                </Avatar>
                <Avatar>
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <Avatar>
                  <AvatarFallback>AB</AvatarFallback>
                </Avatar>
              </CardContent>
            </Card>

            {/* Accordion */}
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Accordion</CardTitle>
                <CardDescription>Expandable sections</CardDescription>
              </CardHeader>
              <CardContent>
                <Accordion type="single" collapsible className="w-full">
                  <AccordionItem value="item-1">
                    <AccordionTrigger>
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4" />
                        What is this demo?
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      This is a comprehensive demo page showcasing @djangocfg/ui components.
                      It includes forms, feedback, layout, data display, and overlay components.
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="item-2">
                    <AccordionTrigger>
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        Is it production ready?
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      Yes! All components are built with accessibility, performance, and
                      customization in mind. They follow best practices and are type-safe.
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="item-3">
                    <AccordionTrigger>
                      <div className="flex items-center gap-2">
                        <Rocket className="h-4 w-4" />
                        How many components?
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      Over 100+ components including forms, layouts, navigation, overlays,
                      feedback, data display, developer tools, and pre-built blocks.
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Data Display Tab */}
        <TabsContent value="data" className="space-y-6 mt-6">
          {/* Table */}
          <Card>
            <CardHeader>
              <CardTitle>Table</CardTitle>
              <CardDescription>Data table with rows and columns</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableData.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>{row.id}</TableCell>
                      <TableCell>{row.name}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            row.status === 'Active'
                              ? 'default'
                              : row.status === 'Completed'
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          {row.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={row.progress} className="w-20" />
                          <span className="text-sm">{row.progress}%</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* JSON Tree */}
          <Card>
            <CardHeader>
              <CardTitle>JSON Tree</CardTitle>
              <CardDescription>Interactive JSON viewer</CardDescription>
            </CardHeader>
            <CardContent>
              <JsonTree
                title="Sample Data"
                data={sampleData}
                config={{
                  maxAutoExpandDepth: 2,
                  showCollectionInfo: true,
                  showExpandControls: true,
                  showActionButtons: true,
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Overlay Tab */}
        <TabsContent value="overlay" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Dialog */}
            <Card>
              <CardHeader>
                <CardTitle>Dialog</CardTitle>
                <CardDescription>Modal dialog overlay</CardDescription>
              </CardHeader>
              <CardContent>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button>Open Dialog</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Dialog Title</DialogTitle>
                      <DialogDescription>
                        This is a modal dialog. You can put any content here.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                      <p>Dialog content goes here. You can include forms, text, or any other components.</p>
                    </div>
                    <DialogFooter>
                      <Button variant="outline">Cancel</Button>
                      <Button>Confirm</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>

            {/* Tooltip */}
            <Card>
              <CardHeader>
                <CardTitle>Tooltip</CardTitle>
                <CardDescription>Hover for more info</CardDescription>
              </CardHeader>
              <CardContent className="flex gap-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="outline">Hover me</Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>This is a helpful tooltip!</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="outline">
                        <Info className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>More information available</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
