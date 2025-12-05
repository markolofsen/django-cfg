import { HashRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Button } from '@djangocfg/ui-core';
import { cn } from '@djangocfg/ui-core/lib';
import { ThemeProvider } from '@djangocfg/electron-ui';
import { Home as HomeIcon, Info, Settings as SettingsIcon, Terminal as TerminalIcon } from 'lucide-react';
import Home from './pages/Home';
import About from './pages/About';
import Settings from './pages/Settings';
import Terminal from './pages/Terminal';

function NavLink({ to, children, icon: Icon }: { to: string; children: React.ReactNode; icon: React.ComponentType<{ className?: string }> }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to}>
      <Button
        variant={isActive ? "secondary" : "ghost"}
        size="sm"
        className={cn(
          "gap-2",
          isActive && "bg-primary/10 text-primary"
        )}
      >
        <Icon className="h-4 w-4" />
        {children}
      </Button>
    </Link>
  );
}

function Navigation() {
  return (
    <nav className="border-b bg-card">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-4">
            <span className="text-xl font-bold text-primary">DjangoCFG</span>
            <div className="flex gap-1">
              <NavLink to="/" icon={HomeIcon}>Home</NavLink>
              <NavLink to="/about" icon={Info}>About</NavLink>
              <NavLink to="/settings" icon={SettingsIcon}>Settings</NavLink>
              <NavLink to="/terminal" icon={TerminalIcon}>Terminal</NavLink>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <ThemeProvider defaultTheme="system">
      <HashRouter>
        <div className="min-h-screen bg-background text-foreground">
          <Navigation />
          <main className="max-w-7xl mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/terminal" element={<Terminal />} />
            </Routes>
          </main>
        </div>
      </HashRouter>
    </ThemeProvider>
  );
}
