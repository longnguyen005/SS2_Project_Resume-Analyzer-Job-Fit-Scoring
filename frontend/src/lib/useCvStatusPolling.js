import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { apiRequest } from "./api";
import { CV_STATUSES, isTerminalCvStatus, normalizeCvStatusPayload } from "./cvStatusModel";

const DEFAULT_POLL_INTERVAL_MS = 1500;

export function useCvStatusPolling(cvId, options = {}) {
  const { enabled = true, pollIntervalMs = DEFAULT_POLL_INTERVAL_MS, onUnauthorized } = options;
  const timerRef = useRef(null);
  const requestRunRef = useRef(0);
  const [snapshot, setSnapshot] = useState(() => normalizeCvStatusPayload({ status: CV_STATUSES.PENDING }));
  const [message, setMessage] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(Boolean(cvId && enabled));

  const clearPollingTimer = useCallback(() => {
    if (timerRef.current) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const loadStatus = useCallback(async (requestRun = requestRunRef.current) => {
    if (!cvId || !enabled) {
      return;
    }

    try {
      const data = await apiRequest(`/cv/${cvId}/status`);
      if (requestRun !== requestRunRef.current) {
        return;
      }

      const nextSnapshot = normalizeCvStatusPayload(data);
      setSnapshot(nextSnapshot);
      setMessage("");
      setError(null);
      setIsLoading(false);

      if (!isTerminalCvStatus(nextSnapshot.status)) {
        timerRef.current = window.setTimeout(() => loadStatus(requestRun), pollIntervalMs);
      }
    } catch (nextError) {
      if (requestRun !== requestRunRef.current) {
        return;
      }

      setIsLoading(false);
      setError(nextError);

      if (nextError.status === 401) {
        onUnauthorized?.();
        return;
      }

      setMessage(nextError.message || "Unable to retrieve the current analysis status.");
    }
  }, [cvId, enabled, onUnauthorized, pollIntervalMs]);

  useEffect(() => {
    clearPollingTimer();
    const requestRun = requestRunRef.current + 1;
    requestRunRef.current = requestRun;

    if (!cvId || !enabled) {
      setIsLoading(false);
      setSnapshot(normalizeCvStatusPayload({ status: CV_STATUSES.PENDING }));
      setMessage("");
      setError(null);
      return undefined;
    }

    setSnapshot(normalizeCvStatusPayload({ status: CV_STATUSES.PENDING }));
    setMessage("");
    setError(null);
    setIsLoading(true);
    loadStatus(requestRun);

    return () => {
      requestRunRef.current += 1;
      clearPollingTimer();
    };
  }, [clearPollingTimer, cvId, enabled, loadStatus]);

  return useMemo(
    () => ({
      ...snapshot,
      error,
      isLoading,
      message,
      reload: loadStatus,
    }),
    [error, isLoading, loadStatus, message, snapshot],
  );
}
