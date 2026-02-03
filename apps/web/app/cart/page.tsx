"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth-context";
import { useCart } from "@/components/cart-context";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function CartPage() {
  const router = useRouter();
  const { items, updateQty, clear, total } = useCart();
  const { accessToken, setAccessToken } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const checkout = async () => {
    setLoading(true);
    setError(null);
    try {
      const idempotencyKey = `idem-${Date.now()}`;
      const response = await api.post<{ id: string }>(
        "/orders",
        {
          items: items.map((item) => ({
            product_id: item.product_id,
            qty: item.qty,
          })),
        },
        {
          accessToken,
          onAccessToken: setAccessToken,
          headers: { "Idempotency-Key": idempotencyKey },
        }
      );
      clear();
      router.push(`/orders/${response.id}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-6">
      <h1 className="font-display text-3xl font-semibold">Your cart</h1>
      {items.length === 0 ? (
        <Card className="p-6 text-slate-600">
          <CardContent>No items yet. Add some tickets.</CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <Card key={item.product_id} className="p-4">
              <CardContent className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="font-semibold">{item.name}</h3>
                  <p className="text-sm text-slate-500">
                    ${(item.price_cents / 100).toFixed(2)} each
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Input
                    type="number"
                    min={0}
                    value={item.qty}
                    className="w-20"
                    onChange={(event) => updateQty(item.product_id, Number(event.target.value))}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => updateQty(item.product_id, 0)}
                  >
                    Remove
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
          <div className="flex items-center justify-between">
            <p className="text-lg font-semibold">Total: ${(total / 100).toFixed(2)}</p>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={clear}>
                Remove all
              </Button>
              <Button
                disabled={loading || !accessToken}
                className="bg-accent hover:bg-accentDark"
                onClick={checkout}
              >
                {loading ? "Creating order..." : "Checkout"}
              </Button>
            </div>
          </div>
          {!accessToken && (
            <p className="text-sm text-slate-600">Sign in to complete checkout.</p>
          )}
          {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</p>}
        </div>
      )}
    </section>
  );
}
