import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, Plane, Compass, MapPin, Calendar, Users, RotateCcw } from 'lucide-react';
import MessageBubble from './components/MessageBubble';
import TripSearchBar from "./components/TripSearchBar";
import { sendMessage, getTripState, streamMessage } from './api'; // ✅ Import streamMessage

// HIGH QUALITY IMAGE
const HERO_IMAGE = "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?q=80&w=2070&auto=format&fit=crop";

function App() {
  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem("chat_history");
    return savedMessages 
      ? JSON.parse(savedMessages) 
      : [{ role: 'ai', content: "Hi! I'm **TravelGenie**. Where is your next adventure?" }];
  });

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [tripDetails, setTripDetails] = useState(null);
  const [started, setStarted] = useState(false);
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("chat_history", JSON.stringify(messages));
  }, [messages]);

  // Scroll to bottom when messages or loading state changes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
    return () => clearTimeout(timeoutId);
  }, [messages, loading]); 

  // Polling for Trip Details (Destination, Date, etc.)
  useEffect(() => {
    if(!started) return;
    const interval = setInterval(async () => {
      const state = await getTripState();
      if (state?.trip_details) setTripDetails(state.trip_details);
    }, 5000);
    return () => clearInterval(interval);
  }, [started]);

  const handleReset = () => {
    localStorage.removeItem("chat_history");
    localStorage.removeItem("session_id");
    setMessages([{ role: 'ai', content: "Hi! I'm **TravelGenie**. Where is your next adventure?" }]);
    setTripDetails(null);
    setStarted(false);
    setLoading(false);
    setInput("");
  };

  // 🚨 FIXED: Streaming Logic for Trip Start
  const handleTripStart = async (formData) => {
    localStorage.removeItem("chat_history"); 
    setStarted(true);
    setLoading(true);
    
    // 1. Initial User Message
    setMessages([{ 
        role: "user", 
        content: `Planning a trip from **${formData.source}** to **${formData.destination}**.` 
    }]);

    // 2. Add Placeholder "Thinking..." Message
    setMessages(prev => [...prev, { role: "ai", content: "Thinking..." }]);

    // 3. Buffer to accumulate incoming stream data
    let currentData = { greeting: "", flights_section: null, trains_section: null };

    // 4. Start Stream
    await streamMessage("Please plan my trip.", formData, (chunk) => {
        
        // Handle Greeting
        if (chunk.type === "greeting") {
            currentData.greeting = chunk.content;
        } 
        // Handle Flights
        else if (chunk.type === "flights") {
            currentData.flights_section = { info: "Found Flights", data: chunk.data };
        }
        // Handle Trains
        else if (chunk.type === "trains") {
            currentData.trains_section = { info: "Found Trains", data: chunk.data };
        }

        // 5. Update the LAST message in state with the new JSON structure
        setMessages(prev => {
            const newMsgs = [...prev];
            if (newMsgs.length > 0) {
                newMsgs[newMsgs.length - 1] = { 
                    role: "ai", 
                    // MessageBubble.jsx will parse this JSON string
                    content: JSON.stringify(currentData) 
                };
            }
            return newMsgs;
        });
    });

    setLoading(false);
  };

  // Standard Send (Non-Streaming)
  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    const data = await sendMessage(input);
    setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    setLoading(false);
  };

  const handleOptionSelect = async (selectedOption) => {
    let userChoiceText = "";
    let displayText = "";

    if (selectedOption.airline) {
        userChoiceText = `Select option: Flight ${selectedOption.number} (${selectedOption.airline})`;
        displayText = `✅ Selected: ${selectedOption.airline} Flight ${selectedOption.number}`;
    } else if (selectedOption.selected_class) {
        userChoiceText = `Select option: Train ${selectedOption.number} (${selectedOption.name}) in class ${selectedOption.selected_class.name}`;
        displayText = `✅ Selected: ${selectedOption.name} (${selectedOption.selected_class.name})`;
    } else return;

    setMessages(prev => [...prev, { role: 'user', content: displayText }]);
    setLoading(true);
    const data = await sendMessage(userChoiceText);
    setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    setLoading(false);
  };

  return (
    <div className="h-screen w-full overflow-hidden flex flex-col font-sans text-slate-800 relative">
      <div className="absolute inset-0 z-0">
         <img src={HERO_IMAGE} alt="Background" className="w-full h-full object-cover" />
         <div className={`absolute inset-0 transition-all duration-1000 ${started ? 'bg-slate-900/60 backdrop-blur-sm' : 'bg-black/30'}`}></div>
      </div>

      <nav className="absolute top-0 left-0 w-full p-4 md:p-6 flex justify-between items-center z-40">
          <div className="flex items-center gap-2 font-bold text-2xl tracking-tighter text-white drop-shadow-md">
              <div className="bg-white/10 backdrop-blur-md p-2 rounded-xl border border-white/20">
                <Plane className="w-6 h-6 text-white" /> 
              </div>
              TravelGenie
          </div>

          {started && (
            <button 
              onClick={handleReset}
              className="flex items-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-md text-white px-4 py-2 rounded-xl border border-white/20 transition-all text-sm font-bold shadow-sm active:scale-95 cursor-pointer"
            >
              <RotateCcw size={16} />
              New Trip
            </button>
          )}
      </nav>

      {!started && (
        <div className="relative z-20 flex-1 flex flex-col items-center justify-center p-4">
            <div className="text-center space-y-4 mb-10 animate-fade-in-up">
                <span className="inline-block py-1.5 px-4 rounded-full bg-blue-600/80 backdrop-blur-md text-white text-[10px] font-black tracking-[0.2em] uppercase shadow-xl border border-blue-400/30">
                    <Sparkles size={12} className="inline mr-2 mb-0.5 text-yellow-300"/> AI Travel Architect
                </span>
                <h1 className="text-5xl md:text-8xl font-black text-white tracking-tight drop-shadow-2xl leading-tight">
                    Experience the <br/> Extraordinary
                </h1>
                <p className="text-lg md:text-2xl text-white/90 font-medium max-w-2xl mx-auto drop-shadow-lg">
                    Your next journey is just one click away.
                </p>
            </div>
            <div className="w-full max-w-6xl animate-fade-in-up delay-100">
                <TripSearchBar onSubmit={handleTripStart} />
            </div>
        </div>
      )}

      {started && (
        <div className="relative z-20 flex flex-1 h-full pt-20 pb-4 px-4 md:px-8 gap-6 animate-fade-in">
          <aside className="hidden md:flex w-80 flex-col gap-4">
             <div className="bg-white/10 backdrop-blur-xl border border-white/20 p-6 rounded-3xl shadow-2xl text-white">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shadow-lg">
                        <MapPin size={20} />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-blue-200 uppercase tracking-wider">Trip To</p>
                        <h2 className="text-2xl font-black leading-none">{tripDetails?.destination || "Loading..."}</h2>
                    </div>
                </div>

                <div className="space-y-3">
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded-xl border border-white/10">
                        <Calendar size={16} className="text-blue-200"/>
                        <div className="text-sm font-medium">{tripDetails?.start_date || "--"}</div>
                    </div>
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded-xl border border-white/10">
                         <Users size={16} className="text-blue-200"/>
                        <div className="text-sm font-medium">{tripDetails?.travellers || 1} Travelers</div>
                    </div>
                </div>
             </div>
          </aside>

          <main className="flex-1 bg-white/80 backdrop-blur-xl border border-white/40 rounded-[2rem] shadow-2xl flex flex-col overflow-hidden relative">
            <div className="md:hidden p-4 border-b border-slate-200/50 bg-white/50 backdrop-blur-md flex justify-between items-center">
                <span className="font-bold text-slate-800">{tripDetails?.destination || "Trip Planner"}</span>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scrollbar-hide">
              {messages.map((msg, idx) => (
                <MessageBubble 
                    key={idx} 
                    role={msg.role} 
                    content={msg.content} 
                    onOptionSelect={handleOptionSelect}
                />
              ))}
              {loading && (
                 <div className="flex items-center gap-2 text-slate-500 text-sm ml-14 animate-pulse">
                    <Compass size={18} className="animate-spin text-blue-600" /> 
                    <span className="font-medium">AI is planning...</span>
                 </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="p-4 md:p-6 bg-white/60 backdrop-blur-md border-t border-white/50">
               <div className="max-w-4xl mx-auto flex items-center gap-2 bg-white p-2 rounded-2xl shadow-sm border border-slate-200 focus-within:border-blue-400 focus-within:ring-4 focus-within:ring-blue-50 transition-all">
                 <input
                   className="flex-1 bg-transparent px-4 py-2 outline-none text-slate-700 font-medium placeholder-slate-400"
                   placeholder="Type your message..."
                   value={input}
                   onChange={e => setInput(e.target.value)}
                   onKeyDown={e => e.key === "Enter" && handleSend()}
                   disabled={loading}
                 />
                 <button onClick={handleSend} className="w-10 h-10 bg-blue-600 text-white rounded-xl hover:bg-blue-700 flex items-center justify-center transition-transform active:scale-95 shadow-lg">
                    <Send size={18} />
                 </button>
               </div>
            </div>
          </main>
        </div>
      )}
    </div>
  );
}

export default App;