export interface UploadableFile {
  id: string; // Unique client-side ID
  file: File;
  previewUrl: string; // For client-side preview using URL.createObjectURL()
  progress: number; // 0-100
  status: "pending" | "uploading" | "success" | "error";
  error?: string; // Error message if upload fails
  uploadedPath?: string; // Path/URL from server after successful upload
}
