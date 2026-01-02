import { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import AOS from 'aos'
import Layout from './components/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Scholarships from './pages/Scholarships'
import Upload from './pages/Upload'

function App() {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      easing: 'ease-out-cubic'
    })
  }, [])

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/scholarships" element={<Scholarships />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Layout>
  )
}

export default App
