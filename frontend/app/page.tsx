'use client'

import ReportFeed from '@/components/ReportFeed'
import MapComponent from '@/components/MapComponent'
import { useState, useEffect } from 'react'

interface Report {
  id: number
  raw_text: string
  location: string | null
  latitude: number | null
  longitude: number | null
  hazard_type: string | null
  severity: string | null
  confidence_score: number | null
  timestamp: string
  is_verified: boolean
}

export default function Home() {
  const [reports, setReports] = useState<Report[]>([])

  useEffect(() => {
    fetchReports() // Initial fetch
    
    // Poll every 5 seconds for real-time updates
    const interval = setInterval(() => {
      fetchReports()
    }, 5000)
    
    return () => clearInterval(interval) // Cleanup on unmount
  }, [])

  const fetchReports = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/reports/`)
      if (response.ok) {
        const data = await response.json()
        setReports(data)
      } else {
        console.error('Failed to fetch reports')
        // Don't use mock data in production
        if (process.env.NODE_ENV === 'development') {
          setReports([])
        }
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
      // Don't use mock data in production
      if (process.env.NODE_ENV === 'development') {
        setReports([])
      }
    }
  }

  return (
    <main className="flex h-screen w-full overflow-hidden" role="main" aria-label="CrisisFlow dashboard">
      {/* Left Sidebar - Report Feed (30% width) */}
      <aside className="w-[30%] border-r border-gray-800 overflow-y-auto bg-gray-900" aria-label="Report feed">
        <header className="sticky top-0 bg-gray-900 border-b border-gray-800 p-4 z-10">
          <h1 className="text-2xl font-bold text-white">CrisisFlow</h1>
          <p className="text-sm text-gray-400 mt-1">Real-Time Disaster Intelligence</p>
        </header>
        <ReportFeed reports={reports} onRefresh={fetchReports} />
      </aside>

      {/* Right Side - Map (70% width) */}
      <section className="w-[70%] bg-gray-950" aria-label="Map view">
        <MapComponent reports={reports} />
      </section>
    </main>
  )
}

