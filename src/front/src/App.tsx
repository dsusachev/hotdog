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

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#F7F4EF] flex flex-col">
        <Navbar />
        <main className="flex-1 pb-20 md:pb-0 max-w-5xl mx-auto w-full px-4 py-8">
          <Routes>
            <Route path="/"          element={<HomePage />} />
            <Route path="/upload"    element={<UploadPage />} />
            <Route path="/search"    element={<SearchPage />} />
            <Route path="/recipes"   element={<RecipesPage />} />
            <Route path="/history"   element={<HistoryPage />} />
            <Route path="/feedback"  element={<FeedbackPage />} />
            <Route path="/login"     element={<LoginPage />} />
            <Route path="/register"  element={<RegisterPage />} />
          </Routes>
        </main>
        <Footer />
        <BottomNav />
      </div>
    </Router>
  )
}

export default App
