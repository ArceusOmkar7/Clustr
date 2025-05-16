import { useState } from "react";
import { type ImageMetadata } from "../services/galleryService";

/**
 * Props for the GalleryItem component
 */
interface GalleryItemProps {
  image: ImageMetadata; // Image metadata to display
  onClick?: () => void; // Optional click handler for the image
}

/**
 * Component that displays a single image in the gallery
 * Features:
 * - Loading spinner while the image is loading
 * - Hover effects with image information
 * - Responsive square aspect ratio
 *
 * @param image - Image metadata object to display
 * @param onClick - Optional callback for when the image is clicked
 */
export function GalleryItem({ image, onClick }: GalleryItemProps) {
  // Track if the image is still loading
  const [isLoading, setIsLoading] = useState(true);

  // Called when the image has finished loading
  const handleImageLoad = () => {
    setIsLoading(false);
  };

  return (
    <div
      className="group relative bg-card rounded-lg overflow-hidden aspect-square cursor-pointer hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      {/* Loading spinner shown while the image is loading */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-card">
          <div className="w-8 h-8 border-2 border-primary rounded-full border-t-transparent animate-spin" />
        </div>
      )}

      {/* The actual image, with lazy loading for performance */}
      <img
        src={image.url}
        alt={image.caption || image.original_name}
        className={`w-full h-full object-cover transition-opacity ${
          isLoading ? "opacity-0" : "opacity-100"
        }`}
        loading="lazy"
        onLoad={handleImageLoad}
      />

      {/* Overlay with image details that appears on hover */}
      <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
        <p className="text-white text-sm truncate">
          {image.caption || image.original_name}
        </p>
        {image.dimensions && (
          <p className="text-white/80 text-xs">
            {image.dimensions.width} × {image.dimensions.height}
          </p>
        )}
      </div>
    </div>
  );
}
