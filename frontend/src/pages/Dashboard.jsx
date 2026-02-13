import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileText, TrendingUp, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import axios from 'axios'

export default function Dashboard() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    processing: 0,
    failed: 0
  })
  
  useEffect(() => {
    fetchDocuments()
  }, [])
  
  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/documents/')
      const docs = response.data.documents
      setDocuments(docs)
      
      // Calculate stats
      setStats({
        total: docs.length,
        completed: docs.filter(d => d.status === 'completed').length,
        processing: docs.filter(d => d.status === 'processing' || d.status === 'queued').length,
        failed: docs.filter(d => d.status === 'failed').length
      })
      
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch documents:', error)
      setLoading(false)
    }
  }
  
  const getStatusBadge = (status) => {
    const badges = {
      completed: { bg: 'bg-green-100', text: 'text-green-700', icon: CheckCircle },
      processing: { bg: 'bg-blue-100', text: 'text-blue-700', icon: Loader2 },
      queued: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: Clock },
      failed: { bg: 'bg-red-100', text: 'text-red-700', icon: AlertCircle }
    }
    
    const badge = badges[status] || badges.queued
    const Icon = badge.icon
    
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        <Icon className={`w-3.5 h-3.5 ${status === 'processing' ? 'animate-spin' : ''}`} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }
  
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Overview of your pitch deck analysis</p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          <p className="text-sm text-gray-600 mt-1">Total Documents</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
          <p className="text-sm text-gray-600 mt-1">Completed</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.processing}</p>
          <p className="text-sm text-gray-600 mt-1">Processing</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.failed}</p>
          <p className="text-sm text-gray-600 mt-1">Failed</p>
        </div>
      </div>
      
      {/* Documents Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Recent Documents</h2>
        </div>
        
        {loading ? (
          <div className="p-12 text-center">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">No documents uploaded yet</p>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload your first document
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Upload Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.document_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{doc.filename}</p>
                          <p className="text-sm text-gray-500">{doc.document_id.slice(0, 8)}...</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatDate(doc.upload_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(doc.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {doc.confidence ? (
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                doc.confidence > 0.8 ? 'bg-green-500' :
                                doc.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${doc.confidence * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-700">
                            {(doc.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/document/${doc.document_id}`}
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
