import { useState, useEffect } from "react";
import { Wifi, WifiOff, Clock, Users, Bell, Loader2 } from "lucide-react";
import { useHealth } from "@/hooks/use-system";
import { usePendingAlertCount } from "@/hooks/use-alerts";

export function StatusBar() {
  const [time, setTime] = useState(new Date());
  const { data: health, isLoading: healthLoading, dataUpdatedAt } = useHealth();
  const { data: pendingCount } = usePendingAlertCount();

  // Calculate time since last sync
  const [syncAgo, setSyncAgo] = useState<string>("--");
  
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (dataUpdatedAt) {
      const updateSyncAgo = () => {
        const seconds = Math.floor((Date.now() - dataUpdatedAt) / 1000);
        setSyncAgo(seconds < 60 ? `${seconds}s ago` : `${Math.floor(seconds / 60)}m ago`);
      };
      updateSyncAgo();
      const interval = setInterval(updateSyncAgo, 1000);
      return () => clearInterval(interval);
    }
  }, [dataUpdatedAt]);

  const connected = health?.status === 'ok' || health?.status === 'healthy';

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'UTC'
    }) + ' UTC';
  };

  return (
    <div className="h-8 px-4 flex items-center justify-between border-b border-border bg-card text-xs">
      <div className="flex items-center gap-6">
        {/* Connection Status */}
        <div className="flex items-center gap-1.5">
          {healthLoading ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />
              <span className="text-muted-foreground">Connecting...</span>
            </>
          ) : connected ? (
            <>
              <span className="status-dot status-dot-active connection-pulse" />
              <Wifi className="w-3 h-3 text-muted-foreground" />
              <span className="text-muted-foreground">Connected</span>
            </>
          ) : (
            <>
              <span className="status-dot status-dot-error" />
              <WifiOff className="w-3 h-3 text-destructive" />
              <span className="text-destructive">Disconnected</span>
            </>
          )}
        </div>

        {/* Data Freshness */}
        <div className="text-muted-foreground">
          Last sync: {syncAgo}
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* Active Analysts */}
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <Users className="w-3 h-3" />
          <span>2 analysts online</span>
        </div>

        {/* Alerts */}
        <div className="flex items-center gap-1.5">
          <Bell className="w-3 h-3 text-muted-foreground" />
          <span className={pendingCount && pendingCount > 0 ? "text-caution" : "text-muted-foreground"}>
            {pendingCount ?? 0} pending
          </span>
        </div>

        {/* Time */}
        <div className="flex items-center gap-1.5 text-muted-foreground font-mono">
          <Clock className="w-3 h-3" />
          <span>{formatTime(time)}</span>
        </div>
      </div>
    </div>
  );
}
