import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, FileText, Calendar, CheckCircle, AlertCircle, Download } from 'lucide-react'
import axios from 'axios'

export default function DocumentDetail() {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchDocument()
  }, [id])
  
  const fetchDocument = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}`)
      setDocument(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch document:', error)
      setLoading(false)
    }
  }
  
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  if (loading) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    )
  }
  
  if (!document) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Document not found</h2>
          <p className="text-gray-600 mb-6">The document you're looking for doesn't exist.</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }
  
  return (
    <div className="max-w-5xl mx-auto">
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
        <div className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">{document.filename}</h1>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-4 h-4" />
                    {formatDate(document.upload_date)}
                  </div>
                  <div className="flex items-center gap-1.5">
                    {document.status === 'completed' ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-yellow-600" />
                    )}
                    <span className="capitalize">{document.status}</span>
                  </div>
                </div>
              </div>
            </div>
            
            {document.status === 'completed' && (
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Download className="w-4 h-4" />
                Export JSON
              </button>
            )}
          </div>
          
          {document.confidence && (
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-700">Overall Confidence</span>
                <span className="text-2xl font-bold text-gray-900">
                  {(document.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    document.confidence > 0.8 ? 'bg-green-500' :
                    document.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${document.confidence * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
      
      {document.status === 'queued' && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Processing Queued</h3>
          <p className="text-blue-700">Your document is in the queue and will be processed shortly.</p>
        </div>
      )}
      
      {document.error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-1">Processing Error</h3>
              <p className="text-red-700">{document.error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
