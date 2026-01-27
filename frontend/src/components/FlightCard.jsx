// import React from "react";
// import { Plane, Clock } from "lucide-react";

// const FlightCard = ({ flight, onSelect }) => {
//   // 🛠️ HELPER: Universal Time Extractor
//   const extractTime = (val) => {
//     if (!val) return "--:--";
//     const match = String(val).match(/(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)/);
//     return match ? match[0] : "--:--";
//   };

//   const depTime = extractTime(flight.dep || flight.departure);
//   const arrTime = extractTime(flight.arr || flight.arrival);
  
//   const duration = flight.dur || flight.duration || "--";
//   const flightNum = flight.number || flight.flight_number || "Flight";
//   const airlineName = flight.airline || "Airline";
  
//   // Locations
//   const origin = flight.from_city || flight.origin || "Origin"; 
//   const destination = flight.to_city || flight.destination || "Dest";

//   const formatPrice = (price) => {
//     if (!price || price === "N/A") return "N/A";
//     let cleanString = String(price).replace(/[^0-9.]/g, "");
//     const num = parseInt(cleanString, 10);
//     return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
//   };

//   return (
//     <div className="relative bg-white rounded-2xl shadow-sm border border-slate-200 p-5 hover:shadow-md transition-all duration-300 group mb-4">
      
//       {/* Badge Logic */}
//       {flight.badge && (
//         <div className={`absolute -top-3 left-4 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm 
//           ${flight.badge.includes('Cheapest') ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-blue-100 text-blue-700 border border-blue-200'}
//         `}>
//           {flight.badge}
//         </div>
//       )}

//       <div className="flex flex-col lg:flex-row justify-between items-center gap-6 mt-1">
        
//         {/* --- LEFT: Airline Info --- */}
//         <div className="flex items-center gap-4 w-full lg:w-1/4">
//           <div className="w-12 h-12 bg-slate-50 rounded-xl flex items-center justify-center border border-slate-100 shadow-sm shrink-0">
//              <Plane size={24} className="text-blue-600 transform -rotate-45" />
//           </div>
//           <div className="min-w-0">
//             {/* Airline Name: Large & Clear */}
//             <h3 className="font-bold text-slate-900 text-lg leading-tight">{airlineName}</h3>
            
//             {/* Flight Number: Subtle & Small */}
//             <p className="text-[10px] text-slate-400 font-medium bg-slate-50 px-1.5 py-0.5 rounded-md inline-block mt-1">
//                {flightNum}
//             </p>
//           </div>
//         </div>

//         {/* --- CENTER: Timeline (Fixed Truncation) --- */}
//         <div className="flex-1 flex items-center justify-center w-full lg:w-2/4 px-2 gap-4">
           
//            {/* Departure */}
//            <div className="text-center min-w-[100px]">
//               <p className="text-base font-black text-slate-800 leading-none mb-1.5 whitespace-nowrap">{depTime}</p>
//               <p className="text-xs text-slate-500 font-bold uppercase tracking-wide">
//                 {origin}
//               </p>
//            </div>

//            {/* Graphic Container */}
//            <div className="flex flex-col items-center w-full max-w-[160px] min-w-[120px]">
//               <p className="text-[11px] text-slate-500 font-bold mb-1.5 flex items-center gap-1 whitespace-nowrap">
//                 <Clock size={12} className="text-slate-400"/> {duration}
//               </p>

//               {/* Line Graphic */}
//               <div className="w-full flex items-center gap-2">
//                  <div className="h-[2px] flex-1 bg-slate-300 relative rounded-full">
//                     <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
//                  </div>
//                  <Plane size={14} className="text-blue-500 transform rotate-90 shrink-0" />
//                  <div className="h-[2px] flex-1 bg-slate-300 relative rounded-full">
//                     <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
//                  </div>
//               </div>

//               <p className={`text-[10px] font-bold mt-1.5 whitespace-nowrap px-2 py-0.5 rounded-full ${
//                   flight.stops === 0 || String(flight.details || "").toLowerCase().includes("non-stop") 
//                   ? 'bg-emerald-50 text-emerald-600' 
//                   : 'bg-orange-50 text-orange-600'
//               }`}>
//                  {flight.stops === 0 || String(flight.details || "").toLowerCase().includes("non-stop") ? "Non-stop" : "1 Stop"}
//               </p>
//            </div>

//            {/* Arrival */}
//            <div className="text-center min-w-[100px]">
//               <p className="text-base font-black text-slate-800 leading-none mb-1.5 whitespace-nowrap">{arrTime}</p>
//               <p className="text-xs text-slate-500 font-bold uppercase tracking-wide">
//                 {destination}
//               </p>
//            </div>
//         </div>

//         {/* --- RIGHT: Price & Button --- */}
//         <div className="flex flex-row items-center justify-end w-full lg:w-auto gap-6 lg:pl-6 lg:border-l lg:border-slate-100">
//            <div className="text-right">
//              <h3 className="text-2xl font-black text-slate-900 whitespace-nowrap">{formatPrice(flight.price)}</h3>
//              <p className="text-[10px] text-slate-400 font-medium">per adult</p>
//            </div>
           
//            <button 
//              onClick={() => onSelect(flight)}
//              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-xl transition-all active:scale-95 flex items-center gap-2 shrink-0 shadow-lg shadow-blue-200"
//            >
//              Book Now 
//            </button>
//         </div>

//       </div>
//     </div>
//   );
// };

// export default FlightCard;

// import React from "react";
// import { Plane, Clock, Check } from "lucide-react";

// const FlightCard = ({ flight, onSelect, isSelected }) => {
//   // ... (Keep your existing extractTime / formatPrice helpers here) ...
//   const extractTime = (val) => {
//     if (!val) return "--:--";
//     const match = String(val).match(/(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)/);
//     return match ? match[0] : "--:--";
//   };
//   const depTime = extractTime(flight.dep || flight.departure);
//   const arrTime = extractTime(flight.arr || flight.arrival);
//   const duration = flight.dur || flight.duration || "--";
//   const flightNum = flight.number || flight.flight_number || "Flight";
//   const airlineName = flight.airline || "Airline";
//   const origin = flight.from_city || flight.origin || "Origin"; 
//   const destination = flight.to_city || flight.destination || "Dest";
//   const formatPrice = (price) => {
//     if (!price || price === "N/A") return "N/A";
//     let cleanString = String(price).replace(/[^0-9.]/g, "");
//     const num = parseInt(cleanString, 10);
//     return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
//   };

//   return (
//     <div 
//       className={`relative rounded-2xl p-5 transition-all duration-300 group mb-4 cursor-pointer
//         ${isSelected 
//           ? "bg-blue-50 border-2 border-blue-600 shadow-md transform scale-[1.01]" 
//           : "bg-white border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300"
//         }`}
//       onClick={() => onSelect(flight)}
//     >
      
//       {/* Badge Logic */}
//       {flight.badge && (
//         <div className={`absolute -top-3 left-4 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm 
//           ${flight.badge.includes('Cheapest') ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-blue-100 text-blue-700 border border-blue-200'}
//         `}>
//           {flight.badge}
//         </div>
//       )}

//       {/* Selected Indicator */}
//       {isSelected && (
//           <div className="absolute -top-3 right-4 bg-blue-600 text-white px-3 py-1 rounded-full text-[10px] font-bold flex items-center gap-1 shadow-sm">
//              <Check size={12} /> SELECTED
//           </div>
//       )}

//       <div className="flex flex-col lg:flex-row justify-between items-center gap-6 mt-1">
        
//         {/* --- LEFT: Airline Info --- */}
//         <div className="flex items-center gap-4 w-full lg:w-1/4">
//           <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-sm shrink-0 ${isSelected ? 'bg-white border-blue-200' : 'bg-slate-50 border-slate-100'}`}>
//              <Plane size={24} className="text-blue-600 transform -rotate-45" />
//           </div>
//           <div className="min-w-0">
//             <h3 className="font-bold text-slate-900 text-lg leading-tight">{airlineName}</h3>
//             <p className="text-[10px] text-slate-400 font-medium bg-slate-50 px-1.5 py-0.5 rounded-md inline-block mt-1 border border-slate-100">
//                {flightNum}
//             </p>
//           </div>
//         </div>

//         {/* --- CENTER: Timeline --- */}
//         <div className="flex-1 flex items-center justify-center w-full lg:w-2/4 px-2 gap-4">
//            {/* Dep */}
//            <div className="text-center min-w-[100px]">
//               <p className="text-2xl font-black text-slate-800 leading-none mb-1.5 whitespace-nowrap">{depTime}</p>
//               <p className="text-xs text-slate-500 font-bold uppercase tracking-wide">{origin}</p>
//            </div>
           
//            {/* Graphic */}
//            <div className="flex flex-col items-center w-full max-w-[160px] min-w-[120px]">
//               <p className="text-[11px] text-slate-500 font-bold mb-1.5 flex items-center gap-1 whitespace-nowrap">
//                 <Clock size={12} className="text-slate-400"/> {duration}
//               </p>
//               <div className="w-full flex items-center gap-2">
//                  <div className={`h-[2px] flex-1 relative rounded-full ${isSelected ? 'bg-blue-200' : 'bg-slate-300'}`}></div>
//                  <Plane size={14} className="text-blue-500 transform rotate-90 shrink-0" />
//                  <div className={`h-[2px] flex-1 relative rounded-full ${isSelected ? 'bg-blue-200' : 'bg-slate-300'}`}></div>
//               </div>
//               <p className={`text-[10px] font-bold mt-1.5 whitespace-nowrap px-2 py-0.5 rounded-full ${
//                   flight.stops === 0 || String(flight.details || "").toLowerCase().includes("non-stop") 
//                   ? 'bg-emerald-50 text-emerald-600' : 'bg-orange-50 text-orange-600'
//               }`}>
//                  {flight.stops === 0 || String(flight.details || "").toLowerCase().includes("non-stop") ? "Non-stop" : "1 Stop"}
//               </p>
//            </div>

//            {/* Arr */}
//            <div className="text-center min-w-[100px]">
//               <p className="text-2xl font-black text-slate-800 leading-none mb-1.5 whitespace-nowrap">{arrTime}</p>
//               <p className="text-xs text-slate-500 font-bold uppercase tracking-wide">{destination}</p>
//            </div>
//         </div>

//         {/* --- RIGHT: Price & Button --- */}
//         <div className="flex flex-row items-center justify-end w-full lg:w-auto gap-6 lg:pl-6 lg:border-l lg:border-slate-100">
//            <div className="text-right">
//              <h3 className={`text-2xl font-black whitespace-nowrap ${isSelected ? 'text-blue-700' : 'text-slate-900'}`}>{formatPrice(flight.price)}</h3>
//              <p className="text-[10px] text-slate-400 font-medium">per adult</p>
//            </div>
           
//            <button 
//              onClick={(e) => { e.stopPropagation(); onSelect(flight); }}
//              className={`px-6 py-2.5 text-sm font-bold rounded-xl transition-all active:scale-95 flex items-center gap-2 shrink-0 shadow-lg
//                ${isSelected 
//                  ? "bg-blue-600 text-white shadow-blue-200 hover:bg-blue-700" 
//                  : "bg-blue-100 text-blue-700 hover:bg-blue-200"
//                }`}
//            >
//              {isSelected ? <><Check size={16}/> Selected</> : "Book Now"}
//            </button>
//         </div>

//       </div>
//     </div>
//   );
// };

// export default FlightCard;

import React from "react";
import { Plane, Clock, Check } from "lucide-react";

const extractTime = (val) => {
  if (!val) return "--:--";
  const match = String(val).match(/(\d{1,2}:\d{2})/);
  return match ? match[0] : "--:--";
};

const formatPrice = (price) => {
  if (!price || price === "N/A") return "N/A";
  let cleanString = String(price).replace(/[^0-9.]/g, "");
  const num = parseInt(cleanString, 10);
  return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
};

const FlightCard = ({ flight, onSelect, isSelected }) => {
  const flightNum = flight.number || flight.flight_number || "Unknown";
  
  const depTime = extractTime(flight.dep || flight.departure);
  const arrTime = extractTime(flight.arr || flight.arrival);
  const duration = flight.dur || flight.duration || "--";
  const airlineName = flight.airline || "Airline";
  const origin = flight.from_city || flight.origin || "Origin"; 
  const destination = flight.to_city || flight.destination || "Dest";
  
  const isCheapest = flight.badge?.toLowerCase().includes('cheapest');

  return (
    <div 
      className={`relative rounded-2xl p-5 transition-all duration-300 group mb-4 cursor-pointer border
        ${isSelected 
          ? "bg-blue-50 border-blue-600 shadow-md transform scale-[1.01] ring-1 ring-blue-600" 
          : "bg-white border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300"
        }`}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(flight);
      }}
    >
      
      {/* Badge Logic */}
      {flight.badge && (
        <div className={`absolute -top-3 left-4 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm border
          ${isCheapest 
            ? 'bg-emerald-100 text-emerald-700 border-emerald-200' 
            : 'bg-blue-100 text-blue-700 border-blue-200'}
        `}>
          {flight.badge}
        </div>
      )}

      {/* Selected Indicator */}
      {isSelected && (
          <div className="absolute -top-3 right-4 bg-blue-600 text-white px-3 py-1 rounded-full text-[10px] font-bold flex items-center gap-1 shadow-sm animate-fade-in">
             <Check size={12} strokeWidth={3} /> SELECTED
          </div>
      )}

      <div className="flex flex-col lg:flex-row justify-between items-center gap-6 mt-1">
        
        {/* --- LEFT: Airline Info --- */}
        <div className="flex items-center gap-4 w-full lg:w-1/4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-sm shrink-0 transition-colors
            ${isSelected ? 'bg-white border-blue-200' : 'bg-slate-50 border-slate-100'}`}>
             <Plane size={24} className="text-blue-600 transform -rotate-45" />
          </div>
          <div className="min-w-0">
            <h3 className="font-bold text-slate-900 text-lg leading-tight truncate">{airlineName}</h3>
            <p className="text-[10px] text-slate-500 font-bold bg-slate-100 px-2 py-0.5 rounded-md inline-block mt-1 border border-slate-200 tracking-wide">
               {flightNum}
            </p>
          </div>
        </div>

        {/* --- CENTER: Timeline --- */}
        <div className="flex-1 flex items-center justify-center w-full lg:w-2/4 px-2 gap-4">
           {/* Dep */}
           <div className="text-center min-w-[80px]">
              <p className="text-2xl font-black text-slate-800 leading-none mb-1.5 whitespace-nowrap">{depTime}</p>
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wide truncate max-w-[100px]">{origin}</p>
           </div>
           
           {/* Graphic */}
           <div className="flex flex-col items-center w-full max-w-[160px] min-w-[100px]">
              <p className="text-[11px] text-slate-500 font-bold mb-1.5 flex items-center gap-1 whitespace-nowrap">
                <Clock size={12} className="text-slate-400"/> {duration}
              </p>
              <div className="w-full flex items-center gap-2">
                 <div className={`h-[2px] flex-1 relative rounded-full ${isSelected ? 'bg-blue-300' : 'bg-slate-300'}`}></div>
                 <Plane size={14} className={`transform rotate-90 shrink-0 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                 <div className={`h-[2px] flex-1 relative rounded-full ${isSelected ? 'bg-blue-300' : 'bg-slate-300'}`}></div>
              </div>
              <p className={`text-[10px] font-bold mt-1.5 whitespace-nowrap px-2 py-0.5 rounded-full ${
                  flight.stops === 0 || String(flight.details || "").toLowerCase().includes("non-stop") 
                  ? 'bg-emerald-50 text-emerald-600' : 'bg-orange-50 text-orange-600'
              }`}>
                  {flight.stops === 0 || String(flight.details || "").toLowerCase().includes("non-stop") ? "Non-stop" : "1 Stop"}
              </p>
           </div>

           {/* Arr */}
           <div className="text-center min-w-[80px]">
              <p className="text-2xl font-black text-slate-800 leading-none mb-1.5 whitespace-nowrap">{arrTime}</p>
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wide truncate max-w-[100px]">{destination}</p>
           </div>
        </div>

        {/* --- RIGHT: Price & Button --- */}
        <div className="flex flex-row items-center justify-end w-full lg:w-auto gap-6 lg:pl-6 lg:border-l lg:border-slate-100">
           <div className="text-right">
             <h3 className={`text-2xl font-black whitespace-nowrap ${isSelected ? 'text-blue-700' : 'text-slate-900'}`}>
                {formatPrice(flight.price)}
             </h3>
             <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wide">per adult</p>
           </div>
           
           <button 
             className={`px-6 py-2.5 text-sm font-bold rounded-xl transition-all active:scale-95 flex items-center gap-2 shrink-0 shadow-lg
               ${isSelected 
                 ? "bg-blue-600 text-white shadow-blue-200 hover:bg-blue-700" 
                 : "bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700"
               }`}
           >
             {isSelected ? <><Check size={16} strokeWidth={3}/> Selected</> : "Select"}
           </button>
        </div>

      </div>
    </div>
  );
};

export default FlightCard;