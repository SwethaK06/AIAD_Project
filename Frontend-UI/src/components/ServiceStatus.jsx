import { useState, useEffect, useCallback } from "react";
import {
  FaDatabase,
  FaRobot,
  FaRoute,
  FaDesktop,
  FaCheckCircle,
  FaTimesCircle,
  FaSyncAlt
} from "react-icons/fa";

// This code creates a starting list of all services in your application and their health-check information. 
// It defines that your Service Status / System Health Dashboard will use to show whether each backend service is online or offline.
const INITIAL_SERVICES = [
  {
    id: "database_service",
    name: "Database Service",
    icon: <FaDatabase />,
    endpoint: "/api/health/database",
    status: "Checking...",
    online: false,
    latency: "--"
  },
  {
    id: "ai_prediction",
    name: "AI Prediction API",
    icon: <FaRobot />,
    endpoint: "/api/health/ml",
    status: "Checking...",
    online: false,
    latency: "--"
  },
  {
    id: "route_optimizer",
    name: "Route Optimizer",
    icon: <FaRoute />,
    endpoint: "/api/health/routing",
    status: "Checking...",
    online: false,
    latency: "--"
  },
  {
    id: "dashboard_api",
    name: "Dashboard API",
    icon: <FaDesktop />,
    endpoint: "/api/health/dashboard",
    status: "Checking...",
    online: false,
    latency: "--"
  }
];

export default function ServiceStatus() {
  const [services, setServices] = useState(INITIAL_SERVICES);
  const [lastSync, setLastSync] = useState("--:--");
  const [isRefreshing, setIsRefreshing] = useState(false);

  // It takes the services you defined in INITIAL_SERVICES, checks each service's health endpoint, measures how long each one takes to respond, and then updates the UI with Online/Offline status and latency.
  const checkHealth = useCallback(async () => {
    setIsRefreshing(true);

    const now = new Date();

    const formattedTime = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });

    const updatedServices = await Promise.all(
      INITIAL_SERVICES.map(async (service) => {
        const startTime = performance.now();

        try {
          const controller = new AbortController();

          const timeoutId = setTimeout(() => {
            controller.abort();
          }, 6000);

          const res = await fetch(service.endpoint, {
            method: "GET",
            signal: controller.signal,
            cache: "no-store"
          });

          clearTimeout(timeoutId);

          const durationMs = Math.round(
            performance.now() - startTime
          );

          if (res.ok) {
            return {
              ...service,
              status: "Online",
              online: true,
              latency: `${durationMs} ms`
            };
          }

          return {
            ...service,
            status: "Offline",
            online: false,
            latency: "--"
          };

        } catch (err) {
          return {
            ...service,
            status: "Offline",
            online: false,
            latency: "--"
          };
        }
      })
    );

    setServices(updatedServices);
    setLastSync(formattedTime);
    setIsRefreshing(false);

  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  const onlineCount = services.filter(s => s.online).length;
  const totalCount = services.length;
  const healthPercent = Math.round((onlineCount / totalCount) * 100);

  let podStatus = "Healthy";
  let podColor = "#16a34a";
  if (onlineCount === 0) {
    podStatus = "Offline";
    podColor = "#dc2626";
  } else if (onlineCount < totalCount) {
    podStatus = "Degraded";
    podColor = "#ea580c";
  }

  return (
    <div className="section">
      <div className="health-header">
        <h2 className="section-title">⚙️ System Health Dashboard</h2>
        <button className="health-refresh-btn" onClick={checkHealth} disabled={isRefreshing}>
          <FaSyncAlt className={isRefreshing ? "spin-icon" : ""} />
          {isRefreshing ? "Checking..." : "Refresh Status"}
        </button>
      </div>

      <div className="service-grid">
        {services.map((service) => (
          <div className="service-card" key={service.id}>
            <div className="service-icon">{service.icon}</div>

            <div>
              <h3>{service.name}</h3>
              <p className={service.online ? "online" : "offline"}>
                {service.online ? <FaCheckCircle /> : <FaTimesCircle />}
                {service.status}
              </p>
            </div>

            <div className="latency">{service.latency}</div>
          </div>
        ))}
      </div>

      <hr />

      <div className="system-summary">
        <div>
          <h3>Overall Health</h3>
          <h2 style={{ color: healthPercent > 70 ? "#16a34a" : healthPercent > 30 ? "#ea580c" : "#dc2626" }}>
            {healthPercent}%
          </h2>
        </div>

        <div>
          <h3>Containers Running</h3>
          <h2>{onlineCount} / {totalCount}</h2>
        </div>

        <div>
          <h3>Kubernetes Pods</h3>
          <h2 style={{ color: podColor }}>{podStatus}</h2>
        </div>

        <div>
          <h3>Last Sync</h3>
          <h2>{lastSync}</h2>
        </div>
      </div>
    </div>
  );
}