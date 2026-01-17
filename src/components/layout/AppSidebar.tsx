import { 
  LayoutGrid, 
  Network, 
  FileSearch, 
  ClipboardCheck, 
  Lock, 
  ChevronLeft,
  Settings,
  FileText
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const navItems = [
  { title: "Overview", url: "/", icon: LayoutGrid, badge: null },
  { title: "Architecture", url: "/architecture", icon: Network, badge: null },
  { title: "Governance", url: "/governance", icon: Lock, badge: null },
];

const secondaryItems = [
  { title: "Settings", url: "#", icon: Settings },
  { title: "Documentation", url: "#", icon: FileText },
];

export function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside 
      className={cn(
        "flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-200",
        collapsed ? "w-14" : "w-52"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 px-3 h-12 border-b border-sidebar-border">
        <div className="flex items-center justify-center w-7 h-7 rounded bg-primary/10 text-primary">
          <Network className="w-4 h-4" />
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-foreground tracking-tight">NSA-X</span>
        )}
      </div>

      {/* Primary Navigation */}
      <nav className="flex-1 py-3 px-2 space-y-0.5">
        {navItems.map((item) => {
          const isActive = location.pathname === item.url;
          return (
            <NavLink
              key={item.title}
              to={item.url}
              className={cn(
                "flex items-center gap-2.5 px-2.5 py-2 rounded text-sm transition-colors duration-150",
                isActive 
                  ? "bg-sidebar-accent text-foreground" 
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-foreground"
              )}
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {!collapsed && (
                <>
                  <span className="flex-1">{item.title}</span>
                  {item.badge && (
                    <span className="px-1.5 py-0.5 text-xs bg-caution/20 text-caution rounded">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Divider */}
      <div className="mx-3 border-t border-sidebar-border" />

      {/* Secondary Navigation */}
      <nav className="py-3 px-2 space-y-0.5">
        {secondaryItems.map((item) => (
          <a
            key={item.title}
            href={item.url}
            className="flex items-center gap-2.5 px-2.5 py-2 rounded text-sm text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-foreground transition-colors duration-150"
          >
            <item.icon className="w-4 h-4 flex-shrink-0" />
            {!collapsed && <span>{item.title}</span>}
          </a>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <div className="border-t border-sidebar-border p-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="w-full h-8 justify-center text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className={cn(
            "w-4 h-4 transition-transform duration-200",
            collapsed && "rotate-180"
          )} />
        </Button>
      </div>
    </aside>
  );
}
