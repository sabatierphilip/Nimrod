import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Nimrod AI Trading Assistant", description: "AI market research analyst for educational stock research" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
