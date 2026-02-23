import type React from "react"
import type { Metadata } from "next"
import { Spline_Sans, Noto_Sans } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const splineSans = Spline_Sans({ 
  subsets: ["latin"],
  variable: '--font-spline',
  weight: ['300', '400', '500', '600', '700']
})

const notoSans = Noto_Sans({ 
  subsets: ["latin"],
  variable: '--font-noto',
  weight: ['300', '400', '500', '600', '700']
})

export const metadata: Metadata = {
  title: "EstateParser - DXF Parser & Industrial Park Designer",
  description:
    "Technical DXF parsing and industrial park design tool with AI-powered layout generation, real-time compliance checking, and advanced visualization",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="vi" suppressHydrationWarning className="dark">
      <body className={`${splineSans.variable} ${notoSans.variable} font-display antialiased`} suppressHydrationWarning>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
