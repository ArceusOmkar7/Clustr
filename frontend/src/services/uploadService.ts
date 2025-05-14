import { apiClient } from "./api";
import { API_ENDPOINTS } from "./endpoints";
import { type AxiosProgressEvent } from "axios";

export interface UploadResponse {
  message: string;
  data: {
    stored_filename: string;
    preview_url: string;
    original_filename: string;
    file_size: number;
  }[];
}

export interface UploadProgress {
  loaded: number;
  total: number | undefined;
  percentage: number;
}

export const uploadService = {
  uploadImages: async (
    files: File[],
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResponse> => {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await apiClient.post<UploadResponse>(
      API_ENDPOINTS.UPLOAD_IMAGES,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentage = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress({
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage,
            });
          }
        },
      }
    );

    return response.data;
  },

  uploadSingleImage: async (
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResponse> => {
    return uploadService.uploadImages([file], onProgress);
  },
};
