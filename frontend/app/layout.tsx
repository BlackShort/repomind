import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/config/theme/theme-provider"

export const metadata: Metadata = {
  title: 'RepoMind — Codebase Intelligence',
  description: 'Ask questions about any GitHub repository using AI',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
