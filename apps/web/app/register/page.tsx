"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/components/auth-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function RegisterPage() {
  const router = useRouter();
  const { setAccessToken } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [loading, setLoading] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const nextFieldErrors: { email?: string; password?: string } = {};
    if (password.trim().length < 8) {
      nextFieldErrors.password = "Password must be at least 8 characters.";
    }
    setFieldErrors(nextFieldErrors);
    if (Object.keys(nextFieldErrors).length > 0) {
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<{ access_token: string }>("/auth/register", {
        email,
        password,
      });
      setAccessToken(data.access_token);
      router.push("/products");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.errors?.length) {
          const passwordError = err.errors.find(
            (entry) => entry.loc?.[1] === "password" || entry.loc?.[0] === "password"
          );
          if (passwordError?.msg) {
            setFieldErrors((prev) => ({ ...prev, password: passwordError.msg }));
          }
        }
        if (err.status === 409 || err.detail?.includes("Email already registered")) {
          setError("That email is already in use. Try logging in instead.");
          return;
        }
        if (err.detail) {
          setError(err.detail);
          return;
        }
      }
      setError("We couldn’t create your account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-md space-y-6">
      <h1 className="font-display text-3xl font-semibold">Create your account</h1>
      <Card className="p-6">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={submit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Email</label>
              <Input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Password</label>
              <Input
                type="password"
                required
                value={password}
                onChange={(event) => {
                  const nextValue = event.target.value;
                  setPassword(nextValue);
                  if (nextValue.trim().length >= 8 && fieldErrors.password) {
                    setFieldErrors((prev) => ({ ...prev, password: undefined }));
                  }
                }}
              />
              <p className="text-xs text-slate-400">Minimum 8 characters.</p>
              {fieldErrors.password && (
                <p className="text-xs text-red-600">{fieldErrors.password}</p>
              )}
            </div>
            {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</p>}
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-accent text-white hover:bg-accentDark"
            >
              {loading ? "Creating..." : "Create account"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
