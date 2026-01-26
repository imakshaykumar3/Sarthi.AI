import axios from 'axios';

const API_URL = "http://localhost:8000";

// Generate a random session ID for testing
export const getSessionId = () => {
  let session = localStorage.getItem("session_id");
  if (!session) {
    session = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("session_id", session);
  }
  return session;
};

// Modified sendMessage to accept OPTIONAL tripData
export const sendMessage = async (message, tripData = null) => {
  const session_id = getSessionId();
  
  const payload = {
    session_id: session_id,
    message: message
  };

  // ✅ If data exists, format it correctly for the backend
  if (tripData) {
      payload.trip_data = {
          source: tripData.source,
          destination: tripData.destination,
          start_date: tripData.start_date,
          end_date: tripData.end_date,
          budget: tripData.budget,
          travelers: String(tripData.travellers) 
      };
  }

  try {
    const response = await axios.post(`${API_URL}/chat`, payload);
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    return { response: "Error connecting to server." };
  }
};

export const getTripState = async () => {
    const session_id = getSessionId();
    try {
        const response = await axios.get(`${API_URL}/trip/${session_id}`);
        return response.data;
    } catch (error) {
        return null;
    }
}