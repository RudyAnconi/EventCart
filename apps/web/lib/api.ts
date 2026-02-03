const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string, auth?: RequestOptions) => request<T>(path, {}, auth),
  post: <T>(path: string, body: unknown, auth?: RequestOptions) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }, auth),
};
