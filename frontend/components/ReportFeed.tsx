'use client'

import { AlertTriangle, MapPin, Clock, CheckCircle2, XCircle } from 'lucide-react'
import { useState } from 'react'

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

interface ReportFeedProps {
  reports: Report[]
  onRefresh: () => void
}

export default function ReportFeed({ reports, onRefresh }: ReportFeedProps) {
  const [newReportText, setNewReportText] = useState('')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedImage(file)
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
  }

  const convertImageToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = (error) => reject(error)
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newReportText.trim() && !selectedImage) return

    try {
      let imageBase64 = null
      if (selectedImage) {
        imageBase64 = await convertImageToBase64(selectedImage)
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/reports/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          raw_text: newReportText || 'Image report',
          image_base64: imageBase64
        }),
      })

      if (response.ok) {
        setNewReportText('')
        setSelectedImage(null)
        setImagePreview(null)
        onRefresh()
      } else {
        console.error('Failed to create report')
      }
    } catch (error) {
      console.error('Error creating report:', error)
    }
  }

  const getSeverityColor = (severity: string | null) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'bg-red-500/20 text-red-400 border-red-500/50'
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50'
      case 'low':
        return 'bg-green-500/20 text-green-400 border-green-500/50'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/50'
    }
  }

  const getHazardIcon = (hazardType: string | null) => {
    return <AlertTriangle className="w-5 h-5" />
  }

  return (
    <div className="p-4">
      {/* New Report Form */}
      <form onSubmit={handleSubmit} className="mb-6" aria-label="Report submission form">
        <label htmlFor="report-text" className="sr-only">
          Report text input
        </label>
        <textarea
          id="report-text"
          value={newReportText}
          onChange={(e) => setNewReportText(e.target.value)}
          placeholder="Report a disaster incident... (or upload an image)"
          className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          rows={3}
          aria-label="Report text input"
          aria-required="false"
        />
        
        {/* Image Upload */}
        <div className="mt-2">
          <label htmlFor="image-upload" className="block">
            <span className="sr-only">Choose image</span>
            <input
              id="image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Upload image"
            />
          </label>
          
          {imagePreview && (
            <div className="mt-2 relative">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-32 object-cover rounded-lg"
              />
              <button
                type="button"
                onClick={removeImage}
                className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white rounded-full p-1"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={!newReportText.trim() && !selectedImage}
          className="mt-2 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
          aria-label="Submit report"
          aria-disabled={!newReportText.trim() && !selectedImage}
        >
          Submit Report
        </button>
      </form>

      {/* Reports List */}
      <div className="space-y-4">
        {reports.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No reports yet. Submit a report above.
          </div>
        ) : (
          reports.map((report) => (
            <div
              key={report.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getHazardIcon(report.hazard_type)}
                  <span className="font-semibold text-white">
                    {report.hazard_type || 'Unknown'}
                  </span>
                </div>
                {report.is_verified ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-gray-500" />
                )}
              </div>

              <p className="text-gray-300 text-sm mb-3">{report.raw_text}</p>

              {report.location && (
                <div className="flex items-center gap-2 text-gray-400 text-xs mb-2">
                  <MapPin className="w-4 h-4" />
                  <span>{report.location}</span>
                </div>
              )}

              <div className="flex items-center justify-between mt-3">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(
                    report.severity
                  )}`}
                >
                  {report.severity || 'Unknown'}
                </span>
                <div className="flex items-center gap-2 text-gray-500 text-xs">
                  <Clock className="w-3 h-3" />
                  <span>{new Date(report.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>

              {report.confidence_score && (
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Confidence</span>
                    <span>{(report.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      className="bg-blue-500 h-1.5 rounded-full"
                      style={{ width: `${report.confidence_score * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

