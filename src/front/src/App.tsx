import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import BottomNav from './components/BottomNav'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import UploadPage from './pages/UploadPage'
import SearchPage from './pages/SearchPage'
import RecipesPage from './pages/RecipesPage'
import HistoryPage from './pages/HistoryPage'
import FeedbackPage from './pages/FeedbackPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ResultPage from './pages/ResultPage'
import NotFoundPage from './pages/NotFoundPage'
import { ToastProvider } from './components/Toast'

const MOCK_RESULT = {
  label: 'Яблоко',
  confidence: 0.91,
  calories: 52,
}

function App() {
  return (
    <Router>
      <ToastProvider>
        <div className="min-h-screen bg-[#F7F4EF] flex flex-col">
          <Navbar />
          <main className="flex-1 pb-20 md:pb-0 max-w-5xl mx-auto w-full px-4 py-8">
            <Routes>
              <Route path="/"            element={<HomePage />} />
              <Route path="/upload"      element={<UploadPage />} />
              <Route path="/search"      element={<SearchPage />} />
              <Route path="/recipes"     element={<RecipesPage />} />
              <Route path="/history"     element={<HistoryPage />} />
              <Route path="/feedback"    element={<FeedbackPage />} />
              <Route path="/login"       element={<LoginPage />} />
              <Route path="/register"    element={<RegisterPage />} />
              <Route path="/result"      element={<ResultPage />} />
              <Route path="/result/demo" element={<ResultPage mockResult={MOCK_RESULT} />} />
              <Route path="*"            element={<NotFoundPage />} />
            </Routes>
          </main>
          <Footer />
          <BottomNav />
        </div>
      </ToastProvider>
    </Router>
  )
}

export default App