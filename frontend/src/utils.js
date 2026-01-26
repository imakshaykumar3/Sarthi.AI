export const formatPrice = (price) => {
  if (!price || price === "N/A") return "N/A";
  // Handle strings like "INR 5000" or raw numbers
  let cleanString = String(price).replace(/[^0-9.]/g, "");
  const num = parseInt(cleanString, 10);
  return isNaN(num) ? "N/A" : `₹${num.toLocaleString("en-IN")}`;
};

export const extractTime = (val) => {
  if (!val) return "--:--";
  // Extract HH:MM regardless of seconds or dates attached
  const match = String(val).match(/(\d{1,2}:\d{2})/);
  return match ? match[0] : "--:--";
};

export const formatDate = (dateStr) => {
    if (!dateStr) return "";
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString("en-US", { day: "numeric", month: "short" }).toUpperCase();
    } catch (e) { return ""; }
};