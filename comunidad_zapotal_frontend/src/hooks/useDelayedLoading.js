import { useEffect, useState } from "react";

export function useDelayedLoading(loading, delayMs = 300) {
  const [show, setShow] = useState(loading && delayMs === 0);

  useEffect(() => {
    if (!loading) {
      setShow(false);
      return undefined;
    }
    if (delayMs <= 0) {
      setShow(true);
      return undefined;
    }
    const timer = setTimeout(() => setShow(true), delayMs);
    return () => clearTimeout(timer);
  }, [loading, delayMs]);

  return show;
}
