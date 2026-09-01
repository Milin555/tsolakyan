import React, { useState } from 'react';
import { ArrowRight, CheckCircle, Shield, Award, Users, BookOpen, Star } from 'lucide-react';

export default function LandingPage({ onNavigate }) {
  const [activeTab, setActiveTab] = useState('clinical');

  const tabs = {
    clinical: {
      title: "CLINICAL EXCELLENCE",
      subtitle: "Full-Mouth Reconstruction & Adhesive Prep Guidelines",
      badge: "Protocol Phase 01",
      description: "Master the exact preparation, design, and adhesive cementation guidelines needed for anterior veneers, crowns, and multi-unit complex cases. Learn clinical photography parameters to capture and document your dentistry to the highest standards without losing valuable chairside time.",
      details: ["Adhesive veneers prep designs", "Advanced occlusion & bite alignment", "Clinical photography configuration"]
    },
    business: {
      title: "BUSINESS STRATEGY",
      subtitle: "Reconstructive Case Economics & Patient Persuasion",
      badge: "Protocol Phase 02",
      description: "Dentistry demands a balance between technical perfection and a highly profitable business model. Learn the psychology of case acceptance for high-ticket restorative treatments, fee-setting structures for long chairside slots, and how to communicate value clearly so patients accept treatment with absolute confidence.",
      details: ["High-ticket case acceptance psychology", "Fee configurations & overhead margins", "Streamlining premium lab communication"]
    }
  };

  return (
    <div className="bg-[#FAF9F5] text-[#3b2c2b] min-h-screen font-sans selection:bg-[#ab895b] selection:text-white antialiased">
      
      {/* Top Banner (Clean luxury gold banner inspired by Synergy Emerge) */}
      <div className="bg-[#3b2c2b] text-white text-center py-2 text-xs font-bold tracking-widest uppercase">
        ANNOUNCING: DR. RITTER'S ADVANCED RESTORATIVE PROTOCOL ONLINE MASTERCLASS
      </div>

      {/* Navigation (Inspired by George A. Metz Kajabi site) */}
      <header className="border-b border-[#E8DADA] bg-white sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate('landing')}>
            <img src="/assets/img/synergy_gold_logo.png" alt="Ritter Synergy Emerge Logo" className="w-10 h-10 object-cover rounded-full" />
            <span className="font-bold text-base tracking-[0.2em] uppercase text-[#3b2c2b]">DR. ROBERT RITTER</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-[11px] font-bold tracking-widest text-[#536379]">
            <a href="#about" className="hover:text-[#ab895b] transition-colors">ABOUT DR. RITTER</a>
            <a href="#masterclass" className="hover:text-[#ab895b] transition-colors">MASTERCLASS</a>
            <a href="#register" className="hover:text-[#ab895b] transition-colors">ENROLL NOW</a>
            <button 
              onClick={() => onNavigate('dashboard')}
              className="px-5 py-2.5 bg-[#ab895b] hover:bg-[#96774e] text-white font-bold tracking-widest transition-transform hover:scale-[1.02] text-[10px] uppercase rounded"
            >
              STUDENT PORTAL
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section (Elegant editorial style matching georgeametz.com) */}
      <section className="bg-white py-24 border-b border-[#E8DADA]">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h5 className="text-[11px] font-bold tracking-[0.25em] text-[#ab895b] uppercase mb-4">
            GREAT CLINICIANS ARE NOT BORN — THEY ARE DEVELOPED
          </h5>
          <h1 className="text-4xl md:text-7xl font-light text-[#3b2c2b] tracking-tight leading-[1.1] mb-8 font-serif">
            Adhesive Prep Guidelines & Reconstructive Case Economics
          </h1>
          <p className="max-w-2xl mx-auto text-base md:text-lg text-[#536379] font-light leading-relaxed mb-12">
            Sharpen your restorative decision-making, strengthen your clinical outcome precision, and practice clinical dentistry with absolute confidence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="#register" 
              className="px-8 py-4 bg-[#ab895b] hover:bg-[#96774e] text-white font-bold uppercase tracking-wider text-xs rounded transition-all shadow-md"
            >
              ENROLL IN MASTERCLASS
            </a>
            <button
              onClick={() => onNavigate('dashboard')}
              className="px-8 py-4 bg-white hover:bg-gray-50 border border-[#ab895b] text-[#ab895b] font-bold uppercase tracking-wider text-xs rounded transition-all"
            >
              EXPLORE STUDENT PORTAL
            </button>
          </div>
        </div>
      </section>

      {/* Main Feature / Scraped Quote Section */}
      <section className="py-20 bg-[#FAF9F5] border-b border-[#E8DADA]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h5 className="text-[10px] font-bold text-[#ab895b] uppercase tracking-[0.2em] mb-4">REAL LEADERS, REAL RESULTS</h5>
          <h2 className="text-2xl md:text-4xl font-serif text-[#3b2c2b] leading-snug mb-6 italic">
            "Your clinical dentistry quality starts long before the case reaches the laboratory."
          </h2>
          <p className="text-sm text-[#536379] leading-relaxed max-w-2xl mx-auto font-light mb-6">
            Establishing clean preparation guidelines, adhesive protocols, and high-definition clinical photography is essential to building an elite restorative practice.
          </p>
          <div className="text-xs font-semibold text-[#ab895b] uppercase tracking-widest">
            DR. ROBERT RITTER — JUPITER, FLORIDA
          </div>
        </div>
      </section>

      {/* About Section / Dr. Robert Ritter Biography */}
      <section id="about" className="py-24 bg-white border-b border-[#E8DADA]">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="text-xs font-bold tracking-[0.2em] text-[#ab895b] uppercase mb-4">CLINICAL DIRECTORY</div>
            <h2 className="text-3xl md:text-5xl font-light text-[#3b2c2b] font-serif uppercase mb-6 leading-tight">
              MEET AND LEARN FROM DR. ROBERT RITTER
            </h2>
            <p className="text-sm text-[#536379] font-light leading-relaxed mb-6">
              Dr Rob Ritter has been practicing for over 27 years, and has amassed thousands of hours of CE, from this he has helped grow a healthy and thriving restorative practice in Jupiter, Fl. He has lectured extensively all of the country for 23 years and has presented internationally as well.
            </p>
            <p className="text-sm text-[#536379] font-light leading-relaxed mb-6">
              He is a Fellow of The American Academy of Esthetic Dentistry and a member of The American Academy of Restorative Dentistry. He is a member of the American Society for Dental Aesthetics and the American Society for Color and Appearance Dentistry. He is a member of the Academy of Cosmetic Dentistry, as well as The American Dental Association.
            </p>
            <div className="grid grid-cols-2 gap-6 pt-4 border-t border-[#E8DADA]">
              <div>
                <div className="text-3xl font-light text-[#ab895b] font-serif mb-1">27+ Years</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Active Clinical Practice</div>
              </div>
              <div>
                <div className="text-3xl font-light text-[#3b2c2b] font-serif mb-1">23 Years</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Dental Lecturer & Speaker</div>
              </div>
            </div>
          </div>
          <div className="relative p-3 bg-white border border-[#E8DADA] rounded shadow-sm">
            <img 
              src="/assets/img/dr_ritter.jpg" 
              alt="Dr. Robert Ritter" 
              className="w-full aspect-[4/5] object-cover rounded" 
            />
          </div>
        </div>
      </section>

      {/* Tabs Course Overview Section (Synergy Emerge Styling) */}
      <section id="masterclass" className="py-24 bg-[#FAF9F5] border-b border-[#E8DADA]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-5xl font-light text-[#3b2c2b] font-serif uppercase mb-4">MASTERCLASS OVERVIEW</h2>
            <p className="text-sm text-[#536379] font-light">Explore the specific clinical and strategic outcomes covered in this online curriculum.</p>
          </div>

          <div className="flex justify-center border-b border-[#E8DADA] mb-12 max-w-md mx-auto">
            {Object.keys(tabs).map((key) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex-1 py-4 text-center text-[10px] font-bold uppercase tracking-widest transition-all border-b-2 ${
                  activeTab === key 
                    ? 'border-[#ab895b] text-[#ab895b]' 
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                {tabs[key].title}
              </button>
            ))}
          </div>

          <div className="bg-white border border-[#E8DADA] rounded p-8 md:p-12 max-w-3xl mx-auto shadow-sm">
            <span className="text-[10px] font-bold text-[#ab895b] uppercase tracking-wider mb-2 block">{tabs[activeTab].badge}</span>
            <h3 className="text-2xl font-serif text-[#3b2c2b] mb-4">{tabs[activeTab].subtitle}</h3>
            <p className="text-sm text-[#536379] font-light leading-relaxed mb-6">{tabs[activeTab].description}</p>
            <div className="border-t border-[#E8DADA] pt-6">
              <span className="text-[10px] font-bold text-[#3b2c2b] uppercase tracking-wider mb-4 block">Core Outcomes:</span>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {tabs[activeTab].details.map((detail, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-xs text-[#536379] font-light">
                    <CheckCircle className="w-4 h-4 text-[#ab895b]" />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Enrollment Section (Synergy Emerge Card Layout) */}
      <section id="register" className="py-24 bg-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-5xl font-light text-[#3b2c2b] font-serif uppercase mb-6">SECURE YOUR MASTERCLASS ACCESS</h2>
          <p className="text-sm text-[#536379] font-light leading-relaxed max-w-xl mx-auto mb-12">
            Get lifetime digital access to the online preparatory syllabus, clinical videos library, resources sheets, and live webinar diagnostic reviews.
          </p>

          <div className="border border-[#E8DADA] bg-[#FAF9F5] rounded-xl p-8 max-w-md mx-auto shadow-sm text-left">
            <h4 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-2">COMPLETE PORTAL</h4>
            <h3 className="text-2xl font-serif text-[#3b2c2b] mb-4">Online Preparatory Residency</h3>
            <div className="text-3xl font-light text-[#ab895b] mb-6 font-serif">$5,495.00 <span className="text-[10px] text-gray-400 uppercase tracking-widest font-sans font-bold">USD</span></div>
            <ul className="space-y-3 text-xs text-[#536379] font-light mb-8">
              <li className="flex items-center gap-3"><CheckCircle className="w-4 h-4 text-[#ab895b]" /> Lifetime digital portal access</li>
              <li className="flex items-center gap-3"><CheckCircle className="w-4 h-4 text-[#ab895b]" /> Direct clinical video library</li>
              <li className="flex items-center gap-3"><CheckCircle className="w-4 h-4 text-[#ab895b]" /> Monthly diagnostics webinar invitation</li>
            </ul>
            <button className="w-full py-4 bg-[#ab895b] hover:bg-[#96774e] text-white font-bold uppercase tracking-wider text-xs rounded transition-all shadow-md">
              ENROLL ONLINE NOW
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#E8DADA] bg-[#3b2c2b] text-white py-12 text-center text-xs tracking-widest uppercase">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-[#FAF9F5]">
          <div>© {new Date().getFullYear()} DR. ROBERT RITTER. ALL RIGHTS RESERVED.</div>
          <div className="flex gap-8">
            <a href="#" className="hover:text-[#ab895b] transition-colors">PRIVACY POLICY</a>
            <a href="#" className="hover:text-[#ab895b] transition-colors">TERMS OF USE</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
