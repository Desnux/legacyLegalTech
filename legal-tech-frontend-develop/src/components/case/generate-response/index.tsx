"use client";

import { useState } from "react";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { IconEdit, IconFileText, IconArrowLeft, IconX, IconRefresh, IconCheck } from "@tabler/icons-react";
import Modal from "@/components/modal/modal";
import ResponseTextInputExtractor from "./response-text-input-extractor";
import { extractResponseDispatchResolutionTextInput, extractResponseExceptionTextInput, Suggestion, UpdateSuggestionResponse, updateSuggestionResponse, type SuggestionResponse } from "@/services/response";
import { ResponseTextInputInformation, ResponseTextStructure } from "@/types/response-text";
import ResponseTextAnalyzer from "./response-text";
import ResponseTextSuggestions from "./response-text-suggestions";

interface GenerateResponseProps {
  isVisible: boolean;
  onClose: () => void;
  onReload?: () => void;
  caseId: string;
}

const TAB_CLASSNAME = "flex items-center space-x-2 px-4 py-3 text-body-sm font-medium text-charcoal-gray hover:text-teal-green hover:bg-light-gray rounded-lg transition-all duration-200 cursor-pointer select-none";
const TAB_CLASSNAME_DISABLED = "flex items-center space-x-2 px-4 py-3 text-body-sm font-medium text-medium-gray cursor-not-allowed select-none";

const GenerateResponse: React.FC<GenerateResponseProps> = ({ isVisible, onClose, onReload, caseId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [responseTextInputExtractorResponse, setResponseTextInputExtractorResponse] = useState<ResponseTextInputInformation | null>(null);
  const [loadingExtraction, setLoadingExtraction] = useState<boolean>(false);
  const [selectedEventType, setSelectedEventType] = useState<string>("exceptions");
  const [responseTextStructure, setResponseTextStructure] = useState<ResponseTextStructure | null>(null);
  const [initialResponseTextStructure, setInitialResponseTextStructure] = useState<ResponseTextStructure | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState<Suggestion | null>(null);
  const [eventId, setEventId] = useState<string>("");
  const [isEditing, setIsEditing] = useState(false);

  const handleClose = () => {
    if (suggestions.length > 0 && onReload) {
      onReload();
    }
    setResponseTextStructure(null);
    setInitialResponseTextStructure(null);
    setSuggestions([]);
    setSelectedSuggestion(null);
    setEventId("");
    setIsEditing(false);
    setSelectedEventType("exceptions");
    setActiveTab(0);
    onClose();
  };

  const hasChanges = (): boolean => {
    if (!responseTextStructure || !initialResponseTextStructure) return false;
    return JSON.stringify(responseTextStructure) !== JSON.stringify(initialResponseTextStructure);
  };

  const handleResetChanges = () => {
    if (initialResponseTextStructure) {
      setResponseTextStructure(initialResponseTextStructure);
    }
  };

  const onExtractorPDFSubmit = async (data: ResponseTextInputInformation) => {
    if (loadingExtraction) {
      return;
    }
    setLoadingExtraction(true);
    try {
      let res: SuggestionResponse;
      if (selectedEventType === "exceptions") {
        res = await extractResponseExceptionTextInput(caseId, data.files);
      } else if (selectedEventType === "dispatch_resolution") {
        res = await extractResponseDispatchResolutionTextInput(caseId, data.files);
      } else {
        throw new Error("Event type not supported");
      }
      console.log(res);
      if (res?.suggestions && res.suggestions.length > 0) {
        setSuggestions(res.suggestions);
        setEventId(res.event_id);
        setSelectedSuggestion(null);
        setIsEditing(false);
        setActiveTab(1);
      } else {
        throw new Error("No suggestions found");
      }
    } catch (e) {
      console.error("Error en extracción:", e);
    } finally {
      setLoadingExtraction(false);
    }
  };

  const handleUpdateSuggestion = async (suggestionId: string, suggestion: ResponseTextStructure) => {
    if (loading) {
      return;
    }
    if (!selectedSuggestion) {
      return;
    }
    const suggestionUpdate: UpdateSuggestionResponse = {
      name: selectedSuggestion.name,
      content: suggestion,
      score: selectedSuggestion.score,
    };
    setLoading(true);
    try {
      await updateSuggestionResponse(caseId, suggestionId, eventId, suggestionUpdate);
      
      setSuggestions(prevSuggestions => 
        prevSuggestions.map(sug => 
          sug.id === suggestionId 
            ? { ...sug, content: suggestion }
            : sug
        )
      );
      
      setSelectedSuggestion(null);
      setIsEditing(false);
    } catch (error) {
      console.error("Error al actualizar la sugerencia:", error);
    } finally {
      setLoading(false);
    }
  };

return (
    <Modal
      isVisible={isVisible}
      onClose={handleClose}
      title="Generar Respuesta"
      className="max-h-[90vh] overflow-hidden"
      customWidthClassName="max-w-4xl w-full"
    >
        {/* Contenido Principal */}
        <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray overflow-hidden flex flex-col w-full h-full max-h-[calc(90vh-120px)]">
          {/* Tabs */}
          <Tabs 
            className="flex flex-col h-full"
            selectedTabClassName="text-teal-green bg-teal-green/10 border-b-2 border-teal-green"
            selectedTabPanelClassName="h-full flex-1"
            selectedIndex={activeTab}
            onSelect={index => setActiveTab(index)}
          >
            <TabList className="flex gap-x-1 p-6 border-b border-medium-gray bg-light-gray">
              <Tab className={TAB_CLASSNAME}>
                <IconFileText size={18} />
                <span>Generar</span>
              </Tab>
              <Tab
                className={suggestions.length === 0 ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
                disabled={suggestions.length === 0}
              >
                <IconEdit size={18} />
                <span>Análisis y Ajustes</span>
              </Tab>
            </TabList>

            {/* Paneles de Contenido */}
            <div className="p-4 flex-1 flex flex-col overflow-hidden min-h-0 max-h-[calc(90vh-200px)]">
              <TabPanel forceRender>
                <div className="overflow-y-auto h-full pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                  <ResponseTextInputExtractor
                    className={activeTab === 0 ? "" : "hidden"}
                    loading={loading}
                    extractionLoading={loadingExtraction}
                    onExtractorPDFSubmit={onExtractorPDFSubmit}
                    extractedPdfInformation={responseTextInputExtractorResponse ?? undefined}
                    selectedEventType={selectedEventType}
                    setSelectedEventType={setSelectedEventType}
                  />
                </div>
              </TabPanel>
              
              <TabPanel>
                {isEditing && responseTextStructure && selectedSuggestion && (
                  <div className="flex flex-col h-full max-h-[60vh]">
                    <div className="mb-4 pb-4 border-b border-gray-200  flex-shrink-0">
                      <div className="flex gap-2">
                        <button
                          onClick={() => setIsEditing(false)}
                          className="px-3 py-1 text-sm bg-red-100 text-gray-700 rounded-md hover:bg-red-200 flex items-center gap-2"
                        >
                          <IconX size={16} />
                          Cancelar Edición
                        </button>
                        <button
                          onClick={() => handleUpdateSuggestion(selectedSuggestion.id, responseTextStructure)}
                          disabled={!hasChanges() || !selectedSuggestion}
                          className="px-3 py-1 text-sm bg-green-100 text-gray-700 rounded-md hover:bg-green-200 flex items-center gap-2"
                        >
                          <IconCheck size={16} />
                          Guardar Cambios
                        </button>
                        {hasChanges() && (
                          <button
                            onClick={handleResetChanges}
                            className="px-3 py-1 text-sm bg-yellow-100 text-gray-700 rounded-md hover:bg-yellow-200 flex items-center gap-2"
                          >
                            <IconRefresh size={16} />
                            Restablecer Cambios
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="flex-1 overflow-y-auto">
                      <ResponseTextAnalyzer
                        input={responseTextStructure}
                        onContentChange={setResponseTextStructure}
                        className="h-auto min-h-full"
                      />
                    </div>
                  </div>
                )} 
                
                {selectedSuggestion && !isEditing && (
                  <div className="flex flex-col h-full max-h-[60vh] overflow-y-auto">
                    <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-200 flex-shrink-0">
                      <div className="flex gap-2">
                        <button
                          onClick={() => setSelectedSuggestion(null)}
                          className="px-3 py-1 text-sm bg-green-100 text-gray-700 rounded-md hover:bg-green-200 flex items-center gap-2"
                        >
                          <IconArrowLeft size={16} />
                          Volver a la lista
                        </button>
                        <button
                          onClick={() => {
                            const initialStructure = {
                              header: selectedSuggestion.content.header || null,
                              summary: selectedSuggestion.content.summary || "",
                              court: selectedSuggestion.content.court || "",
                              opening: selectedSuggestion.content.opening || null,
                              compromise_terms: selectedSuggestion.content.compromise_terms || null,
                              exception_responses: selectedSuggestion.content.exception_responses || undefined,
                              main_request: selectedSuggestion.content.main_request || "",
                              additional_requests: selectedSuggestion.content.additional_requests || null,
                              content: selectedSuggestion.content.content || null,
                            };
                            setResponseTextStructure(initialStructure);
                            setInitialResponseTextStructure(initialStructure);
                            setIsEditing(true);
                          }}
                          className="px-3 py-1 text-sm bg-blue-100 text-gray-700 rounded-md hover:bg-blue-200 flex items-center gap-2"
                        >
                          <IconEdit size={16} />
                          Editar
                        </button>
                      </div>
                    </div>
                    <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                      <ResponseTextAnalyzer
                        input={{
                          header: selectedSuggestion.content.header || null,
                          summary: selectedSuggestion.content.summary || "",
                          court: selectedSuggestion.content.court || "",
                          opening: selectedSuggestion.content.opening || null,
                          compromise_terms: selectedSuggestion.content.compromise_terms || null,
                          exception_responses: selectedSuggestion.content.exception_responses || undefined,
                          main_request: selectedSuggestion.content.main_request || "",
                          additional_requests: selectedSuggestion.content.additional_requests || null,
                          content: selectedSuggestion.content.content || null,
                        }}
                        readOnly={true}
                        className="h-auto min-h-full"
                      />
                    </div>
                  </div>
                )} 
                
                {suggestions.length > 0 && !isEditing && !selectedSuggestion && (
                    <ResponseTextSuggestions
                      suggestions={suggestions}
                      setSelectedSuggestion={setSelectedSuggestion}
                    />
                )} 
                
                {suggestions.length === 0 && (
                  <div className="flex-1 text-charcoal-gray flex h-64 justify-center text-body items-center text-center p-8 bg-light-gray rounded-xl">
                    Extraiga información del PDF para ver y editar el texto de respuesta.
                  </div>
                )}
              </TabPanel>
            </div>
          </Tabs>
        </div>
    </Modal>
  );
};

export default GenerateResponse;
