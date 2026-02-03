"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { useCart } from "@/components/cart-context";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Product {
  id: string;
  sku: string;
  name: string;
  price_cents: number;
  stock_qty: number;
}

export default function ProductsPage() {
  const { addItem } = useCart();
  const [justAdded, setJustAdded] = useState<Record<string, number>>({});
  const { data, isLoading, error } = useQuery({
    queryKey: ["products"],
    queryFn: () => api.get<Product[]>("/products"),
  });

  return (
    <section className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-semibold">Tickets</h1>
        <p className="text-slate-600">Reserve your spot. Inventory updates instantly.</p>
      </div>
      {isLoading && <p>Loading products...</p>}
      {error && <p className="text-red-600">Unable to load products.</p>}
      <div className="grid gap-6 md:grid-cols-2">
        {data?.map((product) => (
          <Card key={product.id} className="p-6">
            <CardHeader className="flex items-start justify-between">
              <div>
                <CardTitle>{product.name}</CardTitle>
                <p className="text-sm text-slate-500">SKU {product.sku}</p>
              </div>
              <Badge>{product.stock_qty} left</Badge>
            </CardHeader>
            <CardContent className="flex items-center justify-between">
              <p className="text-lg font-semibold text-ink">
                ${(product.price_cents / 100).toFixed(2)}
              </p>
              <Button
                size="sm"
                className={`${justAdded[product.id] ? "bg-accent hover:bg-accentDark add-pulse" : ""}`}
                onClick={() => {
                  addItem({
                    product_id: product.id,
                    name: product.name,
                    price_cents: product.price_cents,
                    qty: 1,
                  });
                  setJustAdded((prev) => ({ ...prev, [product.id]: Date.now() }));
                  setTimeout(() => {
                    setJustAdded((prev) => {
                      const next = { ...prev };
                      delete next[product.id];
                      return next;
                    });
                  }, 900);
                }}
              >
                {justAdded[product.id] ? "Added!" : "Add to cart"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
