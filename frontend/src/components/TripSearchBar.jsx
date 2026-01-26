import React, { useState, useRef } from "react";
import {
  Search,
  Users,
  ArrowRightLeft,
  PlaneTakeoff,
  PlaneLanding,
  Calendar,
  Wallet,
} from "lucide-react";

const TripSearchBar = ({ onSubmit }) => {
  const [form, setForm] = useState({
    source: "",
    destination: "",
    start_date: "",
    end_date: "",
    travellers: 1,
    budget: "medium",
  });

  const [rotated, setRotated] = useState(false);

  const departureRef = useRef(null);
  const returnRef = useRef(null);

  const update = (key, value) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSwap = (e) => {
    e.stopPropagation();
    setRotated(!rotated);
    setForm((prev) => ({
      ...prev,
      source: prev.destination,
      destination: prev.source,
    }));
  };

  const handleSubmit = () => {
    if (!form.source || !form.destination || !form.start_date) return;
    onSubmit(form);
  };

  return (
    <div className="w-full max-w-7xl mx-auto relative z-20">
      <div className="bg-white/90 backdrop-blur-xl border border-white/50 shadow-2xl rounded-[2rem] p-4 animate-fade-in-up">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-0 items-center lg:divide-x divide-slate-300">

          {/* FROM */}
          <div className="lg:col-span-3 px-6 py-2 relative group">
            <label className="text-[11px] font-black text-blue-900 uppercase tracking-widest mb-1 flex items-center gap-1">
              <PlaneTakeoff size={12} className="text-blue-700" /> From
            </label>
            <input
              className="w-full bg-transparent outline-none text-slate-900 font-extrabold text-lg placeholder-slate-500 group-hover:placeholder-grey-500 transition-all"
              placeholder="Origin City"
              value={form.source}
              onChange={(e) => update("source", e.target.value)}
            />

            <button
              onClick={handleSwap}
              className="hidden lg:flex absolute -right-5 top-1/2 -translate-y-1/2 w-10 h-10 bg-white border border-slate-200 shadow-lg rounded-full items-center justify-center text-grey-500 hover:scale-110 hover:bg-blue-50 z-10 transition-all duration-300"
            >
              <ArrowRightLeft
                size={16}
                className={`transition-transform duration-300 ${
                  rotated ? "rotate-180" : ""
                }`}
              />
            </button>
          </div>

          {/* TO */}
          <div className="lg:col-span-3 px-6 py-2 group pl-8">
            <label className="text-[11px] font-black text-blue-900 uppercase tracking-widest mb-1 flex items-center gap-1">
              <PlaneLanding size={12} className="text-blue-700" /> To
            </label>
            <input
              className="w-full bg-transparent outline-none text-slate-900 font-extrabold text-lg placeholder-slate-500 group-hover:placeholder-grey-500 transition-all"
              placeholder="Dream Destination"
              value={form.destination}
              onChange={(e) => update("destination", e.target.value)}
            />
          </div>

          {/* DATES */}
          <div className="lg:col-span-4 px-6 py-2 grid grid-cols-2 gap-4">

            {/* DEPARTURE */}
            <div className="group hover:bg-blue-50/50 rounded-lg transition-colors p-1">
              <label className="text-[11px] font-black text-blue-900 uppercase tracking-widest mb-1 flex items-center gap-1">
                <Calendar size={12} className="text-blue-700" /> Departure
              </label>
              <input
                ref={departureRef}
                type="date"
                className="w-full bg-transparent outline-none text-slate-900 font-bold text-sm cursor-pointer uppercase select-none"
                onMouseDown={(e) => e.preventDefault()}   // ⛔ stop text selection
                onClick={(e) => e.currentTarget.showPicker()}
                onChange={(e) => update("start_date", e.target.value)}
              />
            </div>

            {/* RETURN */}
            <div className="group border-l border-slate-300 pl-4 hover:bg-blue-50/50 rounded-lg transition-colors p-1">
              <label className="text-[11px] font-black text-blue-900 uppercase tracking-widest mb-1 flex items-center gap-1">
                <Calendar size={12} className="text-blue-700" /> Return
              </label>
              <input
                ref={returnRef}
                type="date"
                className="w-full bg-transparent outline-none text-slate-900 font-bold text-sm cursor-pointer uppercase select-none"
                onMouseDown={(e) => e.preventDefault()}
                onClick={(e) => e.currentTarget.showPicker()}
                onChange={(e) => update("end_date", e.target.value)}
              />
            </div>
          </div>

          {/* ACTION */}
          <div className="lg:col-span-2 px-4 py-1 flex flex-col gap-3">
            <div className="flex justify-between items-center px-1">
              <div className="flex items-center gap-1">
                <Users size={14} className="text-blue-900" />
                <input
                  type="number"
                  min="1"
                  value={form.travellers}
                  onChange={(e) => update("travellers", e.target.value)}
                  className="w-8 bg-transparent text-sm font-black text-slate-900 outline-none text-center"
                />
              </div>
              <div className="flex items-center gap-1">
                <Wallet size={14} className="text-blue-900" />
                <select
                  className="bg-transparent text-[11px] font-bold outline-none text-slate-900 uppercase cursor-pointer"
                  onChange={(e) => update("budget", e.target.value)}
                >
                  <option value="medium">Medium</option>
                  <option value="high">Luxury</option>
                  <option value="low">Economy</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleSubmit}
              className="w-full py-3 bg-blue-700 hover:bg-blue-800 text-white rounded-xl font-bold text-sm shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
            >
              EXPLORE <Search size={16} strokeWidth={3} />
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};

export default TripSearchBar;
