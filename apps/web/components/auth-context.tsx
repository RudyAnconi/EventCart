"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";

interface AuthState {
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("access_token");
    if (stored) {
      setAccessToken(stored);
    }
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      accessToken,
      setAccessToken: (token) => {
        setAccessToken(token);
        if (token) {
          window.localStorage.setItem("access_token", token);
        } else {
          window.localStorage.removeItem("access_token");
        }
      },
      logout: async () => {
        try {
          await api.post("/auth/logout", {}, { accessToken });
        } catch {
          // best-effort logout; clear local auth regardless
        }
        setAccessToken(null);
        window.localStorage.removeItem("access_token");
      },
    }),
    [accessToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("AuthProvider missing");
  }
  return ctx;
}
