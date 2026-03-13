import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Explorer",
  description: "Generate API integration guides from documentation URLs",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
