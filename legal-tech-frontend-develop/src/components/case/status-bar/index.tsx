"use client";

import { useState } from "react";
import { differenceInDays, parseISO } from "date-fns";
import { formatDate } from "@/utils/date";
import { translatedEventNames } from "@/utils/event-types";

interface Event {
  type: "documents" | "demand_text" | "dispatch" | "notification" | "defense" | "plaintiff_answer" | "finished" | string;
  date: string | null;
}

interface StatusBarProps {
  receivedEvents: Event[];
}

const allEventTypes: Event["type"][] = [
  "documents",
  "demand_text",
  "dispatch",
  "notification",
  "defense",
  "plaintiff_answer",
  "finished"
];

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

const establishEventColor = (event: { type: string; date: string | null }, index: number, events: { type: string; date: string | null }[]) => {
  // Encontrar la etapa actual (la primera pendiente)
  let currentStageIndex = -1;
  for (let i = 0; i < events.length; i++) {
    if (!events[i].date && events[i].type !== "finished") {
      currentStageIndex = i;
      break;
    }
  }
  
  // Si no hay etapa actual pendiente, la última completada es la actual
  if (currentStageIndex === -1) {
    for (let i = events.length - 1; i >= 0; i--) {
      if (events[i].date && events[i].type !== "finished") {
        currentStageIndex = i;
        break;
      }
    }
  }
  
  // Etapas futuras (después de la actual) siempre en gris
  if (currentStageIndex !== -1 && index > currentStageIndex) {
    return "gray";
  }
  
  // Etapa actual
  if (index === currentStageIndex) {
    if (!event.date) {
      // Etapa actual pendiente - verificar si está atrasada
      let lastCompletedEventIndex = -1;
      for (let i = index - 1; i >= 0; i--) {
        if (events[i].date && events[i].type !== "finished") {
          lastCompletedEventIndex = i;
          break;
        }
      }
      
      if (lastCompletedEventIndex !== -1) {
        const lastEvent = events[lastCompletedEventIndex];
        if (lastEvent.date) {
          const lastEventDate = parseISO(lastEvent.date);
          const today = new Date();
          const daysSinceLastEvent = differenceInDays(today, lastEventDate);
          const period = 20;
          if (daysSinceLastEvent > period) {
            return "red"; // Etapa actual pendiente y atrasada
          }
        }
      }
      return "blue"; // Etapa actual pendiente a tiempo
    } else {
      // Etapa actual completada - verificar si está atrasada
      const eventDate = parseISO(event.date);
      const today = new Date();
      const daysSinceEvent = differenceInDays(today, eventDate);
      const period = 20;
      if (daysSinceEvent > period) {
        return "red"; // Etapa actual completada pero atrasada
      }
      return "blue"; // Etapa actual completada a tiempo
    }
  }
  
  // Etapas pasadas (antes de la actual)
  if (index < currentStageIndex) {
    if (event.date) {
      // Etapa pasada completada - verificar si fue a tiempo
      const eventDate = parseISO(event.date);
      let nextEventDate = null;
      
             // Buscar la fecha del siguiente evento
       for (let i = index + 1; i < events.length; i++) {
         if (events[i].date) {
           nextEventDate = parseISO(events[i].date!);
           break;
         }
       }
      
      if (nextEventDate) {
        const daysBetween = differenceInDays(nextEventDate, eventDate);
        const period = 20;
        if (daysBetween <= period) {
          return "green"; // Etapa pasada completada a tiempo
        } else {
          return "red"; // Etapa pasada completada pero atrasada
        }
      } else {
        return "green"; // No hay siguiente evento para comparar, asumir a tiempo
      }
    } else {
      return "gray"; // Etapa pasada pendiente (no debería ocurrir)
    }
  }
  
  // Caso por defecto
  return "gray";
};

const shouldShowAsterisk = (event: { type: string; date: string | null }, index: number, events: { type: string; date: string | null }[]) => {
  // Only show asterisk for pending events that are overdue (red)
  if (event.date) {
    return false;
  }
  
  const eventColor = establishEventColor(event, index, events);
  return eventColor === "red";
};

const getEventColor = (eventColor: string) => {
  if(eventColor === "green") {
    return "bg-teal-green border-teal-green";
  }
  if(eventColor === "yellow") {
    return "bg-soft-gold border-soft-gold";
  }
  if(eventColor === "orange") {
    return "bg-soft-gold border-soft-gold";
  }
  if(eventColor === "red") {
    return "bg-red-600 border-red-600";
  }
  if(eventColor === "blue") {
    return "bg-petroleum-blue border-petroleum-blue";
  }
  return "bg-medium-gray border-medium-gray";
}

const getBarColor = (currentEvent: Event, nextEvent: Event, currentIndex: number, events: Event[]) => {
  // Encontrar la etapa actual (la primera pendiente)
  let currentStageIndex = -1;
  for (let i = 0; i < events.length; i++) {
    if (!events[i].date && events[i].type !== "finished") {
      currentStageIndex = i;
      break;
    }
  }
  
  // Si no hay etapa actual pendiente, la última completada es la actual
  if (currentStageIndex === -1) {
    for (let i = events.length - 1; i >= 0; i--) {
      if (events[i].date && events[i].type !== "finished") {
        currentStageIndex = i;
        break;
      }
    }
  }
  
  // Si la barra está después de la etapa actual, debe ser gris
  if (currentStageIndex !== -1 && currentIndex >= currentStageIndex) {
    return "bg-medium-gray";
  }
  
  // En todos los demás casos, la barra debe ser verde
  return "bg-teal-green";
};

export default function StatusBar({ receivedEvents }: StatusBarProps) {
const [hoveredEvent, setHoveredEvent] = useState<null | string>(null);

  const events = allEventTypes.map((type) => {
    const match = receivedEvents.find((e) => e.type === type);
    return { type, date: match?.date || null };
  });

  return (
    <div className="flex items-center space-x-0 p-4 gap-0">
      {events.map((event, index) => {
        const eventColor = establishEventColor(event, index, events);
        const showAsterisk = shouldShowAsterisk(event, index, events);
        
        return (
          <div key={index} className="flex items-center relative">
            <div className="relative">
              <div
                className={`relative w-5 h-5 flex items-center justify-center rounded-full border-2 z-30 
                  ${getEventColor(eventColor)}`}
                onMouseEnter={() => setHoveredEvent(event.type)}
                onMouseLeave={() => setHoveredEvent(null)}
              >
                {showAsterisk && (
                  <span className="text-white text-xs font-bold leading-none">*</span>
                )}
                {hoveredEvent === event.type && (
                  <div className={`absolute -top-10 left-1/2 transform -translate-x-1/2 ${getEventColor(eventColor)} text-white text-xs p-1 rounded shadow-md w-40 h-13 text-center`}>
                    {translatedEventNames[event.type]}
                    {event.date && <div>{formatDate(event.date)}</div>}
                  </div>
                )}
              </div>
            </div>
            {index < events.length - 1 && (
              <div className="relative w-12 sm:w-20">
                <div className="h-1 w-full flex">
                  <div className={`${getBarColor(event, events[index + 1], index, events)} w-1/2 h-full`}></div>
                  <div className={`${getBarColor(event, events[index + 1], index, events)} w-1/2 h-full`}></div>
                </div>
                <div className="absolute left-0 w-full flex justify-center mt-0">
                  <span className="text-sm text-gray-600 hidden sm:block">
                    {calculateDaysDifference(event.date, events[index + 1].date)}
                  </span>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}