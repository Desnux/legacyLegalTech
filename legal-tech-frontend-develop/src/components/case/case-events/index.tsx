import { useEffect, useState } from "react";
import { Event } from "@/types/event";
import { fetchEventDocuments, fetchEventSuggestions } from "@/services/case";
import { EventDocument } from "@/types/event-document";
import ModalDocuments from "@/components/modal/modal-documents";
import { Case, CaseEventSuggestion } from "@/types/case";
import ModalSuggestions from "@/components/modal/modal-suggestions";
import { toast } from "react-toastify";
import { partyLabels } from "@/utils/case-details";
import { formatProcedureDate } from "@/utils/date";
import { Milestone } from "@/types/milestone";

interface CaseEventsProps {
    events: Event[];
    caseId: string;
    caseData: Case;
    loadCaseData: () => void;
    milestones?: Milestone[];
    onDispatchStartDate?: (date: string | null) => void;
  }
  
  const CaseEvents: React.FC<CaseEventsProps> = ({
    events,
    caseId,
    caseData,
    loadCaseData,
    milestones = [],
    onDispatchStartDate,
  }) => {

    const [relatedEvents, setRelatedEvents] = useState<Event[]>([]);
    const [unrelatedEvents, setUnrelatedEvents] = useState<Event[]>([]);
    const [documents, setDocuments] = useState<EventDocument[]>([]);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [suggestions, setSuggestions] = useState<CaseEventSuggestion[]>([]);
    const [isModalSuggestionsVisible, setIsModalSuggestionsVisible] = useState(false);
    const [selectedEventId, setSelectedEventId] = useState<string>("");

    useEffect(() => {
        const { related, unrelated } = separateEvents(events);
        
        const sortByDate = (a: Event, b: Event) => {
          const procedureDateA = new Date(a.procedure_date || a.created_at || 0);
          const procedureDateB = new Date(b.procedure_date || b.created_at || 0);
          
          const dayA = new Date(procedureDateA);
          dayA.setHours(0, 0, 0, 0);
          const dayB = new Date(procedureDateB);
          dayB.setHours(0, 0, 0, 0);
          
          const dayComparison = dayB.getTime() - dayA.getTime();
          
          if (dayComparison === 0) {
            const createdA = new Date(a.created_at || 0).getTime();
            const createdB = new Date(b.created_at || 0).getTime();
            return createdB - createdA;
          }
          
          return dayComparison;
        };

        const sortEventsWithPriority = (events: Event[]) => {
          const demandStart = events.find(event => event.type === "demand_start");
          const dispatchStart = events.find(event => event.type === "dispatch_start");
          const otherEvents = events.filter(event => 
            event.type !== "demand_start" && event.type !== "dispatch_start"
          );
          
          if (milestones.length > 0) {
            const firstMilestone = milestones.reduce((oldest, current) => {
              const parseDate = (dateStr: string) => {
                if (dateStr.includes('-')) {
                  const [day, month, year] = dateStr.split('-');
                  return new Date(`${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`).getTime();
                }
                return new Date(dateStr).getTime();
              };
              
              const oldestDate = parseDate(oldest.procedureDate);
              const currentDate = parseDate(current.procedureDate);
              return currentDate < oldestDate ? current : oldest;
            });
            
            let dateStr = firstMilestone.procedureDate;
            if (dateStr.includes('-')) {
              const [day, month, year] = dateStr.split('-');
              dateStr = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
            }
            
            const milestoneDate = new Date(dateStr);
            if (!isNaN(milestoneDate.getTime())) {
              const formattedDate = milestoneDate.toISOString().split('T')[0]; // YYYY-MM-DD
              
              //TODO: usar la fecha real del evento
              if (demandStart) {
                demandStart.procedure_date = formattedDate;
              }
              if (dispatchStart) {
                dispatchStart.procedure_date = formattedDate;
              }
            }
          }
          if (dispatchStart) {
            onDispatchStartDate?.(dispatchStart.procedure_date || dispatchStart.created_at || null);
          } else {
            onDispatchStartDate?.(null);
          }
          
          const sortedOtherEvents = otherEvents.sort(sortByDate);
          
          const result = [];
          result.push(...sortedOtherEvents);
          if (dispatchStart) result.push(dispatchStart);
          if (demandStart) result.push(demandStart);
          
          return result;
        };
        
        setRelatedEvents(sortEventsWithPriority(related));
        setUnrelatedEvents([...unrelated].sort(sortByDate));
    }, [events, milestones, onDispatchStartDate]);

    function separateEvents(events: Event[]): { related: Event[]; unrelated: Event[] } {
        const referencedIds = new Set<string>(); // IDs que son referenciados en previous_event_id
        const idMap = new Map<string, Event>(); // Mapa de eventos por ID
    
        for (const event of events) {
          idMap.set(event.id, event);
          if (event.previous_event_id) {
            referencedIds.add(event.previous_event_id);
          }
        }
    
        const related: Event[] = [];
        const unrelated: Event[] = [];
        const processed = new Set<string>();
    
        for (const event of events) {
          if (processed.has(event.id)) continue;
    
          if (event.previous_event_id || referencedIds.has(event.id)) {
            chainEvents(event, idMap, related, processed);
          } else {
            unrelated.push(event);
            processed.add(event.id);
          }
        }
    
        return { related, unrelated };
      }

      function chainEvents(
        event: Event,
        idMap: Map<string, Event>,
        groupA: Event[],
        processed: Set<string>
      ) {
        let currentEvent: Event | null = event;
    
        while (currentEvent && !processed.has(currentEvent.id)) {
          groupA.push(currentEvent);
          processed.add(currentEvent.id);
    
          const nextEvent: Event | null = currentEvent.previous_event_id
            ? idMap.get(currentEvent.previous_event_id) || null
            : null;
    
          currentEvent = nextEvent;
        }
      }

      async function handleSeeDocumentsClick(eventId: string) {
        try {
          const documents = await fetchEventDocuments(caseId, eventId);
          setDocuments(documents);
          setIsModalVisible(true);
        } catch (error: any) {
          toast.error(error.message);
        }
      }

      async function handleEventSuggestionsClick(eventId: string) {
        try {
          const suggestions = await fetchEventSuggestions(caseId, eventId);
          setSelectedEventId(eventId);
          setSuggestions(suggestions);
          setIsModalSuggestionsVisible(true);
        } catch (error: any) {
          toast.error(error.message);
        }
      }
      

      const removeCertificationFromTitle = (title: string) => {
        if(title.includes("Diligencia:")) {
          return title.split("Diligencia:")[0].trim();
        }
        return title;
      }

      const toTitleCase = (text: string) => {
        return text.replace(/\w\S*/g, (w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());
      }

      const colorByType = (type: string, component: 'bg-event' | 'circle-event') => {
        const isBg = component === 'bg-event';
        const padding = isBg ? 'px-1 rounded-md' : '';

        const MAP: Record<string, { bg: string; dot: string }> = {
          demand_start: { bg: 'bg-[#DEECF8]/60', dot: 'bg-[#DEECF8]/60' },
          dispatch_start: { bg: 'bg-[#DEECF8]/60', dot: 'bg-[#DEECF8]/60' },
          dispatch_resolution: { bg: 'bg-[#BFE4A8]/60', dot: 'bg-[#BFE4A8]/60' },
          notification: { bg: 'bg-[#F7C6AE]/60', dot: 'bg-[#F7C6AE]/60' },
          exceptions: { bg: 'bg-[#D7D7D7]/60', dot: 'bg-[#D7D7D7]/60' },
          trial_start: { bg: 'bg-[#A6A6A6]/60', dot: 'bg-[#A6A6A6]/60' },
          legal_sentence: { bg: 'bg-[#A6A6A6]/60', dot: 'bg-[#A6A6A6]/60' },
          translation_evacuation: { bg: 'bg-[#E6D8F8]/60', dot: 'bg-[#E6D8F8]/60' },
          evacuation_translation: { bg: 'bg-[#E6D8F8]/60', dot: 'bg-[#E6D8F8]/60' },
        };
        const entry = MAP[type];
        if (entry) {
          return `${isBg ? entry.bg : entry.dot} ${padding}`;
        }
        return isBg ? '' : 'bg-gray-500';
      }

      const transformType = (type: string, title: string) => {
        switch(type) {
          case "demand_start":
            return "Abogado ingresa datos para demanda";
          case "dispatch_start":
            return "Abogado presenta demanda";
          case "exceptions":
            return "Opone Excepciones y Juez da Traslado";
          case "translation_evacuation":
            return "Evacúa Traslado (Responde a Traslado de Excepciones)";
        }
        return title;
      }

      const transformActor = (event: Event) => {
        if (event.type === "demand_start" || event.type === "dispatch_start") {
          return "Abogado";
        }
        if (event.type === "notification") {
          return "Receptor";
        }
        if(event.type === "exceptions") {
          return "Ejecutado - Juez";
        }
        if(event.type === "translation_evacuation") {
          return "Abogado";
        }
        return event.source ? partyLabels[event.source] : "Sin información";
      }

      const transformReceiver = (event: Event) => {
        if(event.type === "translation_evacuation") {
          return "Juez";
        }
        if(event.type === "demand_start") {
          return "Bandeja PJUD";
        }
        if(event.type === "dispatch_start" || event.type === "notification") {
          return "Juez";
        }
        return event.target ? partyLabels[event.target] : "Sin información";
      }

      return (  
        <> 
        {/* Sección de eventos */}
        <div className="mt-10">
          <h2 className="text-lg md:text-xl font-semibold text-gray-800 mb-3">Eventos del Caso</h2>
          <div className="relative border-l-2 mx-2 border-gray-300">
            {unrelatedEvents.map((event) => (
              <div key={event.id} className="mb-8 ml-2">
                <div className={`absolute -left-3 w-6 h-6 ${colorByType(event.type, 'circle-event')} rounded-full flex items-center justify-center`}>
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                </div>
    
                <div className={`ml-4 md:ml-6 ${colorByType(event.type, 'bg-event')} p-3 md:p-4 rounded-xl` }>
                    <h3
                      className="text-base md:text-lg font-bold text-gray-800 truncate min-w-0"
                    >
                      {toTitleCase(event.source ? `${removeCertificationFromTitle(transformType(event.type, event.title))}` : removeCertificationFromTitle(transformType(event.type, event.title)))}
                    </h3>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-3 overflow-hidden whitespace-nowrap flex-1 min-w-0">
                      <span className="text-sm text-gray-600">
                        <strong>Fecha:</strong> {event.procedure_date ? formatProcedureDate(event.procedure_date) : new Date(event.created_at).toLocaleDateString('es-CL')}
                      </span>
                      {event.content?.summary && (
                        <>
                          <span className="text-gray-300">|</span>
                          <span className="text-sm text-gray-600 truncate min-w-0" title={event.content.summary}>
                            <strong>Resumen:</strong> {event.content.summary}
                          </span>
                        </>
                      )}
                      <span className="text-gray-300">|</span>
                      <span className="text-sm text-gray-600">
                        <strong>Actúa:</strong> {transformActor(event)}
                      </span>
                      {event.type !== "trial_start" && (
                        <>
                          <span className="text-gray-300">|</span>
                          <span className="text-sm text-gray-600">
                              <strong>Recibe:</strong> {transformReceiver(event)}
                          </span>
                        </>
                      )}
                    </div>
                    <div className="ml-auto flex items-center gap-2 shrink-0">
                      {event.document_count > 0 && (
                        <button
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-cyan-700 hover:bg-blue-100 border border-blue-100"
                          onClick={() => handleSeeDocumentsClick(event.id)}
                        >
                          Ver documentos
                        </button>
                      )}
                      {event.target === "plaintiffs" && event.next_event_id === null && caseData.winner === null && (event.type === "dispatch_resolution" || event.type === "exceptions") && (
                        <button
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-cyan-700 hover:bg-blue-100 border border-blue-100"
                          onClick={() => handleEventSuggestionsClick(event.id)}
                        >
                          Alternativas de respuesta
                        </button>
                      )}
                    </div>
                  </div>

                </div>
              </div>
            ))}
          </div>
          <div className="relative border-l-2 mx-2 border-gray-300">
            {relatedEvents.map((event) => (
              <div key={event.id} className="mb-8 ml-2">
                <div className={`absolute -left-3 w-6 h-6 ${colorByType(event.type, 'circle-event')} rounded-full flex items-center justify-center`}>
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                </div>
    
                <div className={`ml-4 md:ml-6 ${colorByType(event.type, 'bg-event')} p-3 md:p-4 rounded-xl` }>
                  <h3 className="text-base md:text-lg font-bold text-gray-800 mb-1">
                      {toTitleCase(event.source ? `${transformType(event.type, event.title)}` : transformType(event.type, event.title))}
                  </h3>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-3 overflow-hidden whitespace-nowrap flex-1 min-w-0">
                    <p className="text-sm text-gray-600">
                      <strong>Fecha:</strong> {event.procedure_date ? formatProcedureDate(event.procedure_date) : new Date(event.created_at).toLocaleDateString('es-CL')}
                    </p>
                    {event.content?.summary && (
                      <>
                        <span className="text-gray-300">|</span>
                        <span className="text-sm text-gray-600 truncate min-w-0" title={event.content.summary}>
                          <strong>Resumen:</strong> {event.content.summary}
                        </span>
                      </>
                    )}
                    <span className="text-gray-300">|</span>
                    <p className="text-sm text-gray-600">
                      <strong>Actúa:</strong> {transformActor(event)}
                    </p>
                    {event.type !== "trial_start" && (
                      <>
                        <span className="text-gray-300">|</span>
                        <p className="text-sm text-gray-600">
                          <strong>Recibe:</strong> {transformReceiver(event)}
                        </p>
                      </>
                    )}
                    </div>
                    <div className="ml-auto flex items-center gap-2 shrink-0">
                      {event.document_count > 0 && (
                        <button
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-cyan-700 hover:bg-blue-100 border border-blue-100"
                          onClick={() => handleSeeDocumentsClick(event.id)}
                        >
                          Ver documentos
                        </button>
                      )}
                      {event.target === "plaintiffs" && event.next_event_id === null && (event.type === "dispatch_resolution" || event.type === "exceptions") && (
                        <button
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-cyan-700 hover:bg-blue-100 border border-blue-100"
                          onClick={() => handleEventSuggestionsClick(event.id)}
                        >
                          Alternativas de respuesta
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>


        <ModalDocuments
          title="Documentos"
          isVisible={isModalVisible}
          onClose={() => setIsModalVisible(false)}
          documents={documents}
        />

        <ModalSuggestions
          title="Alternativas de respuesta"
          isVisible={isModalSuggestionsVisible}
          caseId={caseId}
          onClose={() => setIsModalSuggestionsVisible(false)}
          suggestions={suggestions}
          onReloadSuggestions={() => {
            handleEventSuggestionsClick(selectedEventId)
            setSelectedEventId("")
          }}
          onReload={() => {loadCaseData();}}
        />
        </>
        );

  }

export default CaseEvents;
