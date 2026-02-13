import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Upload, FileText } from 'lucide-react'

export default function Layout({ children }) {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 shadow-sm">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Pitch Deck</h1>
              <p className="text-sm text-gray-500">Analyzer</p>
            </div>
          </div>
          
          <nav className="space-y-2">
            <Link
              to="/"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive('/')
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>Dashboard</span>
            </Link>
            
            <Link
              to="/upload"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive('/upload')
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Upload className="w-5 h-5" />
              <span>Upload</span>
            </Link>
          </nav>
        </div>
        
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <p className="font-medium text-gray-700 mb-1">System Status</p>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>All systems operational</span>
            </div>
          </div>
        </div>
      </aside>
      
      {/* Main content */}
      <main className="ml-64 min-h-screen">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
