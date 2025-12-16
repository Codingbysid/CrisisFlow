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
      const response = await fetch('http://127.0.0.1:8000/api/v1/reports/')
      if (response.ok) {
        const data = await response.json()
        setReports(data)
      } else {
        console.error('Failed to fetch reports')
        // Mock data for development if backend isn't running
        setReports([
          {
            id: 1,
            raw_text: 'Fire reported at 5th and Main Street',
            location: '5th and Main Street',
            hazard_type: 'Fire',
            severity: 'High',
            confidence_score: 0.95,
            timestamp: new Date().toISOString(),
            is_verified: false,
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
      // Mock data for development if backend isn't running
      setReports([
        {
          id: 1,
          raw_text: 'Fire reported at 5th and Main Street',
          location: '5th and Main Street',
          hazard_type: 'Fire',
          severity: 'High',
          confidence_score: 0.95,
          timestamp: new Date().toISOString(),
          is_verified: false,
        },
      ])
    }
  }

  return (
    <main className="flex h-screen w-full overflow-hidden">
      {/* Left Sidebar - Report Feed (30% width) */}
      <div className="w-[30%] border-r border-gray-800 overflow-y-auto bg-gray-900">
        <div className="sticky top-0 bg-gray-900 border-b border-gray-800 p-4 z-10">
          <h1 className="text-2xl font-bold text-white">CrisisFlow</h1>
          <p className="text-sm text-gray-400 mt-1">Real-Time Disaster Intelligence</p>
        </div>
        <ReportFeed reports={reports} onRefresh={fetchReports} />
      </div>

      {/* Right Side - Map (70% width) */}
      <div className="w-[70%] bg-gray-950">
        <MapComponent reports={reports} />
      </div>
    </main>
  )
}

