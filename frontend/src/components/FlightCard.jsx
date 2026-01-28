import React from "react";
import { Plane, Clock, Check } from "lucide-react";

/* ---------------- HELPERS ---------------- */

const extractTime = (val) => {
  if (!val) return "--:--";
  const match = String(val).match(/(\d{1,2}:\d{2})/);
  return match ? match[0] : "--:--";
};

const formatPrice = (price) => {
  if (!price || price === "N/A") return "N/A";
  const num = parseInt(String(price).replace(/[^0-9]/g, ""), 10);
  return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
};

const titleCase = (str) =>
  str
    ? str.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())
    : "";

/* ---------------- COMPONENT ---------------- */

const FlightCard = ({ flight, onSelect, isSelected }) => {
  const flightNum = flight.number || "Unknown";
  const airlineName = flight.airline || "Airline";

  const depTime = extractTime(flight.dep);
  const arrTime = extractTime(flight.arr);
  const duration = flight.dur || "--";

  const originCity = titleCase(
    flight.from_city_label || flight.from_airport_code
  );
  const destinationCity = titleCase(
    flight.to_city_label || flight.to_airport_code
  );

  const originCode = flight.from_airport_code;
  const destinationCode = flight.to_airport_code;

  const isNonStop = flight.stops === 0;

  return (
    <div
      className={`group relative rounded-2xl p-5 mb-4 cursor-pointer border transition-all duration-300
        ${
          isSelected
            ? "bg-blue-50 border-blue-600 shadow-md"
            : "bg-white border-slate-200 shadow-sm hover:shadow-lg hover:border-blue-300"
        }`}
      onClick={(e) => {
        e.stopPropagation();
        onSelect?.(flight);
      }}
    >
      <div className="flex flex-col lg:flex-row justify-between items-center gap-6">

        {/* LEFT */}
        <div className="flex items-center gap-4 w-full lg:w-1/4">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center border bg-slate-50">
            <Plane size={24} className="text-blue-600 -rotate-45" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-lg">{airlineName}</h3>
            <p className="text-[11px] text-slate-500 font-bold">{flightNum}</p>
          </div>
        </div>

        {/* CENTER */}
        <div className="flex-1 flex items-center justify-center gap-6">

          {/* Departure */}
          <div className="text-center min-w-[90px]">
            <p className="text-2xl font-black">{depTime}</p>
            <p className="text-xs font-semibold text-slate-700">{originCity}</p>
            <p className="text-[11px] text-slate-400 font-bold">
              ({originCode})
            </p>
          </div>

          {/* Route */}
          <div className="relative flex flex-col items-center min-w-[170px]">

            <p className="text-[11px] text-slate-500 flex items-center gap-1 mb-1">
              <Clock size={12} /> {duration}
            </p>

            {/* Curved dotted path */}
            <svg viewBox="0 0 200 40" className="w-full h-6">
              <path
                d="M10 30 Q100 6 190 30"
                fill="none"
                strokeDasharray="4 6"
                className="stroke-slate-300 stroke-[2]
                  transition-colors duration-300
                  group-hover:stroke-blue-300"
              />
            </svg>

            {/* Plane (SUBTLE animation) */}
            <Plane
              size={16}
              className="
                absolute top-[22px] left-1/2 -translate-x-1/2 rotate-90
                text-blue-600
                transition-all duration-500 ease-out
                group-hover:-translate-y-1
                group-hover:scale-110
                group-hover:opacity-90
              "
            />

            <span
              className={`mt-3 text-[10px] font-semibold px-2 py-0.5 rounded-full
                ${
                  isNonStop
                    ? "bg-emerald-50 text-emerald-600"
                    : "bg-orange-50 text-orange-600"
                }`}
            >
              {isNonStop ? "Non-stop" : `${flight.stops} stop`}
            </span>
          </div>

          {/* Arrival */}
          <div className="text-center min-w-[90px]">
            <p className="text-2xl font-black">{arrTime}</p>
            <p className="text-xs font-semibold text-slate-700">
              {destinationCity}
            </p>
            <p className="text-[11px] text-slate-400 font-bold">
              ({destinationCode})
            </p>
          </div>
        </div>

        {/* RIGHT */}
        <div className="flex items-center gap-5">
          <div className="text-right">
            <p className="text-2xl font-black">{formatPrice(flight.price)}</p>
            <p className="text-[10px] text-slate-400">per adult</p>
          </div>

          <button
            className={`px-6 py-2 rounded-xl text-sm font-bold transition-all active:scale-95
              ${
                isSelected
                  ? "bg-blue-600 text-white"
                  : "bg-blue-100 text-blue-700 hover:bg-blue-200"
              }`}
          >
            {isSelected ? (
              <span className="flex items-center gap-1">
                <Check size={14} /> Selected
              </span>
            ) : (
              "Select"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlightCard;
