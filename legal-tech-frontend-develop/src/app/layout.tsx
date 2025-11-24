import type { Metadata } from "next";
import { Inter, Merriweather } from "next/font/google";
import "./globals.css";
import "react-tooltip/dist/react-tooltip.css";
import "react-toastify/dist/ReactToastify.css";
import { MainLayout } from "@/components/layout";

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const merriweather = Merriweather({
  subsets: ['latin'],
  variable: '--font-merriweather',
  weight: ['300', '400', '700', '900'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "Estratega Legal",
  description: "Generador de estrategias legales potenciado por IA",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full">
      <head>
        <meta name="theme-color" content="#FFFFFF"/>
        <meta name="mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-status-bar-style" content="default"/>
      </head>
      <body className={`${inter.variable} ${merriweather.variable} font-sans antialiased h-full select-auto bg-light-gray text-charcoal-gray leading-relaxed`}>
        <div className="h-full">
          <MainLayout>{children}</MainLayout>
        </div>
      </body>
    </html>
  );
}
