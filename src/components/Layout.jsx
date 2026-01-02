import Navbar from './Navbar'
import Footer from './Footer'
import Toast from './Toast'
import { ToastProvider } from '../context/ToastContext'

const Layout = ({ children }) => {
  return (
    <ToastProvider>
      <div className="min-h-screen flex flex-col bg-slate-50">
        {/* Sticky Navbar */}
        <Navbar />
        
        {/* Main Content - Centered with max-width and consistent padding */}
        <main className="flex-1">
          <div className="max-w-6xl mx-auto px-6 py-8">
            {children}
          </div>
        </main>
        
        {/* Footer */}
        <Footer />
        
        {/* Toast Notifications */}
        <Toast />
      </div>
    </ToastProvider>
  )
}

export default Layout
