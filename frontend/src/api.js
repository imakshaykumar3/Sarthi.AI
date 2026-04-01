import axios from 'axios';

// ✅ Use Environment Variable for production, fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- Helper: Get/Create Session ID ---
export const getSessionId = () => {
  let session = localStorage.getItem("session_id");
  if (!session) {
    session = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("session_id", session);
  }
  return session;
};

// --- 1. Standard Chat (Selections/Confirmations/Itinerary) ---
/**
 * Sends a message to the backend. 
 * @param {string} message - The text content.
 * @param {object} tripData - Optional object containing updated trip context (e.g. selected_hotel).
 */
export const sendMessage = async (message, tripData = null) => {
  const session_id = getSessionId();
  
  const payload = {
    session_id: session_id,
    message: message
  };

  // If tripData is provided (like when selecting a hotel), 
  // we attach it so the Backend AgentState is updated immediately.
  if (tripData) {
      payload.trip_data = {
          source: tripData.source,
          destination: tripData.destination,
          start_date: tripData.start_date,
          end_date: tripData.end_date,
          budget: tripData.budget,
          travelers: String(tripData.travellers || tripData.travelers || "1"),
          selected_hotel: tripData.selected_hotel || null
      };
  }

  try {
    const response = await axios.post(`${API_URL}/chat`, payload);
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    return { response: "I'm having trouble connecting to the server. Please try again." };
  }
};

// --- 2. State Retrieval (Polling) ---
export const getTripState = async () => {
    const session_id = getSessionId();
    try {
        const response = await axios.get(`${API_URL}/trip/${session_id}`);
        return response.data;
    } catch (error) {
        console.error("Polling Error:", error);
        return null;
    }
};

// --- 3. Streaming Chat (Planning Phase) ---
export const streamMessage = async (message, tripData, onChunk) => {
  const session_id = getSessionId();
  
  try {
    const response = await fetch(`${API_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id,
        message,
        trip_data: tripData
          ? {
              source: tripData.source,
              destination: tripData.destination,
              start_date: tripData.start_date,
              end_date: tripData.end_date,
              budget: tripData.budget,
              travelers: String(tripData.travellers || "1"),
            }
          : null,
      }),
    });

    if (!response.body) return;

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n\n");
      
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.replace("data: ", "").trim();
          
          if (jsonStr === "[DONE]") return;
          
          try {
            const data = JSON.parse(jsonStr);
            onChunk(data); 
          } catch (e) {
            console.error("Stream Parse Error", e);
          }
        }
      }
    }
  } catch (error) {
    console.error("Stream Connection Error:", error);
    onChunk({ type: "error", content: "Connection lost." });
  }
};