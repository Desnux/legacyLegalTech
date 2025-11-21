"use client";

import { useState } from "react";
import { differenceInDays, parseISO } from "date-fns";
import { formatDate } from "@/utils/date";

interface Event {
  type: "documents" | "demand_text" | "notification" | "asset_seizure" | "finished" | string;
  date: string | null;
}

interface StatusBarProps {
  receivedEvents: Event[];
}

const allEventTypes: Event["type"][] = [
  "documents",
  "demand_text",
  "notification",
  "asset_seizure",
  "finished"
];

const eventNames: Record<string, string> = {
  documents: "Recepción de antecedentes",
  demand_text: "Envío de demanda",
  notification: "Notificación de demanda",
  asset_seizure: "Traba de embargo",
  finished: "Fin del caso"
};

const calculateDaysDifference = (date1: string | null, date2: string | null) => {
  if (!date1 || !date2) {
    return "";
  }
  try {
    const d1 = parseISO(date1);
    const d2 = parseISO(date2);
    const days = differenceInDays(d2, d1);
    return Math.abs(days) > 300 ? "+300 días" : `${Math.abs(days)} días`;
  } catch (error) {
    return "";
  }
};

export default function StatusBar({ receivedEvents }: StatusBarProps) {
const [hoveredEvent, setHoveredEvent] = useState<null | string>(null);

  const events = allEventTypes.map((type) => {
    const match = receivedEvents.find((e) => e.type === type);
    return { type, date: match?.date || null };
  });

  return (
    <div className="flex items-center space-x-0 p--4 sm:gap-0">
      {events.map((event, index) => (
        <div key={index} className="flex items-center relative">
          <div
            className={`relative w-5 h-5 flex items-center justify-center rounded-full border-2 z-30 
              ${event.date || receivedEvents.length > index ? "bg-blue-600 border-blue-600" : "bg-gray-300 border-gray-400"}`}
            onMouseEnter={() => setHoveredEvent(event.type)}
            onMouseLeave={() => setHoveredEvent(null)}
          >
            {hoveredEvent === event.type && (
              <div className={`absolute -top-10 left-1/2 transform -translate-x-1/2 ${event.date || receivedEvents.length > index ? "bg-blue-600" : "bg-gray-400"} text-white text-xs p-1 rounded shadow-md w-40 h-10 text-center`}>
                {eventNames[event.type]}
                {event.date && <div>{formatDate(event.date)}</div>}
              </div>
            )}
          </div>
          {index < events.length - 1 && (
            <div className="relative w-12 sm:w-20">
              <div className="h-1 w-full flex">
                <div className={`${event.date || receivedEvents.length > index ? "bg-blue-600" : "bg-gray-400"} w-1/2 h-full`}></div>
                <div className={`${events[index + 1].date || receivedEvents.length > index+1 ? "bg-blue-600" : "bg-gray-400"} w-1/2 h-full`}></div>
              </div>
              <div className="absolute left-0 w-full flex justify-center mt-0">
                <span className="text-sm text-gray-600 hidden sm:block">
                  {calculateDaysDifference(event.date, events[index + 1].date)}
                </span>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}