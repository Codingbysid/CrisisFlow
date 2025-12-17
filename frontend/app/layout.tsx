import type { Metadata } from 'next'
import './globals.css'
import './leaflet.css'

export const metadata: Metadata = {
  title: 'CrisisFlow - Real-Time Disaster Intelligence',
  description: 'Real-Time Disaster Intelligence Platform',
  keywords: ['disaster', 'emergency', 'crisis', 'intelligence', 'response'],
  authors: [{ name: 'CrisisFlow Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#18453B',
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="bg-black text-white">{children}</body>
    </html>
  )
}
