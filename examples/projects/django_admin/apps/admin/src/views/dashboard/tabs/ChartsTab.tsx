/**
 * ChartsTab Component
 *
 * Displays charts and analytics data:
 * - User registration chart (configurable days)
 * - User activity chart
 * - Activity tracker (GitHub-style heatmap)
 * - Recent users list
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Badge,
} from '@djangocfg/ui';
import { TrendingUp, Activity, Calendar, Users } from 'lucide-react';
import { useDashboardChartsContext } from '@/contexts/dashboard';

export function ChartsTab() {
  const {
    registrationChart,
    isLoadingRegistrationChart,
    registrationChartDays,
    setRegistrationChartDays,

    activityChart,
    isLoadingActivityChart,
    activityChartDays,
    setActivityChartDays,

    activityTracker,
    isLoadingActivityTracker,

    recentUsers,
    isLoadingRecentUsers,
    recentUsersLimit,
    setRecentUsersLimit,
  } = useDashboardChartsContext();

  return (
    <div className="space-y-6">
      {/* Registration Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                User Registrations
              </CardTitle>
              <CardDescription>
                New user registrations over time
              </CardDescription>
            </div>
            <Select
              value={registrationChartDays.toString()}
              onValueChange={(value) => setRegistrationChartDays(Number(value))}
            >
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoadingRegistrationChart ? (
            <Skeleton className="w-full h-64" />
          ) : registrationChart ? (
            <div className="space-y-4">
              {/* Chart Data Preview */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Total Registrations</p>
                  <p className="text-2xl font-bold">
                    {registrationChart.datasets?.[0]?.data?.reduce((a, b) => a + b, 0) || 0}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Time Period</p>
                  <p className="text-2xl font-bold">{registrationChartDays} days</p>
                </div>
              </div>

              {/* Simple data visualization */}
              <div className="space-y-2">
                {registrationChart.labels?.map((label, index) => {
                  const value = registrationChart.datasets?.[0]?.data?.[index] || 0;
                  return (
                    <div key={label} className="flex items-center gap-2">
                      <span className="text-sm w-20 text-muted-foreground">{label}</span>
                      <div className="flex-1 bg-muted rounded-full h-6 overflow-hidden">
                        <div
                          className="bg-primary h-full flex items-center justify-end pr-2"
                          style={{ width: `${value > 0 ? (value / Math.max(...(registrationChart.datasets?.[0]?.data || [1]))) * 100 : 0}%` }}
                        >
                          {value > 0 && (
                            <span className="text-xs font-medium text-primary-foreground">{value}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No data available</p>
          )}
        </CardContent>
      </Card>

      {/* Activity Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                User Activity
              </CardTitle>
              <CardDescription>
                User activity patterns over time
              </CardDescription>
            </div>
            <Select
              value={activityChartDays.toString()}
              onValueChange={(value) => setActivityChartDays(Number(value))}
            >
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoadingActivityChart ? (
            <Skeleton className="w-full h-64" />
          ) : activityChart ? (
            <div className="space-y-4">
              {/* Chart Data Preview */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Total Activities</p>
                  <p className="text-2xl font-bold">
                    {activityChart.datasets?.[0]?.data?.reduce((a, b) => a + b, 0) || 0}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Time Period</p>
                  <p className="text-2xl font-bold">{activityChartDays} days</p>
                </div>
              </div>

              {/* Simple data visualization */}
              <div className="space-y-2">
                {activityChart.labels?.map((label, index) => {
                  const value = activityChart.datasets?.[0]?.data?.[index] || 0;
                  return (
                    <div key={label} className="flex items-center gap-2">
                      <span className="text-sm w-20 text-muted-foreground">{label}</span>
                      <div className="flex-1 bg-muted rounded-full h-6 overflow-hidden">
                        <div
                          className="bg-primary h-full flex items-center justify-end pr-2"
                          style={{ width: `${value > 0 ? (value / Math.max(...(activityChart.datasets?.[0]?.data || [1]))) * 100 : 0}%` }}
                        >
                          {value > 0 && (
                            <span className="text-xs font-medium text-primary-foreground">{value}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No data available</p>
          )}
        </CardContent>
      </Card>

      {/* Activity Tracker */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Activity Tracker
          </CardTitle>
          <CardDescription>
            GitHub-style activity heatmap (52 weeks)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingActivityTracker ? (
            <Skeleton className="w-full h-32" />
          ) : activityTracker && activityTracker.length > 0 ? (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Showing activity for the last {activityTracker.length} days
              </p>

              {/* GitHub-style heatmap: 52 weeks x 7 days */}
              <div className="overflow-x-auto pb-2">
                <div
                  className="inline-grid"
                  style={{
                    gridTemplateColumns: `repeat(${Math.ceil(activityTracker.length / 7)}, 12px)`,
                    gridTemplateRows: 'repeat(7, 12px)',
                    gridAutoFlow: 'column',
                    gap: '3px'
                  }}
                >
                  {activityTracker.map((day: any, index: number) => (
                    <div
                      key={index}
                      className="rounded-sm border border-border/40"
                      style={{
                        width: '12px',
                        height: '12px',
                        backgroundColor: day.color || 'hsl(var(--muted))'
                      }}
                      title={`${day.date}: ${day.count} activities (level ${day.level})`}
                    />
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">
                  Total active days: {activityTracker.filter((d: any) => d.count > 0).length}
                </p>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <span>Less</span>
                  <div className="flex gap-1">
                    <div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: 'hsl(var(--muted))' }} />
                    <div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: 'hsl(var(--primary) / 0.2)' }} />
                    <div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: 'hsl(var(--primary) / 0.4)' }} />
                    <div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: 'hsl(var(--primary) / 0.6)' }} />
                    <div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: 'hsl(var(--primary) / 0.8)' }} />
                  </div>
                  <span>More</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No activity data available</p>
          )}
        </CardContent>
      </Card>

      {/* Recent Users */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Recent Users
              </CardTitle>
              <CardDescription>
                Recently registered users
              </CardDescription>
            </div>
            <Select
              value={recentUsersLimit.toString()}
              onValueChange={(value) => setRecentUsersLimit(Number(value))}
            >
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">Show 5</SelectItem>
                <SelectItem value="10">Show 10</SelectItem>
                <SelectItem value="20">Show 20</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoadingRecentUsers ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="w-full h-12" />
              ))}
            </div>
          ) : recentUsers && recentUsers.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Registered</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentUsers.map((user: any) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge variant={user.is_active ? 'default' : 'secondary'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {new Date(user.date_joined).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-center text-muted-foreground py-8">No users found</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
