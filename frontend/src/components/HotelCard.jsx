import React from 'react';
import { MapPin, Star, Wifi, Coffee, Wind, ShieldCheck, ArrowRight, Home, Bed } from 'lucide-react';

/**
 * HotelCard - A "Dumb" Presentation Component
 * Receives enriched data (including Unsplash URLs) from the backend.
 */
const HotelCard = ({ data, onSelect }) => {
  return (
    <div className="bg-white/90 backdrop-blur-md rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-2xl hover:border-blue-300 transition-all duration-500 group flex flex-col md:flex-row mb-6">
      
      {/* LEFT: IMAGE SECTION - Powered by Backend Image Enrichment */}
      <div className="md:w-80 h-60 md:h-auto relative overflow-hidden shrink-0">
        <img 
          src={data.image_url || "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb"} 
          alt={data.name} 
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000 ease-in-out"
          onError={(e) => {
            // Self-healing: if the specific backend URL fails, load a high-quality fallback
            e.target.onerror = null; 
            e.target.src = "https://images.unsplash.com/photo-1571896349842-33c89424de2d";
          }}
        />
        
        {/* Rating Overlay (MakeMyTrip Style) */}
        <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-md px-2.5 py-1.5 rounded-xl text-xs font-black flex items-center gap-1 shadow-xl text-slate-800 border border-white/50">
          <Star size={14} className="text-yellow-500 fill-yellow-500"/> {data.rating || "4.2"}
        </div>

        {/* Room Type Overlay */}
        <div className="absolute bottom-4 left-4">
           <span className="bg-black/60 backdrop-blur-md text-white text-[10px] font-black px-3 py-1.5 rounded-full uppercase tracking-widest border border-white/20">
             {data.room_type || "Standard Stay"}
           </span>
        </div>
      </div>

      {/* RIGHT: CONTENT SECTION */}
      <div className="p-6 flex-1 flex flex-col justify-between bg-gradient-to-br from-white to-slate-50/30">
        <div>
          <div className="flex justify-between items-start gap-4">
            <div className="space-y-1">
              <h3 className="font-black text-slate-900 text-2xl tracking-tight leading-tight group-hover:text-blue-700 transition-colors">
                {data.name}
              </h3>
              <div className="flex items-center gap-1.5 text-blue-600 font-bold text-xs uppercase tracking-wide">
                <MapPin size={14} /> {data.location || "Prime Location"}
              </div>
            </div>
            
            {/* Category Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-slate-100 text-slate-600 rounded-full border border-slate-200 text-[10px] font-black uppercase">
                {data.room_type === "Hostel Bed" ? <Bed size={10} /> : <Home size={10} />} 
                {data.room_type?.includes("Luxury") ? "Premium" : "Economy"}
            </div>
          </div>

          <p className="text-sm text-slate-600 mt-4 line-clamp-2 leading-relaxed font-medium">
            {data.description}
          </p>

          {/* AMENITIES SECTION - Dynamically rendered from Backend list */}
          <div className="flex flex-wrap gap-2 mt-5">
            {data.amenities?.map((am, i) => (
              <span key={i} className="px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-[10px] font-bold text-slate-700 flex items-center gap-1.5 shadow-sm">
                {am.toLowerCase().includes("wifi") && <Wifi size={12} className="text-blue-500"/>}
                {am.toLowerCase().includes("breakfast") && <Coffee size={12} className="text-orange-500"/>}
                {am.toLowerCase().includes("ac") && <Wind size={12} className="text-cyan-500"/>}
                {am.toLowerCase().includes("safe") && <ShieldCheck size={12} className="text-emerald-500"/>}
                {am}
              </span>
            ))}
          </div>
        </div>

        {/* PRICE & ACTION BAR */}
        <div className="flex items-center justify-between mt-6 pt-5 border-t border-slate-200/60">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-black uppercase tracking-widest">
              {data.room_type === "Hostel Bed" ? "Bed starting from" : "Room starting from"}
            </span>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-slate-900 tracking-tighter">
                ₹{parseInt(data.price || 0).toLocaleString("en-IN")}
              </span>
              <span className="text-xs text-slate-400 font-bold">/night</span>
            </div>
          </div>
          
          <button 
            onClick={() => onSelect(data)}
            className="bg-blue-600 hover:bg-blue-700 text-white pl-8 pr-6 py-3.5 rounded-2xl text-sm font-black transition-all active:scale-95 flex items-center gap-3 shadow-lg shadow-blue-200 group/btn"
          >
            SELECT STAY 
            <ArrowRight size={18} className="group-hover/btn:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default HotelCard;