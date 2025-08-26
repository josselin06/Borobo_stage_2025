import { useEffect, useState } from "react";

function DateTimeDisplay() {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 1_000);
    return () => clearInterval(interval);
  }, []);

  const dateString = now.toLocaleDateString("fr-FR", {
    weekday: "long",
    day:      "numeric",
    month:    "long",
    year:     "numeric",
  });
  const timeString = now.toLocaleTimeString("fr-FR", {
    hour:   "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <div className="p-2 text-gray-600 text-sm text-right">
      {dateString} — {timeString}
    </div>
  );
}

export default DateTimeDisplay;
