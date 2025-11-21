import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import "react-tooltip/dist/react-tooltip.css";
import "react-toastify/dist/ReactToastify.css";
import { MainLayout } from "@/components/layout";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Estratega Legal | Titan Group",
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
      <body className={`${geistSans.variable} ${geistMono.variable} relative antialiased h-full select-auto bg-gray-100`}>
        <MainLayout>{children}</MainLayout>
      </body>
    </html>
  );
}
