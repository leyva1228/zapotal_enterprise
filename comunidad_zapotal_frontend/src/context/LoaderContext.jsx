import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useLocation } from "react-router-dom";

const LoaderContext = createContext(null);

let nextTaskId = 1;

export function LoaderProvider({ children }) {
  const [taskCount, setTaskCount] = useState(0);
  const [routePending, setRoutePending] = useState(false);
  const tasksRef = useRef(new Set());

  const startTask = useCallback((key) => {
    const id = key || `t${nextTaskId++}`;
    tasksRef.current.add(id);
    setTaskCount(tasksRef.current.size);
    return id;
  }, []);

  const endTask = useCallback((id) => {
    if (!id) return;
    tasksRef.current.delete(id);
    setTaskCount(tasksRef.current.size);
  }, []);

  const setRouteLoading = useCallback((value) => {
    setRoutePending(Boolean(value));
  }, []);

  const value = useMemo(
    () => ({
      isLoading: taskCount > 0 || routePending,
      startTask,
      endTask,
      setRouteLoading,
    }),
    [taskCount, routePending, startTask, endTask, setRouteLoading]
  );

  return (
    <LoaderContext.Provider value={value}>{children}</LoaderContext.Provider>
  );
}

export function useLoader() {
  const ctx = useContext(LoaderContext);
  if (!ctx) {
    return {
      isLoading: false,
      startTask: () => "",
      endTask: () => {},
      setRouteLoading: () => {},
    };
  }
  return ctx;
}

export function useTaskLifecycle(key, active) {
  const { startTask, endTask } = useLoader();
  useEffect(() => {
    if (!active) return undefined;
    const id = startTask(key);
    return () => endTask(id);
  }, [active, key, startTask, endTask]);
}

export function RouteChangeListener({ minMs = 300 }) {
  const location = useLocation();
  const { setRouteLoading } = useLoader();
  const [pending, setPending] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setRouteLoading(true);
    setPending(true);
    const t = setTimeout(() => {
      if (cancelled) return;
      setPending(false);
      setRouteLoading(false);
    }, minMs);
    return () => {
      cancelled = true;
      clearTimeout(t);
      setRouteLoading(false);
    };
  }, [location.pathname, minMs, setRouteLoading]);

  return null;
}
