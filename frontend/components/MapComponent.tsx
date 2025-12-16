'use client'

import { useEffect, useRef } from 'react'

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

interface MapComponentProps {
  reports: Report[]
}

export default function MapComponent({ reports }: MapComponentProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const dangerZonesRef = useRef<any[]>([])

  // Get coordinates from report, with fallback to mock if not available
  const getCoordinates = (report: Report) => {
    if (report.latitude !== null && report.longitude !== null) {
      return { lat: report.latitude, lng: report.longitude }
    }
    
    // Fallback: Mock coordinates near San Francisco if geocoding failed
    const baseLat = 37.7749
    const baseLng = -122.4194
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

        // Clear existing danger zones
        dangerZonesRef.current.forEach((zone) => {
          map.removeLayer(zone)
        })
        dangerZonesRef.current = []

        // Collect valid coordinates for bounds calculation
        const validCoords: [number, number][] = []

        // Add markers for each report
        reports.forEach((report) => {
          const coords = getCoordinates(report)
          
          // Skip reports without valid coordinates (unless we have a fallback)
          if (!coords.lat || !coords.lng) {
            return
          }
          
          validCoords.push([coords.lat, coords.lng])
          
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
          
          // Add danger zone for high severity reports
          if (report.severity?.toLowerCase() === 'high' && coords.lat && coords.lng) {
            // Draw a red circle with 500m radius (approximately 0.0045 degrees at equator)
            const dangerZone = L.default.circle([coords.lat, coords.lng], {
              radius: 500, // meters
              color: '#ff0000',
              fillColor: '#ff0000',
              fillOpacity: 0.2,
              weight: 2,
              opacity: 0.6
            })
            
            dangerZone.bindPopup(`
              <div style="color: black;">
                <strong>⚠️ DANGER ZONE</strong><br/>
                ${report.hazard_type || 'High Severity Incident'}<br/>
                <small>Avoid this area</small>
              </div>
            `)
            
            dangerZone.addTo(map)
            dangerZonesRef.current.push(dangerZone)
          }
        })

        // Fit map to show all markers, or center on first marker, or use default
        if (validCoords.length > 0) {
          if (validCoords.length === 1) {
            map.setView(validCoords[0], 15)
          } else {
            const bounds = L.default.latLngBounds(validCoords)
            map.fitBounds(bounds, { padding: [50, 50] })
          }
        }
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

