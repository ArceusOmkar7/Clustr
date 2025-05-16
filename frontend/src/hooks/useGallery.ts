import { useState, useEffect, useRef, useCallback } from "react";
import { galleryService, type ImageMetadata } from "../services/galleryService";

/**
 * Interface for the return value of the useGallery hook
 */
interface UseGalleryResult {
  images: ImageMetadata[]; // Array of loaded images
  loading: boolean; // Whether images are currently being loaded
  error: Error | null; // Any error that occurred during loading
  hasMore: boolean; // Whether there are more images to load
  loadMore: () => void; // Function to trigger loading more images
}

/**
 * Custom hook for managing gallery images with infinite scrolling
 *
 * @param initialLimit - Number of images to load per page
 * @returns Object containing images, loading state, and functions to control loading
 */
export function useGallery(initialLimit: number = 20): UseGalleryResult {
  const [images, setImages] = useState<ImageMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // We use this to prevent multiple concurrent requests
  const isLoadingRef = useRef(false);

  /**
   * Fetch images from the backend with the current page and limit
   * This is wrapped in useCallback to prevent unnecessary re-renders
   */
  const fetchImages = useCallback(async () => {
    // Skip if already loading or no more images to load
    if (isLoadingRef.current || !hasMore) return;

    try {
      isLoadingRef.current = true;
      setLoading(true);

      const response = await galleryService.getUploads(page, initialLimit);

      setImages((prevImages) => {
        // Filter out duplicates based on id
        const existingIds = new Set(prevImages.map((img) => img.id));
        const newImages = response.data.filter(
          (img) => !existingIds.has(img.id)
        );
        return [...prevImages, ...newImages];
      });

      // Check if we have more images to load
      setHasMore(response.total > page * initialLimit);
      setPage((prevPage) => prevPage + 1);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Failed to fetch images")
      );
    } finally {
      setLoading(false);
      isLoadingRef.current = false;
    }
  }, [page, initialLimit, hasMore]);

  // Initial fetch when the component mounts
  useEffect(() => {
    fetchImages();
  }, []);

  /**
   * Function to manually trigger loading more images
   * Only loads more if not currently loading and there are more to load
   */
  const loadMore = useCallback(() => {
    if (!loading && hasMore) {
      fetchImages();
    }
  }, [fetchImages, loading, hasMore]);

  return {
    images,
    loading,
    error,
    hasMore,
    loadMore,
  };
}
