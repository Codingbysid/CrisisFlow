import type { Metadata } from 'next'
import './globals.css'
import './leaflet.css'

export const metadata: Metadata = {
  title: 'CrisisFlow - Real-Time Disaster Intelligence',
  description: 'Real-Time Disaster Intelligence Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black text-white">{children}</body>
    </html>
  )
}

