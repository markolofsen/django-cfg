/**
 * ZonesTab Component
 *
 * Displays OpenAPI zones/groups:
 * - Zones summary with statistics
 * - Paginated zones list
 * - Zone details (apps, endpoints, status)
 * - Links to schema and API endpoints
 */

'use client';

import React from 'react';
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
  Button,
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@djangocfg/ui';
import { Globe, FileCode, Link, Package } from 'lucide-react';
import { useDashboardZonesContext } from '@/contexts/dashboard';

export function ZonesTab() {
  const {
    zones,
    isLoadingZones,

    summary,
    isLoadingSummary,
  } = useDashboardZonesContext();

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        {isLoadingSummary ? (
          <>
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-16" />
                </CardHeader>
              </Card>
            ))}
          </>
        ) : summary?.summary ? (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Zones
                </CardTitle>
                <div className="text-3xl font-bold">{summary.summary.total_zones}</div>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Apps
                </CardTitle>
                <div className="text-3xl font-bold">{summary.summary.total_apps}</div>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Endpoints
                </CardTitle>
                <div className="text-3xl font-bold">{summary.summary.total_endpoints}</div>
              </CardHeader>
            </Card>
          </>
        ) : null}
      </div>

      {/* Zones List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            API Zones
          </CardTitle>
          <CardDescription>
            OpenAPI zones with their configuration and endpoints
          </CardDescription>
        </CardHeader>

        <CardContent>
          {isLoadingZones ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="w-full h-24" />
              ))}
            </div>
          ) : zones && Array.isArray(zones) && zones.length > 0 ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Zone</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead className="text-center">Apps</TableHead>
                    <TableHead className="text-center">Endpoints</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {zones.map((zone: any) => (
                    <TableRow key={zone.name}>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="font-medium">{zone.title}</div>
                          <code className="text-xs text-muted-foreground">{zone.name}</code>
                        </div>
                      </TableCell>
                      <TableCell className="max-w-md">
                        <p className="text-sm text-muted-foreground truncate">
                          {zone.description}
                        </p>
                        {zone.apps && zone.apps.length > 0 && (
                          <div className="flex gap-1 mt-2 flex-wrap">
                            {zone.apps.slice(0, 3).map((app: string) => (
                              <Badge key={app} variant="outline" className="text-xs">
                                <Package className="h-3 w-3 mr-1" />
                                {app}
                              </Badge>
                            ))}
                            {zone.apps.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{zone.apps.length - 3} more
                              </Badge>
                            )}
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="secondary">{zone.app_count}</Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="secondary">{zone.endpoint_count}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            zone.status === 'active' ? 'default' :
                            zone.status === 'empty' ? 'secondary' :
                            'outline'
                          }
                        >
                          {zone.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(zone.schema_url, '_blank')}
                          >
                            <FileCode className="h-4 w-4 mr-1" />
                            Schema
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(zone.api_url, '_blank')}
                          >
                            <Link className="h-4 w-4 mr-1" />
                            API
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          ) : (
            <div className="text-center py-12">
              <Globe className="h-12 w-12 mx-auto text-muted-foreground/50" />
              <p className="mt-2 text-muted-foreground">
                No API zones configured
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Configure OpenAPI groups in your Django settings
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
