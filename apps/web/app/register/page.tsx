"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
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
  const [loading, setLoading] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
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
      const message = (err as Error).message;
      setError(
        message.includes("Email already registered")
          ? "That email is already in use. Try logging in instead."
          : "We couldn’t create your account. Please try again."
      );
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
              <label className="text-sm font-medium text-slate-600">Email</label>
              <Input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-600">Password</label>
              <Input
                type="password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>
            {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</p>}
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-accent hover:bg-accentDark"
            >
              {loading ? "Creating..." : "Create account"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
