import type { Metadata, Viewport } from "next";
import { Inter, Manrope } from "next/font/google";
import "./globals.css";

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
      <body className="font-sans text-slate-600 bg-gradient-to-br from-blue-50 via-sky-50 to-blue-100 bg-fixed min-h-screen selection:bg-brand-blue/20 selection:text-brand-blue leading-relaxed">
        {children}
      </body>
    </html>
  );
}