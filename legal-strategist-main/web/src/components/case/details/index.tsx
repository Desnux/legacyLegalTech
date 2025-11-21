import React, { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import { Tooltip } from "react-tooltip";
import { IconInfoCircleFilled } from "@tabler/icons-react";
import Advent from "@/components/case/advent";
import { FullPageOverlay } from "@/components/loading";
import { Spinner } from "@/components/state";
import ModalDocuments from "@/components/modal/modal-documents";
import ModalSuggestions from "@/components/modal/modal-suggestions";
import { fetchCaseDetails, fetchCaseEvents, fetchEventDocuments, fetchEventSuggestions } from "@/services/case";
import { Case, CaseEventSuggestion } from "@/types/case";
import { Event } from "@/types/event";
import { EventDocument } from "@/types/event-document";
import "react-toastify/dist/ReactToastify.css";

type Props = {
  caseId: string;
};

const CaseDetails: React.FC<Props> = ({ caseId }) => {
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [relatedEvents, setRelatedEvents] = useState<Event[]>([]);
  const [unrelatedEvents, setUnrelatedEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingCompromise, setLoadingCompromise] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");
  const [documents, setDocuments] = useState<EventDocument[]>([]);
  const [suggestions, setSuggestions] = useState<CaseEventSuggestion[]>([]);

  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isModalSuggestionsVisible, setIsModalSuggestionsVisible] = useState(false);

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

  async function handleEventClick(eventId: string) {
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
      setSuggestions(suggestions);
      setIsModalSuggestionsVisible(true);
    } catch (error: any) {
      toast.error(error.message);
    }
  }

  const loadCaseData = async () => {
    try {
      setLoading(true);
      const data = await fetchCaseDetails(caseId);
      setCaseData(data);
      const eventList = await fetchCaseEvents(caseId);
      const { related, unrelated } = separateEvents(eventList);
      setRelatedEvents(related);
      setUnrelatedEvents(unrelated);
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCaseData();
  }, [caseId]);

  if (loading) {
    return <Spinner className="flex-1 w-full h-full" />;
  }

  if (!caseData) {
    return <p>No se encontraron detalles del caso.</p>;
  }

  const statusLabels: Record<string, string> = {
    draft: "Borrador",
    active: "Activo",
    archived: "Archivado",
    finished: "Finalizado",
  };

  const legalSubjects: Record<string, string> = {
    promissory_note_collection: "Cobro de pagaré",
    promisory_note_collection: "Cobro de pagaré",
    bill_collection: "Cobro de factura",
    general_collection: "Cumplimiento obligación de dar",
  };

  const partyLabels: Record<"plaintiffs" | "defendants" | "court" | "external_party", string> = {
    plaintiffs: "Demandantes",
    defendants: "Ejecutados",
    court: "Tribunal",
    external_party: "Terceros",
  };

  return (
    <div className="p-6 md:p-8 bg-white md:rounded-xl md:shadow-lg md:mb-4 relative">
      <div
        className="grid gap-6 md:grid-cols-3"
        style={{ gridTemplateAreas: `"details details avenimiento" "events events events"` }}
      >
        {/* Sección de detalles del caso */}
        <div className="md:col-span-2" style={{ gridArea: "details" }}>
          <div className="flex items-center">
            <h1 className="text-xl md:text-2xl font-semibold mb-4">
              {caseData.title}
            </h1>
            {caseData.simulated && false  && (
              <>
              <IconInfoCircleFilled
                data-tooltip-id="simulated-case-tooltip"
                className="text-blue-400 ml-2 cursor-help hover:text-blue-600  mb-4"
                size={24}
              />
              <Tooltip id="simulated-case-tooltip" place="top">
                Este caso es simulado
              </Tooltip>
            </>
            )}
          </div>
          <div className="mb-6">
            <p className="text-sm md:text-base">
              <strong>Materia legal:</strong> {legalSubjects[caseData.legal_subject]}
            </p>
            <p className="text-sm md:text-base">
              <strong>Estado:</strong> {statusLabels[caseData.status]}
            </p>
            <p className="text-sm md:text-base">
              <strong>Ganador:</strong> {caseData.winner ? partyLabels[caseData.winner] : "Aún no definido"}
            </p>
            <p className="text-sm md:text-base">
              <strong>Fecha de creación:</strong> {new Date(caseData.created_at).toLocaleString()}
            </p>
          </div>
        </div>
  
        {/* Componente de avenimiento */}
        <div className="hidden lg:block" style={{ gridArea: "avenimiento" }}>
          <Advent
            caseId={caseData.id}
            status={caseData.status}
            lastEvent={relatedEvents?.[relatedEvents.length - 1]?.type || 'other'}
            loading={loadingCompromise}
            setLoading={setLoadingCompromise}
            winner={caseData.winner}
            stats={caseData.stats}
          />
        </div>
      </div>
  
      {/* Sección de eventos */}
      <div className="grid grid-cols-2 gap-6 mt-6">
        <div className="relative border-l-2 mx-2 border-gray-300">
          {relatedEvents.map((event) => (
            <div key={event.id} className="mb-8 ml-2">
              <div className="absolute -left-3 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
  
              <div className="ml-4 md:ml-6">
                <h3 className="text-base md:text-lg font-bold text-gray-800 mb-1">
                  {event.source ? `${partyLabels[event.source]} - ${event.title}` : event.title}
                </h3>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Fecha:</strong> {new Date(event.created_at).toLocaleString()}
                </p>
                {event.content?.summary && (
                  <p className="text-sm text-gray-600 mb-1">
                    <strong>Resumen:</strong> {event.content.summary}
                  </p>
                )}
                {/*
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Emisor:</strong> {event.source ? partyLabels[event.source] : "Sin información"}
                </p>
                */}
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Receptor:</strong> {event.target ? partyLabels[event.target] : "Sin información"}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Documentos involucrados:</strong> {event.document_count}
                </p>
                {event.document_count > 0 && (
                  <button
                    className="mt-2 text-blue-600 hover:underline"
                    onClick={() => handleEventClick(event.id)}
                  >
                    Ver documentos
                  </button>
                )}
                <br />
                {event.target === "plaintiffs" && event.next_event_id === null && (
                  <button
                    className="mt-2 text-blue-600 hover:underline"
                    onClick={() => handleEventSuggestionsClick(event.id)}
                  >
                    Alternativas de respuesta
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
  
        <div className="relative border-l-2 border-gray-300">
          {unrelatedEvents.map((event) => (
            <div key={event.id} className="mb-8 ml-2">
              <div className="absolute -left-3 w-6 h-6 bg-cyan-500 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
  
              <div className="ml-4 md:ml-6">
                <h3 className="text-base md:text-lg font-bold text-gray-800 mb-1">
                  {event.source ? `${partyLabels[event.source]} - ${event.title}` : event.title}
                </h3>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Fecha:</strong> {new Date(event.created_at).toLocaleString()}
                </p>
                {event.content?.summary && (
                  <p className="text-sm text-gray-600 mb-1">
                    <strong>Resumen:</strong> {event.content.summary}
                  </p>
                )}
                {/*
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Emisor:</strong> {event.source ? partyLabels[event.source] : "Sin información"}
                </p>
                */}
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Receptor:</strong> {event.target ? partyLabels[event.target] : "Sin información"}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Documentos involucrados:</strong> {event.document_count}
                </p>
                {event.document_count > 0 && (
                  <button
                    className="mt-2 text-cyan-600 hover:underline"
                    onClick={() => handleEventClick(event.id)}
                  >
                    Ver documentos
                  </button>
                )}
                <br />
                {event.target === "plaintiffs" && event.next_event_id === null && caseData.winner === null && (
                  <button
                    className="mt-2 text-cyan-600 hover:underline"
                    onClick={() => handleEventSuggestionsClick(event.id)}
                  >
                    Alternativas de respuesta
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
  
      {/* Componente de avenimiento en modo móvil */}
      <div className="block lg:hidden mt-6">
        <Advent
          caseId={caseData.id}
          status={caseData.status}
          lastEvent={relatedEvents?.[relatedEvents.length - 1]?.type || 'other'}
          loading={loadingCompromise}
          setLoading={setLoadingCompromise}
          winner={caseData.winner}
        />
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
        onReload={() => {setIsModalSuggestionsVisible(false); loadCaseData();}}
      />
  
      <ToastContainer toastStyle={{ zIndex: 9999 }} />
      <FullPageOverlay isVisible={loadingCompromise} toastMessage={toastMessage} />
    </div>
  );
  
};

export default CaseDetails;
