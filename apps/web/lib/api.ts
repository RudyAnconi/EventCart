const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ProblemDetail = {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  timestamp?: string;
  errors?: Array<{
    loc?: Array<string | number>;
    msg?: string;
    type?: string;
    ctx?: Record<string, unknown>;
  }>;
};

export class ApiError extends Error {
  status: number;
  title?: string;
  detail?: string;
  errors?: ProblemDetail["errors"];

  constructor(message: string, status: number, body?: ProblemDetail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.title = body?.title;
    this.detail = body?.detail;
    this.errors = body?.errors;
  }
}

interface RequestOptions {
  accessToken?: string | null;
  onAccessToken?: (token: string | null) => void;
  headers?: Record<string, string>;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth: RequestOptions = {}
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (auth.accessToken) {
    headers.set("Authorization", `Bearer ${auth.accessToken}`);
  }
  if (auth.headers) {
    Object.entries(auth.headers).forEach(([key, value]) => headers.set(key, value));
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (response.status === 401) {
    const refresh = await fetch(`${baseUrl}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (refresh.ok) {
      const data = (await refresh.json()) as { access_token: string };
      auth.onAccessToken?.(data.access_token);
      return request(path, options, { ...auth, accessToken: data.access_token });
    }
  }

  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    const rawText = await response.text();
    let body: ProblemDetail | undefined;

    if (contentType.includes("application/json") || contentType.includes("problem+json")) {
      try {
        body = JSON.parse(rawText) as ProblemDetail;
      } catch {
        body = undefined;
      }
    }

    const message =
      body?.detail || body?.title || rawText || `Request failed: ${response.status}`;
    throw new ApiError(message, response.status, body);
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string, auth?: RequestOptions) => request<T>(path, {}, auth),
  post: <T>(path: string, body: unknown, auth?: RequestOptions) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }, auth),
};
