"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { useAuth } from "@/components/auth-context";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface OrderItem {
  id: string;
  product_id: string;
  qty: number;
  unit_price_cents: number;
}

interface Order {
  id: string;
  status: string;
  total_cents: number;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params.id as string;
  const { accessToken, setAccessToken } = useAuth();
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () =>
      api.get<Order>(`/orders/${orderId}`, {
        accessToken,
        onAccessToken: setAccessToken,
      }),
    enabled: Boolean(accessToken && orderId),
  });

  const payNow = async () => {
    setPaying(true);
    setError(null);
    try {
      await api.post(`/payments/confirm/${orderId}`, {}, { accessToken, onAccessToken: setAccessToken });
      await refetch();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPaying(false);
    }
  };

  if (!accessToken) {
    return <p className="text-slate-600">Sign in to view this order.</p>;
  }

  return (
    <section className="space-y-6">
      {isLoading && <p>Loading order...</p>}
      {data && (
        <div className="space-y-4">
          <Card className="p-6">
            <CardHeader>
              <CardTitle>Order {data.id.slice(0, 8)}</CardTitle>
              <p className="text-sm text-slate-500">Status: {data.status}</p>
              <p className="text-lg font-semibold">
                Total ${(data.total_cents / 100).toFixed(2)}
              </p>
            </CardHeader>
          </Card>
          <Card className="p-6">
            <CardHeader>
              <CardTitle>Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {data.items.map((item) => (
                <div key={item.id} className="flex items-center justify-between text-sm">
                  <span>{item.product_id.slice(0, 8)}</span>
                  <span>
                    {item.qty} x ${(item.unit_price_cents / 100).toFixed(2)}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
          {data.status === "PENDING_PAYMENT" && (
            <Button
              disabled={paying}
              className="bg-accent hover:bg-accentDark"
              onClick={payNow}
            >
              {paying ? "Processing..." : "Pay now"}
            </Button>
          )}
          {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</p>}
        </div>
      )}
    </section>
  );
}
