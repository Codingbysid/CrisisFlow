'use client'

import { useEffect, useRef } from 'react'

interface Report {
  id: number
  raw_text: string
  location: string | null
  hazard_type: string | null
  severity: string | null
  confidence_score: number | null
  timestamp: string
  is_verified: boolean
}

interface MapComponentProps {
  reports: Report[]
}

export default function MapComponent({ reports }: MapComponentProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])

  // Mock coordinates generator - assigns random coordinates near San Francisco
  const getMockCoordinates = (reportId: number) => {
    // Base coordinates for San Francisco
    const baseLat = 37.7749
    const baseLng = -122.4194
    
    // Add some random variation
    const lat = baseLat + (Math.random() - 0.5) * 0.1
    const lng = baseLng + (Math.random() - 0.5) * 0.1
    
    return { lat, lng }
  }

  useEffect(() => {
    // Dynamically import Leaflet only on client side
    if (typeof window !== 'undefined' && mapRef.current) {
      import('leaflet').then((L) => {
        // Initialize map if not already initialized
        if (!mapInstanceRef.current) {
          const map = L.default.map(mapRef.current!, {
            center: [37.7749, -122.4194], // San Francisco
            zoom: 12,
          })

          // Add OpenStreetMap tile layer
          L.default.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
          }).addTo(map)

          mapInstanceRef.current = map
        }

        const map = mapInstanceRef.current

        // Clear existing markers
        markersRef.current.forEach((marker) => {
          map.removeLayer(marker)
        })
        markersRef.current = []

        // Add markers for each report
        reports.forEach((report) => {
          const coords = getMockCoordinates(report.id)
          
          // Choose marker color based on severity
          let markerColor = 'blue'
          if (report.severity?.toLowerCase() === 'high') {
            markerColor = 'red'
          } else if (report.severity?.toLowerCase() === 'medium') {
            markerColor = 'orange'
          } else if (report.severity?.toLowerCase() === 'low') {
            markerColor = 'green'
          }

          const marker = L.default.marker([coords.lat, coords.lng], {
            icon: L.default.divIcon({
              className: 'custom-marker',
              html: `<div style="
                background-color: ${markerColor};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
              "></div>`,
              iconSize: [20, 20],
            }),
          })

          marker.bindPopup(`
            <div style="color: black;">
              <strong>${report.hazard_type || 'Unknown'}</strong><br/>
              ${report.location || 'Location not specified'}<br/>
              <small>Severity: ${report.severity || 'Unknown'}</small><br/>
              <small>${report.raw_text}</small>
            </div>
          `)

          marker.addTo(map)
          markersRef.current.push(marker)
        })
      })
    }
  }, [reports])

  return (
    <div className="w-full h-full relative">
      <div ref={mapRef} className="w-full h-full" />
      <style jsx global>{`
        .custom-marker {
          background: transparent !important;
          border: none !important;
        }
        .leaflet-container {
          background-color: #1a1a1a;
        }
      `}</style>
    </div>
  )
}

