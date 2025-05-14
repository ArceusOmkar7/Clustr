import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { toast } from "sonner";
import { UploadCloud, XCircle, CheckCircle2, Loader2 } from "lucide-react";
import { type UploadableFile } from "../types";

interface ImageUploaderProps {
  onUploadComplete: (uploadedFiles: UploadableFile[]) => void;
  backendUrl: string;
}

const MAX_FILES = 10;
const MAX_SIZE_MB = 5;
const ACCEPTED_IMAGE_TYPES = {
  "image/jpeg": [],
  "image/png": [],
  "image/gif": [],
  "image/webp": [],
};

export function UploadComponent({
  onUploadComplete,
  backendUrl,
}: ImageUploaderProps) {
  const [files, setFiles] = useState<UploadableFile[]>([]);

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    if (fileRejections.length > 0) {
      fileRejections.forEach(({ errors }) => {
        errors.forEach((err: any) =>
          toast.error("File Error", { description: err.message })
        );
      });
    }

    const newFiles = acceptedFiles.map((file) => ({
      id: uuidv4(),
      file,
      previewUrl: URL.createObjectURL(file),
      progress: 0,
      status: "pending" as const,
    }));

    setFiles((prev) => [...prev, ...newFiles].slice(0, MAX_FILES));
  }, []);

  // Cleanup preview URLs
  useEffect(() => {
    return () => {
      files.forEach((file) => {
        if (file.previewUrl.startsWith("blob:")) {
          URL.revokeObjectURL(file.previewUrl);
        }
      });
    };
  }, [files]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_IMAGE_TYPES,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    maxFiles: MAX_FILES,
    multiple: true,
  });

  // Update file progress
  const updateFile = (id: string, updates: Partial<UploadableFile>) => {
    setFiles((prev) =>
      prev.map((file) => (file.id === id ? { ...file, ...updates } : file))
    );
  };

  // Upload files
  const handleUpload = async () => {
    const pendingFiles = files.filter((file) => file.status === "pending");

    if (pendingFiles.length === 0) {
      toast("No new files to upload.");
      return;
    }

    let successful = true;

    for (const file of pendingFiles) {
      updateFile(file.id, { progress: 0, status: "uploading" });

      const formData = new FormData();
      formData.append("files", file.file);

      try {
        const response = await axios.post(backendUrl, formData, {
          onUploadProgress: (event) => {
            const percent = event.total
              ? Math.round((event.loaded * 100) / event.total)
              : 0;
            updateFile(file.id, { progress: percent });
          },
        });

        const uploadedInfo = response.data.data[0];
        updateFile(file.id, {
          progress: 100,
          status: "success",
          uploadedPath: uploadedInfo.preview_url,
        });
      } catch (error) {
        console.error("Upload error:", file.file.name, error);
        const errorMessage =
          axios.isAxiosError(error) && error.response?.data?.detail
            ? error.response.data.detail
            : "Upload failed. Please try again.";

        updateFile(file.id, { status: "error", error: errorMessage as string });
        toast.error(`Upload Failed: ${file.file.name}`, {
          description: errorMessage as string,
        });
        successful = false;
      }
    }

    onUploadComplete(files);

    if (successful && pendingFiles.length > 0) {
      toast.success("All files uploaded successfully!");
    } else if (pendingFiles.length > 0) {
      toast.warning("Some files failed to upload.");
    }
  };

  // Remove file
  const removeFile = (id: string) => {
    const fileToRemove = files.find((f) => f.id === id);
    if (fileToRemove?.previewUrl.startsWith("blob:")) {
      URL.revokeObjectURL(fileToRemove.previewUrl);
    }
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Upload Your Photos</CardTitle>
        <CardDescription>
          Drag & drop images or click to browse. Max {MAX_SIZE_MB}MB per file.
          Up to {MAX_FILES} files.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`p-8 border-2 border-dashed rounded-md cursor-pointer
            ${
              isDragActive
                ? "border-primary bg-primary/10"
                : "border-border hover:border-primary/50"
            }
            transition-colors text-center`}
        >
          <input {...getInputProps()} />
          <UploadCloud className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          {isDragActive ? (
            <p className="text-primary">Drop the files here ...</p>
          ) : (
            <p>
              Drag & drop images or click to browse. Max {MAX_SIZE_MB}MB per
              file.
            </p>
          )}
        </div>

        {files.length > 0 && (
          <div className="mt-6 space-y-4">
            <h3 className="text-lg font-medium">Selected Files:</h3>
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center p-3 border rounded-md gap-3"
              >
                <img
                  src={
                    file.status === "success" && file.uploadedPath
                      ? file.uploadedPath
                      : file.previewUrl
                  }
                  alt={file.file.name}
                  className="w-16 h-16 object-cover rounded"
                />
                <div className="flex-1">
                  <p className="text-sm font-medium truncate">
                    {file.file.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {(file.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  {file.status === "uploading" && (
                    <Progress value={file.progress} className="h-2 mt-1" />
                  )}
                  {file.status === "error" && (
                    <p className="text-xs text-destructive mt-1">
                      {file.error}
                    </p>
                  )}
                </div>
                {file.status === "pending" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(file.id)}
                    aria-label="Remove file"
                  >
                    <XCircle className="w-5 h-5 text-muted-foreground hover:text-destructive" />
                  </Button>
                )}
                {file.status === "uploading" && (
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                )}
                {file.status === "success" && (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                )}
                {file.status === "error" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(file.id)}
                    aria-label="Remove file"
                  >
                    <XCircle className="w-5 h-5 text-destructive" />
                  </Button>
                )}
              </div>
            ))}
            <Button
              onClick={handleUpload}
              disabled={files.every(
                (f) => f.status === "uploading" || f.status === "success"
              )}
              className="w-full"
            >
              {files.some((f) => f.status === "uploading") && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Upload {files.filter((f) => f.status === "pending").length}{" "}
              File(s)
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
