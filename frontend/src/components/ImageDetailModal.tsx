import { useEffect } from "react";
import { type ImageMetadata } from "../services/galleryService";

/**
 * Props for the ImageDetailModal component
 */
interface ImageDetailModalProps {
  image: ImageMetadata | null; // Image to display, null means modal is closed
  onClose: () => void; // Function to call when the modal is closed
}

/**
 * Modal component that displays detailed information about an image
 *
 * @param image - The image metadata to display, or null to hide the modal
 * @param onClose - Function called when the user closes the modal
 */
export function ImageDetailModal({ image, onClose }: ImageDetailModalProps) {
  // If no image is provided, don't render anything
  if (!image) return null;

  // Add event listener to close modal on escape key
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleEscapeKey);

    // Prevent scrolling on the body when modal is open
    document.body.style.overflow = "hidden";

    return () => {
      window.removeEventListener("keydown", handleEscapeKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  // Format file size to human-readable format
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Format date to local string
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      onClick={onClose}
    >
      {/* Modal content - stop propagation to prevent closing when clicking inside */}
      <div
        className="bg-background rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col md:flex-row"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Image container */}
        <div className="flex-1 min-h-[300px] bg-black flex items-center justify-center overflow-hidden">
          <img
            src={image.url}
            alt={image.caption || image.original_name}
            className="max-h-[70vh] max-w-full object-contain"
          />
        </div>

        {/* Image details */}
        <div className="p-6 flex flex-col w-full md:w-80 md:max-h-[70vh] overflow-y-auto">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-xl font-semibold truncate">
              {image.caption || image.original_name}
            </h3>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
              aria-label="Close"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            {/* Image metadata */}
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">
                File Details
              </h4>
              <dl className="mt-2 space-y-1">
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">File name:</dt>
                  <dd className="text-sm">{image.original_name}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Size:</dt>
                  <dd className="text-sm">{formatFileSize(image.size)}</dd>
                </div>
                {image.dimensions && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-muted-foreground">
                      Dimensions:
                    </dt>
                    <dd className="text-sm">
                      {image.dimensions.width} × {image.dimensions.height}
                    </dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Uploaded:</dt>
                  <dd className="text-sm">{formatDate(image.upload_time)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Status:</dt>
                  <dd className="text-sm capitalize">{image.status}</dd>
                </div>
              </dl>
            </div>

            {/* Tags if available */}
            {image.tags && image.tags.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground">
                  Tags
                </h4>
                <div className="flex flex-wrap gap-1 mt-2">
                  {image.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Caption if available */}
            {image.caption && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground">
                  Caption
                </h4>
                <p className="mt-1 text-sm">{image.caption}</p>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="mt-auto pt-4 flex gap-2">
            <button
              className="flex-1 px-4 py-2 rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              onClick={() => window.open(image.url, "_blank")}
            >
              Open Original
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
