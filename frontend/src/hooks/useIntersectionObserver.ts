import { useEffect, useRef, useState } from "react";

interface UseIntersectionObserverProps {
  threshold?: number;
  rootMargin?: string;
  enabled?: boolean;
}

/**
 * Custom hook for intersection observer functionality
 * Useful for implementing lazy loading and infinite scroll optimizations
 */
export function useIntersectionObserver({
  threshold = 0.1,
  rootMargin = "50px",
  enabled = true,
}: UseIntersectionObserverProps = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);
  const targetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!enabled) return;

    const target = targetRef.current;
    if (!target) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isElementIntersecting = entry.isIntersecting;
        setIsIntersecting(isElementIntersecting);

        // Once intersected, keep track for lazy loading
        if (isElementIntersecting && !hasIntersected) {
          setHasIntersected(true);
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(target);

    return () => {
      observer.unobserve(target);
    };
  }, [threshold, rootMargin, enabled, hasIntersected]);

  return {
    targetRef,
    isIntersecting,
    hasIntersected,
  };
}
