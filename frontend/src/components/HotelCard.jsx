import React from 'react';
import { MapPin, Star, Wifi, Coffee, Utensils, ArrowRight } from 'lucide-react';

const HotelCard = ({ data, onSelect }) => {
  // Random image generator based on hotel name hash to keep it consistent
  const randomImage = `https://source.unsplash.com/800x600/?hotel,room,${data.name.split(' ')[0]}`;
  // Fallback if Unsplash source is slow, use a static placeholder
  const placeholderImg = "[https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000&auto=format&fit=crop](https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000&auto=format&fit=crop)";

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 group flex flex-col md:flex-row">
      
      {/* IMAGE SECTION */}
      <div className="md:w-1/3 h-48 md:h-auto relative overflow-hidden">
        <img 
          src={placeholderImg} 
          alt={data.name} 
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1 shadow-sm text-slate-800">
          <Star size={12} className="text-yellow-500 fill-yellow-500"/> {data.rating || "4.5"}
        </div>
      </div>

      {/* CONTENT SECTION */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-bold text-slate-900 text-lg leading-tight">{data.name}</h3>
              <div className="flex items-center gap-1 text-slate-500 text-xs mt-1">
                <MapPin size={12} /> {data.location || "City Center"}
              </div>
            </div>
            {/* Price for Mobile (Hidden on Desktop, shown via Flex order if needed, but simplified here) */}
          </div>

          <p className="text-xs text-slate-500 mt-3 line-clamp-2 leading-relaxed">
            {data.description || "Experience luxury and comfort at this top-rated property featuring modern amenities and excellent service."}
          </p>

          {/* AMENITIES PILLS */}
          <div className="flex flex-wrap gap-2 mt-4">
            {(data.amenities || ["Free Wifi", "Breakfast"]).slice(0, 3).map((am, i) => (
              <span key={i} className="px-2 py-1 bg-slate-50 border border-slate-100 rounded-md text-[10px] font-medium text-slate-600 flex items-center gap-1">
                {am.includes("Wifi") && <Wifi size={10}/>}
                {am.includes("Break") && <Coffee size={10}/>}
                {am}
              </span>
            ))}
          </div>
        </div>

        {/* BOTTOM ACTION */}
        <div className="flex items-end justify-between mt-5 pt-4 border-t border-slate-50">
          <div>
            <span className="text-xs text-slate-400 font-medium">Starting from</span>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-black text-slate-900">₹{data.price?.toLocaleString()}</span>
              <span className="text-[10px] text-slate-400">/night</span>
            </div>
          </div>
          
          <button 
            onClick={() => onSelect(data)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all active:scale-95 flex items-center gap-2 shadow-blue-200 shadow-md"
          >
            Book Now <ArrowRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default HotelCard;