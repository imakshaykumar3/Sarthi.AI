import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, Sparkles, Building2, Compass } from 'lucide-react';
import FlightCard from './FlightCard';
import TrainCard from './TrainCard';
import HotelCard from './HotelCard';

// ✅ ROBUST PARSER: Handles Raw JSON, Markdown Blocks, and Plain Text
const extractJson = (content) => {
  if (!content || typeof content !== 'string') return { text: "", data: null };

  // 1. Try parsing the WHOLE string as JSON first
  try {
    const parsed = JSON.parse(content);
    if (parsed.greeting || parsed.flights_section || parsed.trains_section || parsed.hotels_section || parsed.rentals_section || Array.isArray(parsed)) {
       return { text: "", data: parsed };
    }
  } catch (e) {
    // Not raw JSON, proceed to check for markdown blocks
  }

  // 2. Try finding Markdown Code Block (Fallback)
  const jsonMatch = content.match(/([\s\S]*?)```json\s*([\s\S]*?)\s*```/);
  
  if (jsonMatch) {
    try {
      const introText = jsonMatch[1].trim(); 
      const cleanJson = jsonMatch[2].trim(); 
      return { text: introText, data: JSON.parse(cleanJson) };
    } catch (e) { 
      return { text: content, data: null };
    }
  }

  // 3. Fallback: Treat as regular text
  return { text: content, data: null };
};

// Sub-component for clean section headers
const SectionHeader = ({ icon, label, colorClass }) => (
  <div className="flex items-center gap-2 mb-3 ml-1 mt-2">
    <div className={`p-1.5 rounded-lg ${colorClass}`}>
      {icon}
    </div>
    <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
      {label}
    </span>
  </div>
);

const MessageBubble = ({ role, content, onOptionSelect }) => {
  const isUser = role === 'user';
  
  // Local state to track selection visually
  const [selectedId, setSelectedId] = useState(null);

  // Extract data using our robust helper
  const { text, data } = isUser ? { text: content, data: null } : extractJson(content);

  // Helper to handle selection click
  const handleSelection = (item) => {
      const id = item.number || item.id || item.name; 
      setSelectedId(id);
      if (onOptionSelect) onOptionSelect(item);
  };

  // 🔥 THE FIX: Stricter Itinerary Check
  // We ONLY flag as itinerary if it specifically has the Day marker. 
  // This prevents the Final Bill's markdown table (`|---|---|`) from being split into pieces!
  const isItinerary = !isUser && text && text.includes("### 🗓️ Day");

  // Split itinerary into individual cards based on '---' delimiter
  // If it's NOT an itinerary (like the Bill), it stays as one solid block so tables render correctly.
  const itineraryDays = isItinerary ? text.split('---').filter(d => d.trim()) : [text];

  return (
    <div className={`flex w-full mb-8 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
      <div className={`flex w-full max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-4 items-start`}>
        
        {/* Avatar */}
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/20
          ${isUser ? 'bg-indigo-600' : 'bg-emerald-500'}`}>
          {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-white" />}
        </div>

        {/* --- CONTENT CONTAINER --- */}
        <div className="flex-1 flex flex-col gap-6 min-w-0">
            
            {/* 1. TEXT / ITINERARY BUBBLE */}
            {text && (
                <div className="space-y-4">
                  {itineraryDays.map((dayContent, idx) => (
                    <div 
                      key={idx}
                      className={`p-8 rounded-[2rem] shadow-xl border transition-all duration-700 ${
                        isUser 
                        ? 'bg-indigo-600 text-white rounded-tr-none border-indigo-500' 
                        : isItinerary
                          ? 'bg-white/95 backdrop-blur-md rounded-tl-none border-slate-100 hover:shadow-2xl'
                          : 'bg-white/90 backdrop-blur-md rounded-tl-none border-white/50 text-slate-800 shadow-sm'
                      }`}
                    >
                      {/* Premium Header for Bespoke Itineraries - Only on first card */}
                      {!isUser && isItinerary && idx === 0 && (
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
                          <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg shadow-blue-200">
                            <Compass className="w-5 h-5 animate-pulse" />
                          </div>
                          <div>
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-500 block leading-none mb-1">TravelGenie Expert</span>
                            <h2 className="text-lg font-black text-slate-900 leading-none tracking-tight">Your Bespoke Itinerary</h2>
                          </div>
                        </div>
                      )}

                      <div className={`prose max-w-none ${
                          isUser 
                          ? 'prose-invert prose-p:leading-relaxed' 
                          : 'prose-slate prose-headings:text-blue-900 prose-strong:text-blue-700 prose-headings:font-black prose-p:font-medium leading-relaxed'
                      }`}>
                          {/* remarkGfm is required to render Markdown tables */}
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{dayContent.trim()}</ReactMarkdown>
                      </div>

                      {isItinerary && idx === itineraryDays.length - 1 && (
                         <div className="mt-8 pt-4 border-t border-blue-50 flex items-center gap-2 text-xs font-bold text-blue-400 italic">
                            <Sparkles size={14} /> Specially curated for your journey
                         </div>
                      )}
                    </div>
                  ))}
                </div>
            )}

            {/* 2. STRUCTURED DATA (Segmented UI) */}
            {data && !Array.isArray(data) && (
                <div className="flex flex-col gap-4">
                    {/* A. GREETING BUBBLE */}
                    {data.greeting && (
                        <div className="bg-white/90 backdrop-blur-sm p-5 rounded-2xl rounded-tl-none shadow-sm border border-slate-200/60 text-slate-700 text-sm">
                            <span className="font-bold text-lg block mb-2 text-slate-800 flex items-center gap-2">
                                👋 Hello!
                            </span>
                            {data.greeting}
                        </div>
                    )}

                    {/* B. FLIGHT SECTION */}
                    {data.flights_section && (
                        <div className="animate-fade-in delay-100">
                            <SectionHeader 
                              icon={<Sparkles size={14} />} 
                              label="Flight Options" 
                              colorClass="bg-blue-100 text-blue-600" 
                            />
                            
                            {data.flights_section.info && (
                                <div className="bg-blue-50 text-blue-900 text-xs px-4 py-3 rounded-xl mb-4 border border-blue-100 flex items-start gap-2">
                                    <span className="text-lg">✈️</span>
                                    <span className="mt-0.5 font-medium">{data.flights_section.info}</span>
                                </div>
                            )}

                            {Array.isArray(data.flights_section.data) && (
                                <div className="grid gap-4">
                                    {data.flights_section.data.map((flight, idx) => (
                                        <FlightCard 
                                            key={idx} 
                                            flight={flight} 
                                            onSelect={handleSelection} 
                                            isSelected={selectedId === flight.number} 
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* C. TRAIN SECTION */}
                    {data.trains_section && (
                        <div className="animate-fade-in delay-200 pt-4 border-t border-slate-100/50 mt-2">
                             <SectionHeader 
                              icon={<Sparkles size={14} />} 
                              label="Train Options" 
                              colorClass="bg-orange-100 text-orange-600" 
                            />

                            {data.trains_section.info && (
                                <div className="bg-orange-50 text-orange-900 text-xs px-4 py-3 rounded-xl mb-4 border border-orange-100 flex items-start gap-2">
                                    <span className="text-lg">🚆</span>
                                    <span className="mt-0.5 font-medium">{data.trains_section.info}</span>
                                </div>
                            )}

                            {Array.isArray(data.trains_section.data) && (
                                <div className="grid gap-4">
                                    {data.trains_section.data.map((train, idx) => (
                                        <TrainCard 
                                            key={idx} 
                                            train={train} 
                                            onSelect={handleSelection} 
                                            isSelected={selectedId === train.number}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* D. HOTEL SECTION */}
                    {data.hotels_section && (
                        <div className="animate-fade-in delay-300 pt-4 border-t border-slate-100/50 mt-2">
                             <SectionHeader 
                              icon={<Building2 size={14} />} 
                              label="Recommended Stays" 
                              colorClass="bg-emerald-100 text-emerald-600" 
                            />

                            {Array.isArray(data.hotels_section.data) && (
                                <div className="grid gap-4">
                                    {data.hotels_section.data.map((hotel, idx) => (
                                        <HotelCard 
                                            key={idx} 
                                            data={hotel} 
                                            onSelect={handleSelection} 
                                            isSelected={selectedId === hotel.name || selectedId === hotel.id}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* E. RENTALS SECTION */}
                    {data.rentals_section && (
                        <div className="animate-fade-in delay-300 pt-4 border-t border-slate-100/50 mt-2">
                             <SectionHeader 
                              icon={<Compass size={14} />} 
                              label="Local Rentals" 
                              colorClass="bg-purple-100 text-purple-600" 
                            />
                            <div className="grid gap-4">
                                {data.rentals_section.data.map((rental, idx) => (
                                    <div 
                                        key={idx} 
                                        onClick={() => handleSelection(rental)} 
                                        className={`p-4 border rounded-xl cursor-pointer transition-all ${
                                            selectedId === rental.id || selectedId === rental.name
                                                ? "bg-purple-50 border-purple-500 shadow-md transform scale-[1.01]"
                                                : "bg-white hover:shadow-md hover:border-purple-300"
                                        }`}
                                    >
                                        <h4 className="font-bold text-slate-800">{rental.name}</h4>
                                        <p className="text-sm text-slate-500 font-medium">{rental.type} • <span className="font-bold text-slate-700">₹{rental.price}</span>/day</p>
                                        <p className="text-xs text-slate-400 mt-1">Provided by: {rental.provider}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* 3. LEGACY LIST / FLAT ARRAY SUPPORT */}
            {data && Array.isArray(data) && (
               <div className="w-full grid gap-3 mt-1">
                  {data.map((item, idx) => {
                      const id = item.number || item.id || item.name;
                      const isSelected = selectedId === id;
                      if (item.type === 'flight') return <FlightCard key={idx} flight={item} onSelect={handleSelection} isSelected={isSelected} />;
                      if (item.type === 'train') return <TrainCard key={idx} train={item} onSelect={handleSelection} isSelected={isSelected} />;
                      if (item.type === 'hotel' || item.room_type) return <HotelCard key={idx} data={item} onSelect={handleSelection} isSelected={isSelected} />;
                      return null;
                  })}
               </div>
            )}
            
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;