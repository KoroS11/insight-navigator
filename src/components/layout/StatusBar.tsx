import { useState, useEffect } from "react";
import { Wifi, WifiOff, Clock, Users, Bell } from "lucide-react";

export function StatusBar() {
  const [time, setTime] = useState(new Date());
  const [connected, setConnected] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    }) + ' UTC';
  };

  return (
    <div className="h-8 px-4 flex items-center justify-between border-b border-border bg-card text-xs">
      <div className="flex items-center gap-6">
        {/* Connection Status */}
        <div className="flex items-center gap-1.5">
          {connected ? (
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
          Last sync: 3s ago
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
          <span className="text-caution">3 pending</span>
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
