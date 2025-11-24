import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { useAuth } from '@djangocfg/layouts';
import {
  Users,
  Wallet,
  Bitcoin,
  TrendingUp,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

export default function DashboardView() {
  const { user, isLoading: userLoading } = useAuth();

  if (userLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                <div className="h-4 w-4 bg-muted animate-pulse rounded" />
              </CardHeader>
              <CardContent>
                <div className="h-8 w-16 bg-muted animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Portfolio Balance',
      value: '$10,234.56',
      description: 'Total balance',
      icon: DollarSign,
      trend: '+12.5%',
      trendUp: true
    },
    {
      title: 'Active Trades',
      value: '24',
      description: '8 pending orders',
      icon: TrendingUp,
      trend: '+8.2%',
      trendUp: true
    },
    {
      title: 'Crypto Wallets',
      value: '12',
      description: '5 active coins',
      icon: Wallet,
      trend: '+4.3%',
      trendUp: true
    }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back, {user?.display_username || 'User'}! Here's what's happening.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.description}
              </p>
              <div className="flex items-center mt-1">
                {stat.trendUp ? (
                  <ArrowUpRight className="h-3 w-3 text-green-600 dark:text-green-400 mr-1" />
                ) : (
                  <ArrowDownRight className="h-3 w-3 text-red-600 dark:text-red-400 mr-1" />
                )}
                <p className={`text-xs ${stat.trendUp ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {stat.trend} from last month
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* User Profile Card */}
      <Card>
        <CardHeader>
          <CardTitle>User Profile</CardTitle>
          <CardDescription>Your account information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Username</span>
            </div>
            <span className="text-sm font-medium">{user?.display_username || 'N/A'}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Email</span>
            </div>  
            <span className="text-sm font-medium">{user?.email || 'N/A'}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wallet className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Member Since</span>
            </div>
            <span className="text-sm font-medium">
              {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
