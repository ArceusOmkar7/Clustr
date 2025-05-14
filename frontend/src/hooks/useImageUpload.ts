import { useState, useCallback } from "react";
import {
  uploadService,
  type UploadProgress,
  type UploadResponse,
} from "../services/uploadService";
import { type UploadableFile } from "../types";

export interface UseImageUploadReturn {
  uploadFiles: (files: UploadableFile[]) => Promise<UploadableFile[]>;
  isUploading: boolean;
  uploadProgress: Record<string, number>;
}

export const useImageUpload = (): UseImageUploadReturn => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>(
    {}
  );

  const uploadFiles = useCallback(async (files: UploadableFile[]) => {
    const pendingFiles = files.filter((file) => file.status === "pending");

    if (pendingFiles.length === 0) {
      return files;
    }

    setIsUploading(true);
    const updatedFiles = [...files];

    try {
      // Upload files one by one to track individual progress
      for (const fileData of pendingFiles) {
        const fileIndex = updatedFiles.findIndex((f) => f.id === fileData.id);

        if (fileIndex === -1) continue;

        // Update status to uploading
        updatedFiles[fileIndex] = {
          ...updatedFiles[fileIndex],
          status: "uploading",
          progress: 0,
        };

        try {
          const response = await uploadService.uploadSingleImage(
            fileData.file,
            (progress: UploadProgress) => {
              setUploadProgress((prev) => ({
                ...prev,
                [fileData.id]: progress.percentage,
              }));
              updatedFiles[fileIndex] = {
                ...updatedFiles[fileIndex],
                progress: progress.percentage,
              };
            }
          );

          // Debug the response structure
          console.log("Upload response:", response);

          // Validate the response has required data
          if (
            !response ||
            !response.data ||
            !Array.isArray(response.data) ||
            response.data.length === 0
          ) {
            throw new Error("Invalid response from upload service");
          }

          const uploadedInfo = response.data[0];
          updatedFiles[fileIndex] = {
            ...updatedFiles[fileIndex],
            status: "success",
            progress: 100,
            uploadedPath: uploadedInfo.preview_url,
          };

          // Clear progress for this file
          setUploadProgress((prev) => {
            const { [fileData.id]: _, ...rest } = prev;
            return rest;
          });
        } catch (error: any) {
          console.error("Upload error:", fileData.file.name, error);

          const errorMessage =
            error?.response?.data?.detail ||
            error?.message ||
            "Upload failed. Please try again.";

          updatedFiles[fileIndex] = {
            ...updatedFiles[fileIndex],
            status: "error",
            progress: 0,
            error: errorMessage,
          };

          // Clear progress for this file
          setUploadProgress((prev) => {
            const { [fileData.id]: _, ...rest } = prev;
            return rest;
          });
        }
      }
    } finally {
      setIsUploading(false);
      setUploadProgress({}); // Clear all progress when done
    }

    return updatedFiles;
  }, []);

  return {
    uploadFiles,
    isUploading,
    uploadProgress,
  };
};
