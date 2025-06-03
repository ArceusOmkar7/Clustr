import { apiClient } from "./api";
import { API_ENDPOINTS } from "./endpoints";

/**
 * Interface representing an image's metadata from the backend
 * Contains all information about an uploaded image
 */
export interface ImageMetadata {
  id: string; // Unique identifier for the image
  original_name: string; // Original filename uploaded by the user
  filename: string; // Stored filename on the server
  file_path: string; // Path where the file is stored on the server
  url: string; // Full URL to access the image
  thumbnail_url?: string; // URL for thumbnail version
  upload_time: string; // When the image was uploaded
  size: number; // File size in bytes
  dimensions?: {
    // Image dimensions if available
    width: number;
    height: number;
  };
  status: string; // Processing status (pending/processed/error)
  caption?: string; // Optional image caption
  tags?: string[]; // Optional array of tags for the image
}

/**
 * Interface for the paginated response from the uploads endpoint
 */
export interface GetUploadsResponse {
  data: ImageMetadata[]; // Array of image metadata objects
  total: number; // Total number of images available
  page: number; // Current page number
  limit: number; // Number of items per page
}

/**
 * Service for interacting with the gallery-related API endpoints
 */
export const galleryService = {
  /**
   * Fetch paginated uploads from the backend
   *
   * @param page - Page number (1-indexed)
   * @param limit - Number of items per page
   * @returns Promise with paginated image data
   */ getUploads: async (
    page: number = 1,
    limit: number = 20
  ): Promise<GetUploadsResponse> => {
    const response = await apiClient.get(`${API_ENDPOINTS.GET_UPLOADS}`, {
      params: {
        page,
        limit,
      },
    }); // Add thumbnail URLs to the response data
    const baseURL = `${
      import.meta.env.VITE_BACKEND_URL || "http://localhost"
    }:${import.meta.env.VITE_BACKEND_PORT || "8000"}`;

    const dataWithThumbnails = response.data.data.map(
      (image: ImageMetadata) => ({
        ...image,
        thumbnail_url: `${baseURL}/api/uploads/${image.id}/thumbnail?size=300`,
      })
    );

    return {
      ...response.data,
      data: dataWithThumbnails,
    };
  },
};
