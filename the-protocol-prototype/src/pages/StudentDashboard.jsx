import React, { useState } from 'react';
import { PlayCircle, CheckCircle2, Calendar, FileText, Download, User, ArrowLeft, Video, ExternalLink, HelpCircle, Trophy } from 'lucide-react';

export default function StudentDashboard({ onNavigate }) {
  const [selectedVideo, setSelectedVideo] = useState({
    title: "Lesson 2.1: Adhesive Prep Guidelines & Restoration Options",
    duration: "18:45",
    desc: "A detailed clinical lecture on preparation styles for anterior veneers, crown choices, and material selection parameters."
  });

  const modules = [
    {
      title: "Module 1: Esthetics & Preparation Design",
      lessons: [
        { title: "1.1: Veneer Prep Guidelines & Material Selection", duration: "18:45", completed: true, active: true },
        { title: "1.2: Restorations: Anterior Prep Workflows", duration: "15:40", completed: false },
        { title: "1.3: Cementation & Bonding Systems Selection", duration: "22:15", completed: false }
      ]
    },
    {
      title: "Module 2: Business & Case Acceptance",
      lessons: [
        { title: "2.1: Clinical Photography Protocols & Lighting", duration: "14:10", completed: false },
        { title: "2.2: Reconstructive Case Economics & Lab Fee Setting", duration: "19:30", completed: false }
      ]
    }
  ];

  const downloads = [
    { name: "Adhesive Prep Guide Cheat Sheet.pdf", size: "2.4 MB" },
    { name: "Clinical Photography Workflow.pdf", size: "1.8 MB" }
  ];

  return (
    <div className="bg-[#FAF9F5] text-[#3b2c2b] min-h-screen">
      
      {/* Top Banner (Rebranded to George Metz Gold style) */}
      <div className="bg-[#3b2c2b] border-b border-[#E8DADA] py-4 px-6 flex justify-between items-center sticky top-0 z-40 text-white">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => onNavigate('landing')}
            className="p-2 rounded bg-white/5 hover:bg-white/10 transition-colors text-white"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span className="font-bold tracking-wider uppercase text-xs">DR. ROBERT RITTER PORTAL</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 rounded bg-[#ab895b]/20 border border-[#ab895b]/30">
            <span className="w-2 h-2 rounded-full bg-[#ab895b] animate-pulse"></span>
            <span className="text-[10px] font-bold text-[#FAF9F5] uppercase tracking-wider">ACTIVE SYLLABUS</span>
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold">
            <User className="w-4 h-4 text-gray-300" />
            <span className="text-gray-300">Dr. Katherine Pierce</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Lesson Player and Portal Navigation */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Main Video Player (Loads the restoration_intro.mp4!) */}
          <div className="rounded overflow-hidden bg-black border border-[#E8DADA] shadow-md">
            <div className="aspect-video bg-black relative">
              <video 
                key={selectedVideo.title}
                controls 
                className="w-full h-full object-cover"
                poster="/assets/img/dr_ritter.jpg"
              >
                <source src="/assets/img/restoration_intro.mp4" type="video/mp4" />
              </video>
            </div>
            
            <div className="p-6 bg-white">
              <h2 className="text-xl font-serif text-[#3b2c2b] mb-2">{selectedVideo.title}</h2>
              <p className="text-xs text-[#536379] font-light leading-relaxed">{selectedVideo.desc}</p>
              
              <div className="mt-6 flex gap-4">
                <button className="px-5 py-2.5 bg-[#ab895b] text-white font-bold text-[10px] uppercase tracking-wider rounded shadow-sm hover:bg-[#96774e]">
                  Mark Complete & Next
                </button>
                <button className="px-5 py-2.5 bg-white border border-[#E8DADA] text-[#ab895b] text-[10px] font-bold uppercase tracking-wider rounded">
                  Ask Dr. Ritter
                </button>
              </div>
            </div>
          </div>

          {/* Curriculum Lesson List */}
          <div className="p-6 rounded bg-white border border-[#E8DADA]">
            <h3 className="text-sm font-bold uppercase mb-6 flex items-center gap-2 text-[#3b2c2b]">
              <PlayCircle className="w-5 h-5 text-[#ab895b]" />
              Course Syllabus
            </h3>

            <div className="space-y-6">
              {modules.map((mod, idx) => (
                <div key={idx} className="space-y-3">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#ab895b]">{mod.title}</div>
                  <div className="space-y-2">
                    {mod.lessons.map((lesson, lIdx) => (
                      <div 
                        key={lIdx}
                        onClick={() => setSelectedVideo({
                          title: lesson.title,
                          duration: lesson.duration,
                          desc: `Training course lesson content for ${lesson.title}. Master this curriculum section inside your student portal.`
                        })}
                        className={`p-4 rounded flex items-center justify-between cursor-pointer border transition-colors ${
                          lesson.active 
                            ? 'bg-[#FAF9F5] border-[#ab895b] text-[#ab895b]' 
                            : 'bg-white border-[#E8DADA] hover:border-gray-300 text-[#3b2c2b]'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          {lesson.completed ? (
                            <CheckCircle2 className="w-4 h-4 text-[#ab895b] flex-shrink-0" />
                          ) : (
                            <div className="w-4 h-4 rounded-full border border-gray-300 flex-shrink-0" />
                          )}
                          <span className="text-xs font-semibold">{lesson.title}</span>
                        </div>
                        <span className="text-[10px] text-gray-400">{lesson.duration}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Widgets, Webinars, Downloads */}
        <div className="space-y-8">
          
          {/* Progress Tracker Card */}
          <div className="p-6 rounded bg-white border border-[#E8DADA]">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Course Progress</h3>
              <Trophy className="w-5 h-5 text-[#ab895b]" />
            </div>
            <div className="text-3xl font-serif text-[#3b2c2b] mb-2">50%</div>
            <div className="w-full h-2 bg-gray-100 rounded overflow-hidden mb-2">
              <div className="h-full bg-[#ab895b] rounded" style={{ width: '50%' }} />
            </div>
            <div className="text-[10px] text-gray-400">2 of 5 Lessons Completed</div>
          </div>

          {/* Next Live Webinar Widget */}
          <div className="p-6 rounded bg-[#FAF9F5] border border-[#ab895b]/30">
            <div className="flex items-center gap-2 mb-4">
              <span className="px-2 py-0.5 rounded text-[8px] font-bold uppercase bg-[#ab895b] text-white tracking-wider">LIVE</span>
              <span className="text-[9px] font-bold uppercase text-[#ab895b] tracking-wider">Next Diagnosis Webinar</span>
            </div>
            <h4 className="text-sm font-bold uppercase text-[#3b2c2b] mb-2">Treatment Planning Case Review</h4>
            <p className="text-[11px] text-[#536379] font-light mb-4">Upload your clinical cases before the live session for direct diagnostic feedback from Dr. Ritter.</p>
            <div className="flex items-center gap-3 text-xs text-[#3b2c2b] font-medium mb-5">
              <Calendar className="w-4 h-4 text-[#ab895b]" />
              <span>July 28, 2026 — 7:00 PM EST</span>
            </div>
            <button className="w-full py-3 bg-[#ab895b] hover:bg-[#96774e] text-white font-bold text-[10px] uppercase tracking-wider rounded transition-transform hover:scale-102">
              Add to Calendar
            </button>
          </div>

          {/* Portal Downloads Hub */}
          <div className="p-6 rounded bg-white border border-[#E8DADA]">
            <h3 className="text-xs font-bold uppercase mb-4 flex items-center gap-2 text-[#3b2c2b]">
              <FileText className="w-4 h-4 text-[#ab895b]" />
              Course Resources
            </h3>
            <div className="space-y-3">
              {downloads.map((file, idx) => (
                <div key={idx} className="p-3 rounded bg-[#FAF9F5] border border-[#E8DADA] flex items-center justify-between">
                  <div>
                    <div className="text-[11px] font-semibold text-[#3b2c2b] truncate max-w-[150px]">{file.name}</div>
                    <div className="text-[9px] text-gray-400">{file.size}</div>
                  </div>
                  <button className="p-2 rounded bg-white border border-[#E8DADA] hover:bg-[#ab895b] text-gray-400 hover:text-white transition-all">
                    <Download className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
