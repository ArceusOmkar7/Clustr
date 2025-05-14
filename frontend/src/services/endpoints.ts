export const API_ENDPOINTS = {
  // Image Upload endpoints
  UPLOAD_IMAGES: "/api/upload",
};

// Base API configuration
export const API_CONFIG = {
  TIMEOUT: 30000,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB in bytes
  MAX_FILES: 10,
  ACCEPTED_IMAGE_TYPES: ["image/jpeg", "image/png", "image/gif", "image/webp"],
};
