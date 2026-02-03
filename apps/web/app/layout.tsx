import "./globals.css";

import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";

import { Providers } from "@/components/Providers";
import { SiteNav } from "@/components/site-nav";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" });

export const metadata: Metadata = {
  title: "EventCart",
  description: "EventCart demo storefront with outbox processing",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable}`}>
      <body className="gradient-bg min-h-screen">
        <Providers>
          <SiteNav />
          <main className="mx-auto w-full max-w-6xl px-6 py-10">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
