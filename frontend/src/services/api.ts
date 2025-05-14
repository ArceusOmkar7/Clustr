import axios from "axios";

const baseURL = `${import.meta.env.VITE_BACKEND_URL || "http://localhost"}:${
  import.meta.env.VITE_BACKEND_PORT || "8000"
}`;

console.log(baseURL);

export const apiClient = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  }
);
