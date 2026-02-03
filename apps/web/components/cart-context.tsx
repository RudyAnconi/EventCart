"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

export interface CartItem {
  product_id: string;
  name: string;
  price_cents: number;
  qty: number;
}

interface CartState {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  updateQty: (productId: string, qty: number) => void;
  clear: () => void;
  total: number;
  totalItems: number;
  bump: number;
}

const CartContext = createContext<CartState | null>(null);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [bump, setBump] = useState(0);

  useEffect(() => {
    const stored = window.localStorage.getItem("eventcart_cart");
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as CartItem[];
        setItems(parsed);
      } catch {
        setItems([]);
      }
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem("eventcart_cart", JSON.stringify(items));
  }, [items]);

  const value = useMemo<CartState>(() => {
    const addItem = (item: CartItem) => {
      setItems((prev) => {
        const existing = prev.find((p) => p.product_id === item.product_id);
        if (existing) {
          return prev.map((p) =>
            p.product_id === item.product_id ? { ...p, qty: p.qty + item.qty } : p
          );
        }
        return [...prev, item];
      });
      setBump((value) => value + 1);
    };

    const updateQty = (productId: string, qty: number) => {
      setItems((prev) =>
        prev
          .map((p) => (p.product_id === productId ? { ...p, qty } : p))
          .filter((p) => p.qty > 0)
      );
    };

    const clear = () => setItems([]);

    const total = items.reduce((sum, item) => sum + item.price_cents * item.qty, 0);
    const totalItems = items.reduce((sum, item) => sum + item.qty, 0);

    return { items, addItem, updateQty, clear, total, totalItems, bump };
  }, [items]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) {
    throw new Error("CartProvider missing");
  }
  return ctx;
}
