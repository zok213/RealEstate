"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Map, 
  Upload, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  icon: React.ElementType;
  href: string;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
  { label: 'Map Explorer', icon: Map, href: '/map' },
  { label: 'DXF Upload', icon: Upload, href: '/upload' },
  { label: 'Data Analysis', icon: BarChart3, href: '/analysis' },
  { label: 'Configuration', icon: Settings, href: '/settings' },
];

interface SidebarNavigationProps {
  defaultCollapsed?: boolean;
}

export function SidebarNavigation({ defaultCollapsed = false }: SidebarNavigationProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/' || pathname === '/dashboard';
    }
    return pathname?.startsWith(href);
  };

  return (
    <aside 
      className={cn(
        "border-r border-[#1a3d2b] flex flex-col bg-[#0a1a12] z-50 transition-all duration-300",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Header */}
      <div className="p-6 flex items-center gap-3 border-b border-[#1a3d2b]">
        <div className="size-10 bg-primary rounded-md flex items-center justify-center flex-shrink-0">
          <Map className="w-6 h-6 text-[#0a1a12]" />
        </div>
        {!collapsed && (
          <span className="font-bold text-white tracking-tight whitespace-nowrap">
            DXF PARSER <span className="text-primary">PRO</span>
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          const IconComponent = Icon;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-4 px-3 py-3 rounded-md transition-colors",
                active 
                  ? "bg-primary/10 text-primary border border-primary/20" 
                  : "text-[#D1D5DB] hover:bg-[#11261c] hover:text-white"
              )}
              title={collapsed ? item.label : undefined}
            >
              <IconComponent className={cn("shrink-0", collapsed ? "w-6 h-6" : "w-5 h-5")} />
              {!collapsed && (
                <span className="font-medium">{item.label}</span>
              )}
              {!collapsed && item.badge && (
                <span className="ml-auto bg-primary/20 text-primary text-xs font-bold px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Toggle Button */}
      <div className="p-4 border-t border-[#1a3d2b]">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md text-[#D1D5DB] hover:bg-[#11261c] hover:text-white transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <ChevronLeft className="w-5 h-5" />
              <span className="text-sm font-medium">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
