// import React from "react";
// import { Train, ArrowRight } from "lucide-react";

// const TrainCard = ({ train, onSelect }) => {
//   // 🗓️ HELPER: Format Date (e.g., "30 JAN")
//   const formatDate = (dateStr, addedDays = 0) => {
//     if (!dateStr) return "";
//     try {
//       const date = new Date(dateStr);
//       date.setDate(date.getDate() + addedDays);
//       return date.toLocaleDateString("en-US", { day: "numeric", month: "short" }).toUpperCase();
//     } catch (e) {
//       return "";
//     }
//   };

//   // 🚆 HELPER: Running Days (S M T W T F S)
//   const renderRunningDays = () => {
//     const days = [
//       { label: "S", full: "Sun" }, { label: "M", full: "Mon" }, { label: "T", full: "Tue" },
//       { label: "W", full: "Wed" }, { label: "T", full: "Thu" }, { label: "F", full: "Fri" },
//       { label: "S", full: "Sat" },
//     ];
//     const running = (train.run_days || []).map(d => d.substring(0, 3)); 
//     const isDaily = running.length === 0 || train.run_days?.includes("Daily") || train.run_days?.includes("All Days");

//     return (
//       <div className="flex items-center gap-1 mt-1.5">
//         <span className="text-[10px] text-slate-400 font-medium mr-1">Runs on:</span>
//         {days.map((day, idx) => {
//           const isActive = isDaily || running.includes(day.full);
//           return (
//             <span key={idx} className={`text-[9px] font-bold w-4 h-4 flex items-center justify-center rounded-[2px] ${isActive ? "text-emerald-700 bg-emerald-100" : "text-slate-300 bg-slate-50"}`}>
//               {day.label}
//             </span>
//           );
//         })}
//       </div>
//     );
//   };

//   // Duration & Date Logic
//   const durHours = parseInt((train.duration || "0").split("h")[0]) || 0;
//   const daysToAdd = Math.floor(durHours / 24);
//   const depDateDisplay = formatDate(train.travel_date);
//   const arrDateDisplay = formatDate(train.travel_date, daysToAdd || (train.arr < train.dep ? 1 : 0));

//   const formatPrice = (price) => {
//     if (!price || price === "N/A") return "N/A";
//     let cleanString = String(price).replace(/[^0-9.]/g, "");
//     const num = parseInt(cleanString, 10);
//     return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
//   };

//   return (
//     <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-4 hover:shadow-md transition-all group">
      
//       {/* --- TOP SECTION: Split Layout --- */}
//       <div className="flex flex-col md:flex-row justify-between items-start gap-2 mb-3">
        
//         {/* LEFT: Train Info */}
//         <div className="w-full md:w-auto">
//           <div className="flex items-center gap-3">
//              <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center text-orange-600 shrink-0">
//                 <Train size={20} />
//              </div>
//              <div>
//                 <h3 className="font-bold text-slate-900 text-lg leading-tight">
//                   {train.name} 
//                   <span className="ml-2 text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">#{train.number}</span>
//                 </h3>
//                 {renderRunningDays()}
//              </div>
//           </div>
//         </div>

//         {/* RIGHT: Timeline (Time Duration Top Right) */}
//         <div className="flex items-center gap-4 w-full md:w-auto flex-1 md:justify-end border-t md:border-t-0 border-slate-100 pt-4 md:pt-0">
            
//             {/* Departure */}
//             <div className="text-left md:text-right">
//                 <p className="text-base font-black text-slate-800 leading-none">
//                   {train.dep} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{depDateDisplay}</span>
//                 </p>
//                 <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
//                    {train.from_station_name || "New Delhi"} <span className="text-slate-700">({train.from_station_code || "NDLS"})</span>
//                 </p>
//             </div>

//             {/* Duration Graphic */}
//             <div className="flex flex-col items-center px-2 min-w-[80px]">
//                 <p className="text-[10px] text-slate-700 font-bold mb-1">{train.duration}</p>
//                 <div className="w-full h-[2px] bg-slate-300 relative">
//                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
//                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
//                 </div>
//             </div>

//             {/* Arrival */}
//             <div className="text-right md:text-left">
//                 <p className="text-base font-black text-slate-800 leading-none">
//                   {train.arr} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{arrDateDisplay}</span>
//                 </p>
//                 <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
//                    {train.to_station_name || "Dest"} <span className="text-slate-700">({train.to_station_code || "DST"})</span>
//                 </p>
//             </div>
//         </div>

//       </div>

//       {/* --- BOTTOM: Classes --- */}
//       <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide pt-2 border-t border-slate-50">
//         {(train.classes || []).map((cls, idx) => (
//             <button 
//               key={idx}
//               onClick={() => onSelect({ ...train, selected_class: cls })}
//               className="min-w-[140px] border border-slate-200 rounded-xl p-3 text-left hover:border-blue-500 hover:bg-blue-50 transition-all flex flex-col justify-between group/card relative"
//             >
//                <div className="flex justify-between items-center w-full mb-2">
//                   <span className="font-bold text-slate-700 text-sm group-hover/card:text-blue-700">{cls.name}</span>
//                   <span className="font-black text-slate-900 text-lg">{formatPrice(cls.price)}</span>
//                </div>
//                <div className={`text-[11px] font-bold ${String(cls.status || "").includes("WL") ? "text-orange-600" : "text-emerald-600"}`}>
//                   {cls.status || "Available"}
//                </div>
//             </button>
//         ))}
//       </div>

//     </div>
//   );
// };

// export default TrainCard;
// import React from "react";
// import { Train, Check } from "lucide-react";

// const TrainCard = ({ train, onSelect, isSelected }) => {
  
//   // 🗓️ HELPER: Format Date (e.g., "30 JAN")
//   const formatDate = (dateStr, addedDays = 0) => {
//     if (!dateStr) return "";
//     try {
//       const date = new Date(dateStr);
//       date.setDate(date.getDate() + addedDays);
//       return date.toLocaleDateString("en-US", { day: "numeric", month: "short" }).toUpperCase();
//     } catch (e) {
//       return "";
//     }
//   };

//   // 🚆 HELPER: Running Days (S M T W T F S)
//   const renderRunningDays = () => {
//     const days = [
//       { label: "S", full: "Sun" }, { label: "M", full: "Mon" }, { label: "T", full: "Tue" },
//       { label: "W", full: "Wed" }, { label: "T", full: "Thu" }, { label: "F", full: "Fri" },
//       { label: "S", full: "Sat" },
//     ];
//     // Safe access to running days
//     const running = (train.run_days || []).map(d => d.substring(0, 3)); 
//     const isDaily = running.length === 0 || train.run_days?.includes("Daily") || train.run_days?.includes("All Days");

//     return (
//       <div className="flex items-center gap-1 mt-1.5">
//         <span className="text-[10px] text-slate-400 font-medium mr-1">Runs on:</span>
//         {days.map((day, idx) => {
//           const isActive = isDaily || running.includes(day.full);
//           return (
//             <span key={idx} className={`text-[9px] font-bold w-4 h-4 flex items-center justify-center rounded-[2px] ${isActive ? "text-emerald-700 bg-emerald-100" : "text-slate-300 bg-slate-50"}`}>
//               {day.label}
//             </span>
//           );
//         })}
//       </div>
//     );
//   };

//   // Duration & Date Logic
//   const durHours = parseInt((train.duration || "0").split("h")[0]) || 0;
//   const daysToAdd = Math.floor(durHours / 24);
//   const depDateDisplay = formatDate(train.travel_date);
//   const arrDateDisplay = formatDate(train.travel_date, daysToAdd || (train.arr < train.dep ? 1 : 0));

//   const formatPrice = (price) => {
//     if (!price || price === "N/A") return "N/A";
//     let cleanString = String(price).replace(/[^0-9.]/g, "");
//     const num = parseInt(cleanString, 10);
//     return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
//   };

//   return (
//     <div 
//       className={`rounded-xl p-5 mb-4 transition-all group border relative
//         ${isSelected 
//            ? "bg-orange-50 border-orange-500 shadow-md transform scale-[1.01]" 
//            : "bg-white border-slate-200 shadow-sm hover:shadow-md"
//         }`}
//     >

//       {/* Selected Badge (Top Right) */}
//       {isSelected && (
//           <div className="absolute top-0 right-0 bg-orange-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl rounded-tr-xl flex items-center gap-1 shadow-sm z-10">
//              <Check size={12}/> SELECTED
//           </div>
//       )}
      
//       {/* --- TOP SECTION: Split Layout --- */}
//       <div className="flex flex-col md:flex-row justify-between items-start gap-2 mb-3">
        
//         {/* LEFT: Train Info */}
//         <div className="w-full md:w-auto">
//           <div className="flex items-center gap-3">
//              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 shrink-0">
//                 <Train size={20} />
//              </div>
//              <div>
//                 <h3 className="font-bold text-slate-900 text-lg leading-tight">
//                   {train.name} 
//                   <span className="ml-2 text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">#{train.number}</span>
//                 </h3>
//                 {renderRunningDays()}
//              </div>
//           </div>
//         </div>

//         {/* RIGHT: Timeline (Time Duration Top Right) */}
//         <div className="flex items-center gap-4 w-full md:w-auto flex-1 md:justify-end border-t md:border-t-0 border-slate-100 pt-4 md:pt-0">
            
//             {/* Departure */}
//             <div className="text-left md:text-right">
//                 <p className="text-base font-black text-slate-800 leading-none">
//                   {train.dep} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{depDateDisplay}</span>
//                 </p>
//                 <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
//                    {train.from_station_name || "New Delhi"} <span className="text-slate-700">({train.from_station_code || "NDLS"})</span>
//                 </p>
//             </div>

//             {/* Duration Graphic */}
//             <div className="flex flex-col items-center px-2 min-w-[80px]">
//                 <p className="text-[10px] text-slate-700 font-bold mb-1">{train.duration}</p>
//                 <div className="w-full h-[2px] bg-slate-300 relative">
//                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
//                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
//                 </div>
//             </div>

//             {/* Arrival */}
//             <div className="text-right md:text-left">
//                 <p className="text-base font-black text-slate-800 leading-none">
//                   {train.arr} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{arrDateDisplay}</span>
//                 </p>
//                 <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
//                    {train.to_station_name || "Dest"} <span className="text-slate-700">({train.to_station_code || "DST"})</span>
//                 </p>
//             </div>
//         </div>

//       </div>

//       {/* --- BOTTOM: Classes --- */}
//       <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide pt-2 border-t border-slate-50">
//         {(train.classes || []).map((cls, idx) => {
//             // Check if THIS class is the selected one
//             const isClsSelected = isSelected && train.selected_class?.name === cls.name;

//             return (
//             <button 
//               key={idx}
//               onClick={() => onSelect({ ...train, selected_class: cls })}
//               className={`min-w-[140px] border rounded-xl p-3 text-left transition-all flex flex-col justify-between group/card relative
//                 ${isClsSelected 
//                    ? "bg-orange-600 border-orange-600 ring-2 ring-orange-200 text-white" 
//                    : "border-slate-200 hover:border-blue-500 hover:bg-blue-50 bg-white"
//                 }`}
//             >
//                <div className="flex justify-between items-center w-full mb-2">
//                   <span className={`font-bold text-sm ${isClsSelected ? "text-white" : "text-slate-700 group-hover/card:text-blue-700"}`}>
//                     {cls.name}
//                   </span>
//                   <span className={`font-black text-lg ${isClsSelected ? "text-white" : "text-slate-900"}`}>
//                     {formatPrice(cls.price)}
//                   </span>
//                </div>
//                <div className={`text-[11px] font-bold ${isClsSelected ? "text-orange-100" : (String(cls.status || "").includes("WL") ? "text-orange-600" : "text-emerald-600")}`}>
//                   {isClsSelected ? "SELECTED" : (cls.status || "Available")}
//                </div>
//             </button>
//         )})}
//       </div>

//     </div>
//   );
// };

// export default TrainCard;

// import React from "react";
// import { Train, Check } from "lucide-react";

// const formatDate = (dateStr, addedDays = 0) => {
//   if (!dateStr) return "";
//   try {
//     const date = new Date(dateStr);
//     date.setDate(date.getDate() + addedDays);
//     return date.toLocaleDateString("en-US", { day: "numeric", month: "short" }).toUpperCase();
//   } catch (e) {
//     return "";
//   }
// };

// const formatPrice = (price) => {
//   if (!price || price === "N/A") return "N/A";
//   let cleanString = String(price).replace(/[^0-9.]/g, "");
//   const num = parseInt(cleanString, 10);
//   return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
// };

// const TrainCard = ({ train, onSelect, isSelected }) => {
  
//   // 🚆 HELPER: Running Days (S M T W T F S)
//   const renderRunningDays = () => {
//     const days = [
//       { label: "S", full: "Sun" }, { label: "M", full: "Mon" }, { label: "T", full: "Tue" },
//       { label: "W", full: "Wed" }, { label: "T", full: "Thu" }, { label: "F", full: "Fri" },
//       { label: "S", full: "Sat" },
//     ];
//     // Safe access to running days
//     const running = (train.run_days || []).map(d => d.substring(0, 3)); 
//     const isDaily = running.length === 0 || train.run_days?.includes("Daily") || train.run_days?.includes("All Days");

//     return (
//       <div className="flex items-center gap-1 mt-1.5">
//         <span className="text-[10px] text-slate-400 font-medium mr-1">Runs on:</span>
//         {days.map((day, idx) => {
//           const isActive = isDaily || running.includes(day.full);
//           return (
//             <span key={idx} className={`text-[9px] font-bold w-4 h-4 flex items-center justify-center rounded-[2px] ${isActive ? "text-emerald-700 bg-emerald-100" : "text-slate-300 bg-slate-50"}`}>
//               {day.label}
//             </span>
//           );
//         })}
//       </div>
//     );
//   };

//   // Duration & Date Logic
//   const durHours = parseInt((train.duration || "0").split("h")[0]) || 0;
//   const daysToAdd = Math.floor(durHours / 24);
//   const depDateDisplay = formatDate(train.travel_date);
//   const arrDateDisplay = formatDate(train.travel_date, daysToAdd || (train.arr < train.dep ? 1 : 0));

//   return (
//     <div 
//       className={`rounded-xl p-5 mb-4 transition-all group border relative
//         ${isSelected 
//            ? "bg-orange-50 border-orange-500 shadow-md transform scale-[1.01]" 
//            : "bg-white border-slate-200 shadow-sm hover:shadow-md"
//         }`}
//     >

//       {/* Selected Badge (Top Right) */}
//       {isSelected && (
//           <div className="absolute top-0 right-0 bg-orange-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl rounded-tr-xl flex items-center gap-1 shadow-sm z-10">
//              <Check size={12}/> SELECTED
//           </div>
//       )}
      
//       {/* --- TOP SECTION: Split Layout --- */}
//       <div className="flex flex-col md:flex-row justify-between items-start gap-2 mb-3">
        
//         {/* LEFT: Train Info */}
//         <div className="w-full md:w-auto">
//           <div className="flex items-center gap-3">
//              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 shrink-0">
//                 <Train size={20} />
//              </div>
//              <div>
//                 <h3 className="font-bold text-slate-900 text-lg leading-tight">
//                   {train.name} 
//                   <span className="ml-2 text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">#{train.number}</span>
//                 </h3>
//                 {renderRunningDays()}
//              </div>
//           </div>
//         </div>

//         {/* RIGHT: Timeline (Time Duration Top Right) */}
//         <div className="flex items-center gap-4 w-full md:w-auto flex-1 md:justify-end border-t md:border-t-0 border-slate-100 pt-4 md:pt-0">
            
//             {/* Departure */}
//             <div className="text-left md:text-right">
//                 <p className="text-base font-black text-slate-800 leading-none">
//                   {train.dep} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{depDateDisplay}</span>
//                 </p>
//                 <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
//                    {train.from_station_name || "New Delhi"} <span className="text-slate-700">({train.from_station_code || "NDLS"})</span>
//                 </p>
//             </div>

//             {/* Duration Graphic */}
//             <div className="flex flex-col items-center px-2 min-w-[80px]">
//                 <p className="text-[10px] text-slate-700 font-bold mb-1">{train.duration}</p>
//                 <div className="w-full h-[2px] bg-slate-300 relative">
//                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
//                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
//                 </div>
//             </div>

//             {/* Arrival */}
//             <div className="text-right md:text-left">
//                 <p className="text-base font-black text-slate-800 leading-none">
//                   {train.arr} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{arrDateDisplay}</span>
//                 </p>
//                 <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
//                    {train.to_station_name || "Dest"} <span className="text-slate-700">({train.to_station_code || "DST"})</span>
//                 </p>
//             </div>
//         </div>

//       </div>

//       {/* --- BOTTOM: Classes (THE FIX) --- */}
//       <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide pt-2 border-t border-slate-50">
//         {(train.classes || []).map((cls, idx) => {
//             // Check if THIS class is the selected one
//             const isClsSelected = isSelected && train.selected_class?.name === cls.name;

//             return (
//             <button 
//               key={idx}
//               onClick={(e) => {
//                   e.stopPropagation(); // 🚨 Critical: Stop card click from overriding class click
//                   onSelect({ ...train, selected_class: cls })
//               }}
//               // 🚨 NEW STYLING: High visibility orange when selected
//               className={`min-w-[120px] border rounded-xl p-3 text-left transition-all flex flex-col justify-between group/card relative
//                 ${isClsSelected 
//                    ? "bg-orange-600 border-orange-700 shadow-md scale-[1.02] ring-2 ring-orange-200 ring-offset-1 z-10" 
//                    : "border-slate-200 hover:border-blue-400 hover:bg-blue-50 bg-white"
//                 }`}
//             >
//                <div className="flex justify-between items-center w-full mb-2">
//                   <span className={`font-bold text-sm ${isClsSelected ? "text-white" : "text-slate-700"}`}>
//                     {cls.name}
//                   </span>
//                   <span className={`font-black text-lg ${isClsSelected ? "text-white" : "text-slate-900"}`}>
//                     {formatPrice(cls.price)}
//                   </span>
//                </div>
               
//                <div className="flex justify-between items-center">
//                    <div className={`text-[11px] font-bold ${isClsSelected ? "text-orange-100" : (String(cls.status || "").includes("WL") ? "text-red-500" : "text-emerald-600")}`}>
//                       {cls.status || "Available"}
//                    </div>
//                    {/* 🚨 Show checkmark if selected */}
//                    {isClsSelected && <div className="text-white"><Check size={14} strokeWidth={3} /></div>}
//                </div>
//             </button>
//         )})}
//       </div>

//     </div>
//   );
// };

// export default TrainCard;

import React from "react";
import { Train, Check } from "lucide-react";

const formatDate = (dateStr, addedDays = 0) => {
  if (!dateStr) return "";
  try {
    const date = new Date(dateStr);
    date.setDate(date.getDate() + addedDays);
    return date.toLocaleDateString("en-US", { day: "numeric", month: "short" }).toUpperCase();
  } catch (e) {
    return "";
  }
};

const formatPrice = (price) => {
  if (!price || price === "N/A") return "N/A";
  let cleanString = String(price).replace(/[^0-9.]/g, "");
  const num = parseInt(cleanString, 10);
  return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
};

const TrainCard = ({ train, onSelect, isSelected }) => {
  
  // 1. NORMALIZE DATA FIELDS (Backend sends 'departure_time', Frontend expected 'dep')
  const depTime = train.departure_time || train.dep || "--:--";
  const arrTime = train.arrival_time || train.arr || "--:--";
  const fromStation = train.from_station_name || "Origin";
  const fromCode = train.from_station_code || "SRC";
  const toStation = train.to_station_name || "Destination";
  const toCode = train.to_station_code || "DST";

  // 🚆 HELPER: Running Days
  const renderRunningDays = () => {
    const days = [
      { label: "S", full: "Sun" }, { label: "M", full: "Mon" }, { label: "T", full: "Tue" },
      { label: "W", full: "Wed" }, { label: "T", full: "Thu" }, { label: "F", full: "Fri" },
      { label: "S", full: "Sat" },
    ];
    const running = (train.run_days || []).map(d => d.substring(0, 3)); 
    const isDaily = running.length === 0 || train.run_days?.includes("Daily") || train.run_days?.includes("All Days");

    return (
      <div className="flex items-center gap-1 mt-1.5">
        <span className="text-[10px] text-slate-400 font-medium mr-1">Runs on:</span>
        {days.map((day, idx) => {
          const isActive = isDaily || running.includes(day.full);
          return (
            <span key={idx} className={`text-[9px] font-bold w-4 h-4 flex items-center justify-center rounded-[2px] ${isActive ? "text-emerald-700 bg-emerald-100" : "text-slate-300 bg-slate-50"}`}>
              {day.label}
            </span>
          );
        })}
      </div>
    );
  };

  // Duration & Date Logic
  const durHours = parseInt((train.duration || "0").split("h")[0]) || 0;
  const daysToAdd = Math.floor(durHours / 24);
  const depDateDisplay = formatDate(train.travel_date);
  const arrDateDisplay = formatDate(train.travel_date, daysToAdd || (arrTime < depTime ? 1 : 0));

  return (
    <div 
      className={`rounded-xl p-5 mb-4 transition-all group border relative
        ${isSelected 
           ? "bg-orange-50 border-orange-500 shadow-md transform scale-[1.01]" 
           : "bg-white border-slate-200 shadow-sm hover:shadow-md"
        }`}
    >
      {isSelected && (
          <div className="absolute top-0 right-0 bg-orange-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl rounded-tr-xl flex items-center gap-1 shadow-sm z-10">
             <Check size={12}/> SELECTED
          </div>
      )}
      
      <div className="flex flex-col md:flex-row justify-between items-start gap-2 mb-3">
        {/* LEFT: Train Info */}
        <div className="w-full md:w-auto">
          <div className="flex items-center gap-3">
             <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 shrink-0">
                <Train size={20} />
             </div>
             <div>
                <h3 className="font-bold text-slate-900 text-lg leading-tight">
                  {train.name} 
                  <span className="ml-2 text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">#{train.number}</span>
                </h3>
                {renderRunningDays()}
             </div>
          </div>
        </div>

        {/* RIGHT: Timeline */}
        <div className="flex items-center gap-4 w-full md:w-auto flex-1 md:justify-end border-t md:border-t-0 border-slate-100 pt-4 md:pt-0">
            {/* Departure */}
            <div className="text-left md:text-right">
                <p className="text-base font-black text-slate-800 leading-none">
                  {depTime} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{depDateDisplay}</span>
                </p>
                <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
                   {fromStation} <span className="text-slate-500">({fromCode})</span>
                </p>
            </div>

            {/* Graphic */}
            <div className="flex flex-col items-center px-2 min-w-[80px]">
                <p className="text-[10px] text-slate-700 font-bold mb-1">{train.duration}</p>
                <div className="w-full h-[2px] bg-slate-300 relative">
                   <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
                   <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
                </div>
            </div>

            {/* Arrival */}
            <div className="text-right md:text-left">
                <p className="text-base font-black text-slate-800 leading-none">
                  {arrTime} <span className="text-xs font-bold text-slate-700 uppercase ml-0.5">{arrDateDisplay}</span>
                </p>
                <p className="text-xs text-slate-700 font-bold mt-1 uppercase">
                   {toStation} <span className="text-slate-500">({toCode})</span>
                </p>
            </div>
        </div>
      </div>

      {/* Classes */}
      <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide pt-2 border-t border-slate-50">
        {(train.classes || []).map((cls, idx) => {
            const isClsSelected = isSelected && train.selected_class?.name === cls.name;
            return (
            <button 
              key={idx}
              onClick={(e) => {
                  e.stopPropagation(); 
                  onSelect({ ...train, selected_class: cls })
              }}
              className={`min-w-[120px] border rounded-xl p-3 text-left transition-all flex flex-col justify-between group/card relative
                ${isClsSelected 
                  ? "bg-orange-600 border-orange-700 shadow-md scale-[1.02] ring-2 ring-orange-200 ring-offset-1 z-10" 
                  : "border-slate-200 hover:border-blue-400 hover:bg-blue-50 bg-white"
                }`}
            >
               <div className="flex justify-between items-center w-full mb-2">
                  <span className={`font-bold text-sm ${isClsSelected ? "text-white" : "text-slate-700"}`}>
                    {cls.name}
                  </span>
                  <span className={`font-black text-lg ${isClsSelected ? "text-white" : "text-slate-900"}`}>
                    {formatPrice(cls.price)}
                  </span>
               </div>
               
               <div className="flex justify-between items-center">
                   <div className={`text-[11px] font-bold ${isClsSelected ? "text-orange-100" : (String(cls.status || "").includes("WL") ? "text-red-500" : "text-emerald-600")}`}>
                      {cls.status || "Available"}
                   </div>
                   {isClsSelected && <div className="text-white"><Check size={14} strokeWidth={3} /></div>}
               </div>
            </button>
        )})}
      </div>
    </div>
  );
};

export default TrainCard;