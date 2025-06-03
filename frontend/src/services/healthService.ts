import { apiClient } from "./api";

export interface ServiceHealth {
  status: string;
  version?: string;
  error?: string;
  response_time?: string;
  url?: string;
  host?: string;
  image_count?: number;
  captioned_images?: number;
  uncaptioned_images?: number;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  response_time: string;
  services: {
    backend: ServiceHealth;
    database: ServiceHealth;
    captioner: ServiceHealth;
  };
}

export const healthService = {
  /**
   * Get comprehensive health check for all services
   */
  async getHealth(): Promise<HealthCheckResponse> {
    const response = await apiClient.get<HealthCheckResponse>("/api/health");
    return response.data;
  },

  /**
   * Get health check for captioner service only
   */
  async getCaptionerHealth(): Promise<ServiceHealth> {
    const response = await apiClient.get<ServiceHealth>(
      "/api/health/captioner"
    );
    return response.data;
  },

  /**
   * Get health check for database service only
   */
  async getDatabaseHealth(): Promise<ServiceHealth> {
    const response = await apiClient.get<ServiceHealth>("/api/health/database");
    return response.data;
  },

  /**
   * Check if backend is reachable
   */
  async checkBackendReachable(): Promise<boolean> {
    try {
      await apiClient.get("/", { timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Get the backend health page URL
   */
  getHealthPageUrl(): string {
    return `${apiClient.defaults.baseURL}/api/health/page`;
  },
};
