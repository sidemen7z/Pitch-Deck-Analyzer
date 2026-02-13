import { useState } from 'react'
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()
  
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }
  
  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
      setSuccess(false)
    }
  }
  
  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
      setSuccess(false)
    }
  }
  
  const handleUpload = async () => {
    if (!file) return
    
    setUploading(true)
    setError(null)
    setSuccess(false)
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      setSuccess(true)
      setUploading(false)
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
      setUploading(false)
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Pitch Deck</h1>
        <p className="text-gray-600">Upload your PDF or PowerPoint presentation for analysis</p>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div
          className={`relative border-2 border-dashed rounded-xl p-12 transition-all ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.ppt,.pptx"
            onChange={handleChange}
            disabled={uploading}
          />
          
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <UploadIcon className="w-8 h-8 text-blue-600" />
            </div>
            
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700 font-medium"
            >
              Click to upload
            </label>
            <span className="text-gray-600"> or drag and drop</span>
            
            <p className="text-sm text-gray-500 mt-2">
              PDF, PPT, or PPTX (max 50MB)
            </p>
          </div>
        </div>
        
        {file && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <UploadIcon className="w-4 h-4" />
                    Upload
                  </>
                )}
              </button>
            </div>
          </div>
        )}
        
        {success && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <p className="font-medium text-green-900">Upload successful!</p>
              <p className="text-sm text-green-700">Redirecting to dashboard...</p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div>
              <p className="font-medium text-red-900">Upload failed</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-8 grid grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Supported Formats</h3>
          <p className="text-sm text-gray-600">PDF, PowerPoint (PPT/PPTX)</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">AI-Powered</h3>
          <p className="text-sm text-gray-600">Advanced NLP extraction</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <UploadIcon className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Fast Processing</h3>
          <p className="text-sm text-gray-600">Results in under 60 seconds</p>
        </div>
      </div>
    </div>
  )
}
