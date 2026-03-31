import React from 'react';
import { MapPin, Star, Wifi, Coffee, Wind, ShieldCheck, ArrowRight, Home, Bed } from 'lucide-react';

const HotelCard = ({ data, onSelect }) => {
  // Use a reliable fallback if image is missing
  const hotelImg = data.image_url || `https://loremflickr.com/800/600/hotel,room/all?lock=${data.name.length}`;

  return (
    <div className="bg-white/90 backdrop-blur-md rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-xl hover:border-blue-300 transition-all duration-500 group flex flex-col md:flex-row mb-5">
      
      {/* LEFT: IMAGE SECTION */}
      <div className="md:w-72 h-48 md:h-auto relative overflow-hidden shrink-0">
        <img 
          src={hotelImg} 
          alt={data.name} 
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-in-out"
        />
        {/* Rating Overlay */}
        <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-md px-2.5 py-1.5 rounded-xl text-xs font-black flex items-center gap-1 shadow-xl text-slate-800 border border-white/50">
          <Star size={14} className="text-yellow-500 fill-yellow-500"/> {data.rating || "4.2"}
        </div>
      </div>

      {/* RIGHT: CONTENT SECTION */}
      <div className="p-6 flex-1 flex flex-col justify-between bg-gradient-to-br from-white to-slate-50/30">
        <div>
          <div className="flex justify-between items-start gap-4">
            <div className="space-y-1">
              {/* Added Room Type Badge above Title */}
              <div className="flex items-center gap-2 mb-1">
                 <span className="text-[10px] font-black bg-blue-100 text-blue-600 px-2 py-0.5 rounded uppercase tracking-wider">
                   {data.room_type || "Standard Stay"}
                 </span>
              </div>
              
              <h3 className="font-black text-slate-900 text-xl tracking-tight leading-tight group-hover:text-blue-700 transition-colors">
                {data.name}
              </h3>
              <div className="flex items-center gap-1.5 text-slate-500 font-bold text-[11px] uppercase tracking-wider">
                <MapPin size={12} className="text-blue-600" /> {data.location || "Prime Location"}
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

          {/* AMENITIES SECTION */}
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
              <span className="text-2xl font-black text-slate-900 tracking-tighter">
                ₹{parseInt(data.price || 0).toLocaleString("en-IN")}
              </span>
              <span className="text-xs text-slate-400 font-bold">/night</span>
            </div>
          </div>
          
          <button 
            onClick={() => onSelect(data)}
            className="bg-blue-600 hover:bg-blue-700 text-white pl-6 pr-4 py-3 rounded-2xl text-sm font-black transition-all active:scale-95 flex items-center gap-3 shadow-[0_10px_20px_-5px_rgba(37,99,235,0.3)] hover:shadow-blue-300 group/btn"
          >
            SELECT STAY 
            <div className="bg-white/20 p-1 rounded-lg group-hover/btn:translate-x-1 transition-transform">
                <ArrowRight size={16} /> 
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HotelCard;