import { clearToken, getToken } from "./auth";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.data = data;
  }
}

async function readResponseBody(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getErrorMessage(data, status) {
  if (typeof data === "object" && data && Array.isArray(data.errors) && data.errors.length > 0) {
    const firstError = data.errors[0];

    if (firstError && typeof firstError === "object" && "message" in firstError && typeof firstError.message === "string") {
      return firstError.message;
    }
  }

  if (typeof data === "object" && data && "message" in data && typeof data.message === "string") {
    return data.message;
  }

  if (typeof data === "object" && data && "detail" in data) {
    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const firstError = data.detail[0];

      if (typeof firstError === "string") {
        return firstError;
      }

      if (typeof firstError === "object" && firstError && "msg" in firstError) {
        return firstError.msg;
      }
    }
  }

  return `Request failed with status ${status}`;
}

function unwrapResponseData(data) {
  if (typeof data === "object" && data && "success" in data && "data" in data) {
    return data.data;
  }

  return data;
}

export async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  const isFormData = options.body instanceof FormData;

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (!isFormData && options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await readResponseBody(response);

  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
    }

    throw new APIError(getErrorMessage(data, response.status), response.status, data);
  }

  return unwrapResponseData(data);
}
