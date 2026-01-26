// import React from 'react';
// import ReactMarkdown from 'react-markdown';
// import remarkGfm from 'remark-gfm';
// import { Bot, User, Sparkles } from 'lucide-react';
// import FlightCard from './FlightCard';
// import TrainCard from './TrainCard';

// // ✅ ROBUST PARSER: Handles Raw JSON, Markdown Blocks, and Plain Text
// const extractJson = (content) => {
//   if (!content || typeof content !== 'string') return { text: "", data: null };

//   // 1. Try parsing the WHOLE string as JSON first (New Backend Behavior)
//   try {
//     const parsed = JSON.parse(content);
//     // Validation: Ensure it looks like our payload (has specific keys or is a list)
//     if (parsed.greeting || parsed.flights_section || parsed.trains_section || Array.isArray(parsed)) {
//        return { text: "", data: parsed };
//     }
//   } catch (e) {
//     // Not raw JSON, proceed to check for markdown blocks
//   }

//   // 2. Try finding Markdown Code Block (Fallback)
//   const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
//   if (jsonMatch) {
//     try {
//       const cleanJson = jsonMatch[1].trim();
//       return { 
//         // Remove the JSON block from the text so we don't show raw code
//         text: content.replace(jsonMatch[0], "").trim(), 
//         data: JSON.parse(cleanJson) 
//       };
//     } catch (e) { 
//       console.error("Block Parse Failed", e); 
//     }
//   }

//   // 3. Fallback: Treat as regular text
//   return { text: content, data: null };
// };

// const MessageBubble = ({ role, content, onOptionSelect }) => {
//   const isUser = role === 'user';
  
//   // Extract data using our robust helper
//   const { text, data } = isUser ? { text: content, data: null } : extractJson(content);

//   return (
//     <div className={`flex w-full mb-8 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
//       <div className={`flex w-full max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-4 items-start`}>
        
//         {/* Avatar */}
//         <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/20
//           ${isUser ? 'bg-indigo-600' : 'bg-emerald-500'}`}>
//           {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-white" />}
//         </div>

//         {/* --- CONTENT CONTAINER --- */}
//         <div className="flex-1 flex flex-col gap-6 min-w-0">
            
//             {/* 1. TEXT ONLY (Fallback or standard chat) */}
//             {text && (
//                 <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${
//                     isUser 
//                     ? 'bg-indigo-600 text-white rounded-tr-none' 
//                     : 'bg-white/90 backdrop-blur-md rounded-tl-none border border-white/50 text-slate-800'
//                 }`}>
//                     <div className={`prose ${isUser ? 'prose-invert' : 'prose-slate'} max-w-none`}>
//                         <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
//                     </div>
//                 </div>
//             )}

//             {/* 2. STRUCTURED DATA (The New Segmented UI) */}
//             {data && !Array.isArray(data) && (
//                 <>
//                     {/* A. GREETING BUBBLE */}
//                     {data.greeting && (
//                         <div className="bg-white/90 backdrop-blur-sm p-5 rounded-2xl rounded-tl-none shadow-sm border border-slate-200/60 text-slate-700 text-sm">
//                             <span className="font-bold text-lg block mb-2 text-slate-800 flex items-center gap-2">
//                                 👋 Hello!
//                             </span>
//                             {data.greeting}
//                         </div>
//                     )}

//                     {/* B. FLIGHT SECTION */}
//                     {data.flights_section && (
//                         <div className="animate-fade-in delay-100">
//                             {/* Section Header */}
//                             <div className="flex items-center gap-2 mb-3 ml-1">
//                                 <div className="bg-blue-100 p-1.5 rounded-lg text-blue-600">
//                                     <Sparkles size={14} />
//                                 </div>
//                                 <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
//                                     Flight Options
//                                 </span>
//                             </div>
                            
//                             {/* Context Info Box */}
//                             {data.flights_section.info && (
//                                 <div className="bg-blue-50 text-blue-900 text-xs px-4 py-3 rounded-xl mb-4 border border-blue-100 flex items-start gap-2">
//                                     <span className="text-lg">✈️</span>
//                                     <span className="mt-0.5">{data.flights_section.info}</span>
//                                 </div>
//                             )}

//                             {/* Cards Grid */}
//                             <div className="grid gap-4">
//                                 {data.flights_section.data.map((flight, idx) => (
//                                     <FlightCard key={idx} flight={flight} onSelect={onOptionSelect} />
//                                 ))}
//                             </div>
//                         </div>
//                     )}

//                     {/* C. TRAIN SECTION */}
//                     {data.trains_section && (
//                         <div className="animate-fade-in delay-200 pt-4 border-t border-slate-100/50 mt-2">
//                              {/* Section Header */}
//                              <div className="flex items-center gap-2 mb-3 ml-1">
//                                 <div className="bg-orange-100 p-1.5 rounded-lg text-orange-600">
//                                     <Sparkles size={14} />
//                                 </div>
//                                 <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
//                                     Train Options
//                                 </span>
//                             </div>

//                             {/* Context Info Box */}
//                             {data.trains_section.info && (
//                                 <div className="bg-orange-50 text-orange-900 text-xs px-4 py-3 rounded-xl mb-4 border border-orange-100 flex items-start gap-2">
//                                     <span className="text-lg">🚆</span>
//                                     <span className="mt-0.5">{data.trains_section.info}</span>
//                                 </div>
//                             )}

//                             {/* Cards Grid */}
//                             <div className="grid gap-4">
//                                 {data.trains_section.data.map((train, idx) => (
//                                     <TrainCard key={idx} train={train} onSelect={onOptionSelect} />
//                                 ))}
//                             </div>
//                         </div>
//                     )}
//                 </>
//             )}

//             {/* 3. LEGACY LIST SUPPORT (If backend sends simple array) */}
//             {data && Array.isArray(data) && (
//                <div className="w-full grid gap-3 mt-1">
//                   {data.map((item, idx) => {
//                       if (item.type === 'flight') return <FlightCard key={idx} flight={item} onSelect={onOptionSelect} />;
//                       if (item.type === 'train') return <TrainCard key={idx} train={item} onSelect={onOptionSelect} />;
//                       return null;
//                   })}
//                </div>
//             )}
            
//         </div>
//       </div>
//     </div>
//   );
// };

// export default MessageBubble;

// import React, { useState } from 'react';
// import ReactMarkdown from 'react-markdown';
// import remarkGfm from 'remark-gfm';
// import { Bot, User, Sparkles } from 'lucide-react';
// import FlightCard from './FlightCard';
// import TrainCard from './TrainCard';

// // ✅ ROBUST PARSER: Handles Raw JSON, Markdown Blocks, and Plain Text
// const extractJson = (content) => {
//   if (!content || typeof content !== 'string') return { text: "", data: null };

//   // 1. Try parsing the WHOLE string as JSON first
//   try {
//     const parsed = JSON.parse(content);
//     if (parsed.greeting || parsed.flights_section || parsed.trains_section || Array.isArray(parsed)) {
//        return { text: "", data: parsed };
//     }
//   } catch (e) {
//     // Not raw JSON, proceed to check for markdown blocks
//   }

//   // 2. Try finding Markdown Code Block (Fallback)
//   const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
//   if (jsonMatch) {
//     try {
//       const cleanJson = jsonMatch[1].trim();
//       return { 
//         // Remove the JSON block from the text so we don't show raw code
//         text: content.replace(jsonMatch[0], "").trim(), 
//         data: JSON.parse(cleanJson) 
//       };
//     } catch (e) { 
//       console.error("Block Parse Failed", e);
//       // 🚨 FIX 1: Safety Fallback - If JSON fails, show raw text instead of crashing
//       return { text: content, data: null };
//     }
//   }

//   // 3. Fallback: Treat as regular text
//   return { text: content, data: null };
// };

// const MessageBubble = ({ role, content, onOptionSelect }) => {
//   const isUser = role === 'user';
  
//   // 🚨 FIX 2: Local state to track selection visually
//   const [selectedId, setSelectedId] = useState(null);

//   // Extract data using our robust helper
//   const { text, data } = isUser ? { text: content, data: null } : extractJson(content);

//   // Helper to handle selection click
//   const handleSelection = (item) => {
//       // Use a unique property (number) to track selection
//       const id = item.number || item.id; 
//       setSelectedId(id);
//       if (onOptionSelect) onOptionSelect(item);
//   };

//   return (
//     <div className={`flex w-full mb-8 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
//       <div className={`flex w-full max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-4 items-start`}>
        
//         {/* Avatar */}
//         <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/20
//           ${isUser ? 'bg-indigo-600' : 'bg-emerald-500'}`}>
//           {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-white" />}
//         </div>

//         {/* --- CONTENT CONTAINER --- */}
//         <div className="flex-1 flex flex-col gap-6 min-w-0">
            
//             {/* 1. TEXT ONLY (Fallback or standard chat) */}
//             {text && (
//                 <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${
//                     isUser 
//                     ? 'bg-indigo-600 text-white rounded-tr-none' 
//                     : 'bg-white/90 backdrop-blur-md rounded-tl-none border border-white/50 text-slate-800'
//                 }`}>
//                     <div className={`prose ${isUser ? 'prose-invert' : 'prose-slate'} max-w-none`}>
//                         <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
//                     </div>
//                 </div>
//             )}

//             {/* 2. STRUCTURED DATA (The New Segmented UI) */}
//             {data && !Array.isArray(data) && (
//                 <>
//                     {/* A. GREETING BUBBLE */}
//                     {data.greeting && (
//                         <div className="bg-white/90 backdrop-blur-sm p-5 rounded-2xl rounded-tl-none shadow-sm border border-slate-200/60 text-slate-700 text-sm">
//                             <span className="font-bold text-lg block mb-2 text-slate-800 flex items-center gap-2">
//                                 👋 Hello!
//                             </span>
//                             {data.greeting}
//                         </div>
//                     )}

//                     {/* B. FLIGHT SECTION */}
//                     {data.flights_section && (
//                         <div className="animate-fade-in delay-100">
//                             {/* Section Header */}
//                             <div className="flex items-center gap-2 mb-3 ml-1">
//                                 <div className="bg-blue-100 p-1.5 rounded-lg text-blue-600">
//                                     <Sparkles size={14} />
//                                 </div>
//                                 <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
//                                     Flight Options
//                                 </span>
//                             </div>
                            
//                             {/* Context Info Box */}
//                             {data.flights_section.info && (
//                                 <div className="bg-blue-50 text-blue-900 text-xs px-4 py-3 rounded-xl mb-4 border border-blue-100 flex items-start gap-2">
//                                     <span className="text-lg">✈️</span>
//                                     <span className="mt-0.5">{data.flights_section.info}</span>
//                                 </div>
//                             )}

//                             {/* Cards Grid */}
//                             <div className="grid gap-4">
//                                 {data.flights_section.data.map((flight, idx) => (
//                                     <FlightCard 
//                                         key={idx} 
//                                         flight={flight} 
//                                         onSelect={handleSelection} 
//                                         isSelected={selectedId === flight.number} 
//                                     />
//                                 ))}
//                             </div>
//                         </div>
//                     )}

//                     {/* C. TRAIN SECTION */}
//                     {data.trains_section && (
//                         <div className="animate-fade-in delay-200 pt-4 border-t border-slate-100/50 mt-2">
//                              {/* Section Header */}
//                              <div className="flex items-center gap-2 mb-3 ml-1">
//                                 <div className="bg-orange-100 p-1.5 rounded-lg text-orange-600">
//                                     <Sparkles size={14} />
//                                 </div>
//                                 <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
//                                     Train Options
//                                 </span>
//                             </div>

//                             {/* Context Info Box */}
//                             {data.trains_section.info && (
//                                 <div className="bg-orange-50 text-orange-900 text-xs px-4 py-3 rounded-xl mb-4 border border-orange-100 flex items-start gap-2">
//                                     <span className="text-lg">🚆</span>
//                                     <span className="mt-0.5">{data.trains_section.info}</span>
//                                 </div>
//                             )}

//                             {/* Cards Grid */}
//                             <div className="grid gap-4">
//                                 {data.trains_section.data.map((train, idx) => (
//                                     <TrainCard 
//                                         key={idx} 
//                                         train={train} 
//                                         onSelect={handleSelection} 
//                                         isSelected={selectedId === train.number}
//                                     />
//                                 ))}
//                             </div>
//                         </div>
//                     )}
//                 </>
//             )}

//             {/* 3. LEGACY LIST SUPPORT (If backend sends simple array) */}
//             {data && Array.isArray(data) && (
//                <div className="w-full grid gap-3 mt-1">
//                   {data.map((item, idx) => {
//                       const isSelected = selectedId === item.number;
//                       if (item.type === 'flight') return <FlightCard key={idx} flight={item} onSelect={handleSelection} isSelected={isSelected} />;
//                       if (item.type === 'train') return <TrainCard key={idx} train={item} onSelect={handleSelection} isSelected={isSelected} />;
//                       return null;
//                   })}
//                </div>
//             )}
            
//         </div>
//       </div>
//     </div>
//   );
// };

// export default MessageBubble;

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, Sparkles } from 'lucide-react';
import FlightCard from './FlightCard';
import TrainCard from './TrainCard';

// ✅ ROBUST PARSER: Handles Raw JSON, Markdown Blocks, and Mixed Content
const extractJson = (content) => {
  if (!content || typeof content !== 'string') return { text: "", data: null };

  // 1. Try parsing the WHOLE string as JSON first (Pure Data)
  try {
    const parsed = JSON.parse(content);
    if (parsed.greeting || parsed.flights_section || parsed.trains_section || Array.isArray(parsed)) {
       return { text: "", data: parsed };
    }
  } catch (e) {
    // Not raw JSON, proceed to check for markdown blocks
  }

  // 2. Try finding Markdown Code Block (Mixed Content)
  // This regex captures text BEFORE the block and the JSON INSIDE the block
  const jsonMatch = content.match(/([\s\S]*?)```json\s*([\s\S]*?)\s*```/);
  
  if (jsonMatch) {
    try {
      const introText = jsonMatch[1].trim(); // Text before the code block
      const cleanJson = jsonMatch[2].trim(); // JSON inside the block
      
      return { 
        text: introText, 
        data: JSON.parse(cleanJson) 
      };
    } catch (e) { 
      console.error("Block Parse Failed", e);
      // Safety Fallback: Show everything as text
      return { text: content, data: null };
    }
  }

  // 3. Fallback: Treat as regular text
  return { text: content, data: null };
};

const MessageBubble = ({ role, content, onOptionSelect }) => {
  const isUser = role === 'user';
  const [selectedId, setSelectedId] = useState(null);

  // Extract data using our robust helper
  const { text, data } = isUser ? { text: content, data: null } : extractJson(content);

  const handleSelection = (item) => {
      // Use a unique property (number) to track selection
      const id = item.number || item.id; 
      setSelectedId(id);
      if (onOptionSelect) onOptionSelect(item);
  };

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
            
            {/* 1. TEXT BUBBLE (Render if text exists) */}
            {text && typeof text === 'string' && (
                <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${
                    isUser 
                    ? 'bg-indigo-600 text-white rounded-tr-none' 
                    : 'bg-white/90 backdrop-blur-md rounded-tl-none border border-white/50 text-slate-800'
                }`}>
                    <div className={`prose ${isUser ? 'prose-invert' : 'prose-slate'} max-w-none`}>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
                    </div>
                </div>
            )}

            {/* 2. STRUCTURED DATA CARDS (Render if data exists) */}
            {data && !Array.isArray(data) && (
                <div className="flex flex-col gap-4">
                    {/* A. GREETING BUBBLE (If data has a specific greeting field) */}
                    {data.greeting && !text && (
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
                            {/* Section Header */}
                            <div className="flex items-center gap-2 mb-3 ml-1">
                                <div className="bg-blue-100 p-1.5 rounded-lg text-blue-600">
                                    <Sparkles size={14} />
                                </div>
                                <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
                                    Flight Options
                                </span>
                            </div>
                            
                            {/* Context Info Box */}
                            {data.flights_section.info && (
                                <div className="bg-blue-50 text-blue-900 text-xs px-4 py-3 rounded-xl mb-4 border border-blue-100 flex items-start gap-2">
                                    <span className="text-lg">✈️</span>
                                    <span className="mt-0.5">{data.flights_section.info}</span>
                                </div>
                            )}

                            {/* Cards Grid */}
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
                        </div>
                    )}

                    {/* C. TRAIN SECTION */}
                    {data.trains_section && (
                        <div className="animate-fade-in delay-200 pt-4 border-t border-slate-100/50 mt-2">
                             {/* Section Header */}
                             <div className="flex items-center gap-2 mb-3 ml-1">
                                <div className="bg-orange-100 p-1.5 rounded-lg text-orange-600">
                                    <Sparkles size={14} />
                                </div>
                                <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
                                    Train Options
                                </span>
                            </div>

                            {/* Context Info Box */}
                            {data.trains_section.info && (
                                <div className="bg-orange-50 text-orange-900 text-xs px-4 py-3 rounded-xl mb-4 border border-orange-100 flex items-start gap-2">
                                    <span className="text-lg">🚆</span>
                                    <span className="mt-0.5">{data.trains_section.info}</span>
                                </div>
                            )}

                            {/* Cards Grid */}
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
                        </div>
                    )}
                </div>
            )}

            {/* 3. LEGACY LIST SUPPORT (For backward compatibility) */}
            {data && Array.isArray(data) && (
               <div className="w-full grid gap-3 mt-1">
                  {data.map((item, idx) => {
                      const isSelected = selectedId === item.number;
                      if (item.type === 'flight') return <FlightCard key={idx} flight={item} onSelect={handleSelection} isSelected={isSelected} />;
                      if (item.type === 'train') return <TrainCard key={idx} train={item} onSelect={handleSelection} isSelected={isSelected} />;
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