/**
 * Collection of API endpoint paths used throughout the application
 * Centralizes URL management to make updates easier
 */
export const API_ENDPOINTS = {
  // Image Upload endpoints
  UPLOAD_IMAGES: "/api/upload", // POST endpoint for uploading images
  GET_UPLOADS: "/api/uploads", // GET endpoint for retrieving uploaded images with pagination
};

/**
 * API configuration constants
 */
export const API_CONFIG = {
  TIMEOUT: 30000, // API request timeout in milliseconds
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB in bytes - maximum file size for uploads
  MAX_FILES: 10, // Maximum number of files per upload
  ACCEPTED_IMAGE_TYPES: [
    // Allowed MIME types for image uploads
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
  ],
};
