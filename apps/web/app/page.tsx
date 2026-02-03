import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <section className="grid gap-8 md:grid-cols-[1.1fr_0.9fr]">
      <div className="space-y-6">
        <h1 className="font-display text-4xl font-semibold text-ink md:text-5xl">
          EventCart demo store
        </h1>
        <p className="text-lg text-slate-600">
          A full-stack order system showing the outbox pattern, idempotency, and async
          fulfillment. Built with FastAPI, Postgres, and Next.js.
        </p>
        <div className="flex gap-3">
          <Link href="/products">
            <Button className="bg-accent hover:bg-accentDark">Browse products</Button>
          </Link>
          <Link href="/register">
            <Button variant="outline">Create account</Button>
          </Link>
        </div>
      </div>
      <Card className="p-6">
        <CardHeader>
          <CardTitle>Demo credentials</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
            <p>Email: demo@eventcart.dev</p>
            <p>Password: Demo1234!</p>
          </div>
          <ul className="mt-6 space-y-2 text-sm text-slate-600">
            <li>Outbox worker confirms fulfillment</li>
            <li>Idempotent checkout with retry-safe key</li>
            <li>JWT access token + refresh cookie</li>
          </ul>
        </CardContent>
      </Card>
    </section>
  );
}
