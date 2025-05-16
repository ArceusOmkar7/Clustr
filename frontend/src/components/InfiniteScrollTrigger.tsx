import { useEffect, useRef } from "react";

/**
 * Props for the InfiniteScrollTrigger component
 */
interface InfiniteScrollTriggerProps {
  onIntersect: () => void; // Callback function triggered when element is visible
  disabled?: boolean; // Whether to disable the trigger
}

/**
 * Component that triggers a callback when scrolled into view
 * Uses the Intersection Observer API to detect when the element is visible
 * Used for implementing infinite scrolling
 *
 * @param onIntersect - Function to call when the trigger element is visible
 * @param disabled - Set to true to disable the trigger
 */
export function InfiniteScrollTrigger({
  onIntersect,
  disabled = false,
}: InfiniteScrollTriggerProps) {
  // Reference to the DOM element we want to observe
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Skip setup if the trigger is disabled
    if (disabled) return;

    // Create an intersection observer to watch for the element becoming visible
    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        // Call the callback when the element is intersecting (visible)
        if (entry.isIntersecting) {
          onIntersect();
        }
      },
      {
        root: null, // Use the viewport as the root
        rootMargin: "0px", // No margin around the root
        threshold: 0.1, // Trigger when at least 10% of the element is visible
      }
    );

    // Start observing the trigger element
    const currentTrigger = triggerRef.current;
    if (currentTrigger) {
      observer.observe(currentTrigger);
    }

    // Clean up the observer when the component unmounts
    return () => {
      if (currentTrigger) {
        observer.unobserve(currentTrigger);
      }
    };
  }, [onIntersect, disabled]);

  return (
    <div
      ref={triggerRef}
      className="w-full h-10 flex items-center justify-center"
    >
      {/* Show loading spinner when the trigger is active */}
      {!disabled && (
        <div className="w-8 h-8 border-2 border-primary rounded-full border-t-transparent animate-spin" />
      )}
    </div>
  );
}
