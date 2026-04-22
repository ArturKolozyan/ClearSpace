import type { Metadata, Viewport } from "next";
import { Inter, Manrope } from "next/font/google";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-inter",
  display: "swap",
});

const manrope = Manrope({
  subsets: ["latin", "cyrillic"],
  variable: "--font-manrope",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ClearSpace | Профессиональный клининг",
  description: "Высококачественные услуги клининга для вашего дома и офиса. Эко-средства, фиксированная цена и гарантия чистоты.",
  metadataBase: new URL(siteUrl),
  alternates: {
    canonical: "/",
  },
  keywords: [
    "клининг",
    "уборка квартир",
    "уборка офиса",
    "профессиональная уборка",
    "клининговая компания",
  ],
  openGraph: {
    title: "ClearSpace | Профессиональный клининг",
    description: "Эко-средства, фиксированная цена и гарантия чистоты для дома и офиса.",
    url: "/",
    siteName: "ClearSpace",
    locale: "ru_RU",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ClearSpace | Профессиональный клининг",
    description: "Профессиональный клининг для дома и офиса.",
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  themeColor: "#38BDF8",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className={`${inter.variable} ${manrope.variable} scroll-smooth`}>
      <body className="font-sans text-slate-600 min-h-screen selection:bg-brand-blue/20 selection:text-brand-blue leading-relaxed">
        {children}
      </body>
    </html>
  );
}