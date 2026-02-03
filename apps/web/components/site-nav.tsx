"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "./auth-context";
import { useCart } from "./cart-context";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

const links = [
  { href: "/products", label: "Shop" },
  { href: "/cart", label: "Cart" },
  { href: "/orders", label: "Orders" },
];

export function SiteNav() {
  const pathname = usePathname();
  const { accessToken, logout } = useAuth();
  const { totalItems, bump } = useCart();

  return (
    <header className="sticky top-0 z-20 border-b border-white/40 bg-white/70 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="font-display text-xl font-semibold text-ink">
          EventCart
        </Link>
        <nav className="flex items-center gap-4">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`relative text-sm font-medium ${
                pathname === link.href ? "text-accent" : "text-slate-600"
              }`}
            >
              {link.label}
              {link.href === "/cart" && totalItems > 0 && (
                <Badge
                  key={bump}
                  className="cart-bump ml-2 bg-ink text-white"
                >
                  {totalItems}
                </Badge>
              )}
            </Link>
          ))}
          {!accessToken ? (
            <Link href="/login">
              <Button size="sm">Sign in</Button>
            </Link>
          ) : (
            <Button variant="outline" size="sm" onClick={() => logout()}>
              Logout
            </Button>
          )}
        </nav>
      </div>
    </header>
  );
}
