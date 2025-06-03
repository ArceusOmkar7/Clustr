import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import {
  healthService,
  type HealthCheckResponse,
  type ServiceHealth,
} from "../services/healthService";

const Health: React.FC = () => {
  const [healthData, setHealthData] = useState<HealthCheckResponse | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await healthService.getHealth();
      setHealthData(data);
      setLastRefresh(new Date());
    } catch (err) {
      setError("Failed to fetch health data. Backend may be unreachable.");
      console.error("Health check error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
  }, []);

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "online":
      case "connected":
        return "bg-green-500";
      case "degraded":
      case "unhealthy":
        return "bg-yellow-500";
      default:
        return "bg-red-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "online":
      case "connected":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "degraded":
      case "unhealthy":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusVariant = (
    status: string
  ): "default" | "secondary" | "destructive" => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "online":
      case "connected":
        return "default";
      case "degraded":
      case "unhealthy":
        return "secondary";
      default:
        return "destructive";
    }
  };

  const ServiceCard: React.FC<{
    title: string;
    service: ServiceHealth;
    showDetails?: boolean;
  }> = ({ title, service, showDetails = true }) => (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          {getStatusIcon(service.status)}
          {title}
          <Badge variant={getStatusVariant(service.status)} className="ml-auto">
            {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {showDetails && (
          <>
            {service.version && (
              <div className="text-sm text-gray-600">
                <strong>Version:</strong> {service.version}
              </div>
            )}
            {service.url && (
              <div className="text-sm text-gray-600">
                <strong>URL:</strong> {service.url}
              </div>
            )}
            {service.host && (
              <div className="text-sm text-gray-600">
                <strong>Host:</strong> {service.host}
              </div>
            )}
            {service.response_time && (
              <div className="text-sm text-gray-600">
                <strong>Response Time:</strong> {service.response_time}
              </div>
            )}
            {service.image_count !== undefined && (
              <div className="text-sm text-gray-600">
                <strong>Total Images:</strong>{" "}
                {service.image_count.toLocaleString()}
              </div>
            )}
            {service.captioned_images !== undefined && (
              <div className="text-sm text-gray-600">
                <strong>Captioned:</strong>{" "}
                {service.captioned_images.toLocaleString()}
              </div>
            )}
            {service.uncaptioned_images !== undefined && (
              <div className="text-sm text-gray-600">
                <strong>Uncaptioned:</strong>{" "}
                {service.uncaptioned_images.toLocaleString()}
              </div>
            )}
            {service.error && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                <strong>Error:</strong> {service.error}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );

  if (loading && !healthData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
          <span className="ml-2 text-lg">Loading health status...</span>
        </div>
      </div>
    );
  }

  if (error && !healthData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              Connection Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchHealthData} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          System Health Dashboard
        </h1>
        <p className="text-gray-600">
          Monitor the status of all Clustr services
        </p>
      </div>

      {/* Overall Status */}
      {healthData && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(healthData.status)}
              Overall System Status
              <Badge
                variant={getStatusVariant(healthData.status)}
                className="ml-auto"
              >
                {healthData.status.charAt(0).toUpperCase() +
                  healthData.status.slice(1)}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <strong>Last Check:</strong>
                <br />
                {new Date(healthData.timestamp).toLocaleString()}
              </div>
              <div>
                <strong>Response Time:</strong>
                <br />
                {healthData.response_time}
              </div>
              <div>
                <strong>Auto Refresh:</strong>
                <br />
                {lastRefresh.toLocaleTimeString()}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <Button onClick={fetchHealthData} disabled={loading}>
          <RefreshCw
            className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
          />
          {loading ? "Refreshing..." : "Refresh Status"}
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            window.open(healthService.getHealthPageUrl(), "_blank")
          }
        >
          <ExternalLink className="h-4 w-4 mr-2" />
          Backend Health Page
        </Button>
      </div>

      {/* Service Status Cards */}
      {healthData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ServiceCard
            title="Backend Service"
            service={healthData.services.backend}
            showDetails={true}
          />
          <ServiceCard
            title="Database Service"
            service={healthData.services.database}
            showDetails={true}
          />
          <ServiceCard
            title="BLIP Captioner"
            service={healthData.services.captioner}
            showDetails={true}
          />
        </div>
      )}

      {/* Auto-refresh info */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>
          This page does not auto-refresh. Click the refresh button to get the
          latest status.
        </p>
        <p className="mt-1">
          For continuous monitoring, consider setting up automated health
          checks.
        </p>
      </div>
    </div>
  );
};

export default Health;
