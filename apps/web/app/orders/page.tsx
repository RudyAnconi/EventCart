"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { useAuth } from "@/components/auth-context";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

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

export default function OrdersPage() {
  const { accessToken, setAccessToken } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["orders", accessToken],
    queryFn: () =>
      api.get<Order[]>("/orders", {
        accessToken,
        onAccessToken: setAccessToken,
      }),
    enabled: Boolean(accessToken),
  });

  if (!accessToken) {
    return <p className="text-slate-300">Sign in to view orders.</p>;
  }

  return (
    <section className="space-y-6">
      <h1 className="font-display text-3xl font-semibold">Your orders</h1>
      {isLoading && <p>Loading orders...</p>}
      {error && <p className="text-red-600">Unable to load orders.</p>}
      {data?.length === 0 && (
        <Card className="p-6 text-slate-300">
          <CardContent>No orders yet.</CardContent>
        </Card>
      )}
      <div className="space-y-4">
        {data?.map((order) => (
          <Card key={order.id} className="p-6">
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Order</p>
                <p className="font-semibold">{order.id.slice(0, 8)}</p>
              </div>
              <Badge>{order.status}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">
                ${(order.total_cents / 100).toFixed(2)} • {order.items.length} items
              </p>
              <Link
                href={`/orders/${order.id}`}
                className="text-sm font-semibold text-accent"
              >
                View details
              </Link>
            </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
