import React, { useState } from 'react';
import LandingPage from './pages/LandingPage';
import StudentDashboard from './pages/StudentDashboard';
import { Eye, BookOpen, ExternalLink } from 'lucide-react';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  return (
    <div className="bg-[#090909] text-white min-h-screen relative font-sans">
      
      {/* Top Demo Toggle Bar (Highly strategic for sales presentation) */}
      <div className="bg-[#111] text-xs font-semibold py-2 px-6 flex justify-between items-center border-b border-white/10 relative z-50">
        <div className="flex items-center gap-2">
          <Eye className="w-3.5 h-3.5 text-[#E7FF1A]" />
          <span className="text-gray-400">SALES PRESENTATION PROTOTYPE</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentPage('landing')}
            className={`px-3 py-1 rounded transition-all ${
              currentPage === 'landing' 
                ? 'bg-[#E7FF1A] text-black font-bold' 
                : 'text-gray-400 hover:text-white bg-white/5'
            }`}
          >
            1. Landing Page (Sales)
          </button>
          <button
            onClick={() => setCurrentPage('dashboard')}
            className={`px-3 py-1 rounded transition-all ${
              currentPage === 'dashboard' 
                ? 'bg-[#E7FF1A] text-black font-bold' 
                : 'text-gray-400 hover:text-white bg-white/5'
            }`}
          >
            2. Student Dashboard
          </button>
        </div>
      </div>

      {/* Main Luxury Header */}
      <header className="max-w-6xl mx-auto px-6 py-6 flex justify-between items-center relative z-20">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentPage('landing')}>
          {/* Custom Modern Diagonal Triangle Logo from Current Site */}
          <div className="relative w-8 h-8 bg-white overflow-hidden rounded">
            <div className="absolute bottom-0 left-0 w-0 h-0 border-t-[32px] border-t-[#090909] border-r-[32px] border-r-transparent" />
          </div>
          <span className="font-black text-xl tracking-[0.2em] uppercase">The Protocol</span>
        </div>

        {currentPage === 'landing' && (
          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-400">
            <a href="#register" className="hover:text-white transition-colors">Curriculum</a>
            <a href="#register" className="hover:text-white transition-colors">Dates</a>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className="px-4 py-2 rounded bg-white/5 hover:bg-white/10 text-white font-medium transition-all"
            >
              Sign In
            </button>
          </nav>
        )}
      </header>

      {/* Render selected Page */}
      <main className="relative z-10">
        {currentPage === 'landing' ? (
          <LandingPage onNavigate={setCurrentPage} />
        ) : (
          <StudentDashboard onNavigate={setCurrentPage} />
        )}
      </main>

    </div>
  );
}

export default App;
