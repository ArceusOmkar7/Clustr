import { useState } from "react";
import { useGallery } from "../hooks/useGallery";
import { GalleryItem } from "../components/GalleryItem";
import { InfiniteScrollTrigger } from "../components/InfiniteScrollTrigger";
import { ImageDetailModal } from "../components/ImageDetailModal";
import { type ImageMetadata } from "../services/galleryService";

/**
 * Gallery page component that displays uploaded images with infinite scrolling
 *
 * Features:
 * - Loads 24 images at a time
 * - Automatically loads more images when user scrolls to the bottom
 * - Displays a loading indicator when fetching more images
 * - Shows a placeholder when no images are available
 * - Handles error states
 * - Opens a detailed view when clicking on an image
 */
export default function Gallery() {
  // Use the gallery hook to fetch and manage images with infinite scrolling
  const { images, loading, error, hasMore, loadMore } = useGallery(24);

  // State to track the currently selected image for the modal
  const [selectedImage, setSelectedImage] = useState<ImageMetadata | null>(
    null
  );

  // Handler for clicking on an image
  const handleImageClick = (image: ImageMetadata) => {
    setSelectedImage(image);
  };

  // Handler for closing the modal
  const handleCloseModal = () => {
    setSelectedImage(null);
  };

  return (
    <div className="container mx-auto py-6 px-4">
      <h1 className="text-3xl font-bold">Gallery</h1>
      <p className="mt-2 text-muted-foreground">
        Browse your uploaded images with infinite scrolling.
      </p>

      {/* Error message when image loading fails */}
      {error && (
        <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md">
          Error loading images: {error.message}
        </div>
      )}

      {/* Empty state when no images are available */}
      {images.length === 0 && !loading ? (
        <div className="mt-8 flex flex-col items-center justify-center py-10 text-center">
          <div className="text-6xl mb-4">📷</div>
          <h2 className="text-xl font-semibold">No images yet</h2>
          <p className="text-muted-foreground mt-2">
            Upload some images to see them in your gallery.
          </p>
        </div>
      ) : (
        /* Responsive grid layout for gallery items */
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-6">
          {images.map((image) => (
            <GalleryItem
              key={image.id}
              image={image}
              onClick={() => handleImageClick(image)}
            />
          ))}
        </div>
      )}

      {/* Infinite scroll trigger that loads more images when visible */}
      {(loading || hasMore) && (
        <div className="mt-8">
          <InfiniteScrollTrigger onIntersect={loadMore} disabled={!hasMore} />
        </div>
      )}

      {/* Image detail modal */}
      <ImageDetailModal image={selectedImage} onClose={handleCloseModal} />
    </div>
  );
}
