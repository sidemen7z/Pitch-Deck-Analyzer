import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import DocumentDetail from './pages/DocumentDetail'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/document/:id" element={<DocumentDetail />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
