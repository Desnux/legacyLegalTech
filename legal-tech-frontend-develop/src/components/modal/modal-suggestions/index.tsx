import { useState, useEffect, useRef } from "react";
import classNames from "classnames";
import { Modal } from "@/components/modal";
import Button from "@/components/button";
import { PDFViewer, pdf } from "@react-pdf/renderer";
import { CaseEventSuggestion } from "@/types/case";
import { Spinner } from "@/components/state";
import { FullPageOverlay } from "@/components/loading";
import { isWithdrawalStructure } from "@/types/withdrawal-structure";
import { 
  PDFLegalCompromise,
  PDFLegalExceptionResponse,
  PDFLegalResponse,
  PDFDemandTextCorrection,
  PDFWithdrawal,
} from "@/components/pdf";
import ModalSendSuggestion from "@/components/modal/modal-send-suggestion";
import ResponseTextAnalyzer from "@/components/case/generate-response/response-text";
import { ResponseTextStructure } from "@/types/response-text";
import { UpdateSuggestionResponse, updateSuggestionResponse } from "@/services/response";
import { isDemandTextCorrectionStructure, isLegalCompromiseStructure, isLegalExceptionResponseStructure, isLegalResponseStructure } from "@/utils/response-text-structure";
import { IconArrowLeft, IconCheck, IconEdit, IconSend, IconX } from "@tabler/icons-react";

interface ModalSuggestionsProps {
  title: string;
  isVisible: boolean;
  caseId: string;
  onClose: () => void;
  onReload: () => void;
  onReloadSuggestions: () => void;
  suggestions: CaseEventSuggestion[];
}

const ModalSuggestions: React.FC<ModalSuggestionsProps> = ({ title, isVisible, caseId, onClose, onReload, onReloadSuggestions, suggestions }) => {
  const [selectedDocument, setSelectedDocument] = useState<CaseEventSuggestion | null>(null);
  const [docLoading, setDocLoading] = useState(false);
  const [sendSuggestion, setSendSuggestion] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");
  const [eventId, setEventId] = useState<string>("");
  const [suggestionId, setSuggestionId] = useState<string>("");
  const [suggestion, setSuggestion] = useState<CaseEventSuggestion | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState<ResponseTextStructure | null>(null);
  const pdfDocument = useRef<Blob | null>(null);

  const handleBackToList = () => {
    setSelectedDocument(null);
    setIsEditing(false);
  };
  
  const handleToClose = () => {
    setSelectedDocument(null);
    setIsEditing(false);
    onClose();
  };

  const handleToReload = () => {
    setSelectedDocument(null);
    setIsEditing(false);
    onReload();
  }

  const handleSelectDocument = (documento: CaseEventSuggestion) => {
    setSelectedDocument(documento);
    setEventId(documento.case_event_id);
    setSuggestionId(documento.id);
  };

  const handleEdit = () => {
    if (selectedDocument && selectedDocument.content) {
      setEditedContent({
        header: selectedDocument.content.header || null,
        summary: selectedDocument.content.summary || "",
        court: selectedDocument.content.court || "",
        opening: selectedDocument.content.opening || null,
        compromise_terms: selectedDocument.content.compromise_terms || null,
        exception_responses: selectedDocument.content.exception_responses || undefined,
        main_request: selectedDocument.content.main_request || "",
        additional_requests: selectedDocument.content.additional_requests || null,
        content: selectedDocument.content.content || null,
      });
      setIsEditing(true);
    }
  };

  const handleExitEdit = () => {
    setEditedContent(null);
    setIsEditing(false);
  };

  const fnSendSuggestion = async (suggestion: CaseEventSuggestion | null) => {
    if (!suggestion) {
      return;
    }
    setSuggestion(suggestion);
  };

  const renderDocumentContent = (document: CaseEventSuggestion) => {
    if (!document.content) {
      return (
        <div className="flex items-center justify-center h-48">
          <p className="text-center text-gray-500">Documento no disponible.</p>
        </div>
      );
    }
  
    switch (document.type) {
      case "response":
        if (isLegalResponseStructure(document.content)) {
          const {
            header,
            court,
            response,
            request
          } = document.content;
          
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFLegalResponse
                header={header}
                court={court}
                response={response}
                request={request}
              />
            </PDFViewer>
          );
        }
        break;
      case "exceptions_response":
          if (isLegalExceptionResponseStructure(document.content)) {
            const {
              summary,
              court,
              opening,
              exception_responses,
              main_request,
              additional_requests
            } = document.content;
            
            return (
              <PDFViewer className="h-[65vh] w-full">
                <PDFLegalExceptionResponse
                  summary={summary}
                  court={court}
                  opening={opening}
                  exception_responses={exception_responses}
                  main_request={main_request}
                  additional_requests={additional_requests}
                />
              </PDFViewer>
            );
          }
          break;
      case "compromise":
        if (isLegalCompromiseStructure(document.content)) {
          const {
            header,
            summary,
            court,
            opening,
            compromise_terms,
            main_request,
            additional_requests
          } = document.content;
          
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFLegalCompromise
                header={header}
                summary={summary}
                court={court}
                opening={opening}
                compromise_terms={compromise_terms}
                main_request={main_request}
                additional_requests={additional_requests}
              />
            </PDFViewer>
          );
        }
        break;
      case "withdrawal":
        if (isWithdrawalStructure(document.content)) {
          const {
            header,
            summary,
            court,
            content,
            main_request,
          } = document.content;
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFWithdrawal
                header={header}
                summary={summary}
                court={court}
                content={content}
                main_request={main_request}
              />
            </PDFViewer>
          );
        }
      case "demand_text_correction":
        if (isDemandTextCorrectionStructure(document.content)) {
          const {
            summary,
            court = "",
            opening,
            corrections,
            main_request,
            additional_requests

          } = document.content;
          
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFDemandTextCorrection
                summary={summary}
                court={court}
                opening={opening}
                corrections={corrections}
                main_request={main_request}
                additional_requests={additional_requests}
              />
            </PDFViewer>
          );
        }
        break;
      default:
        break;
    }
  
    return (
      <div className="flex items-center justify-center h-48">
        <p className="text-center text-gray-500">
          Visualizador no disponible para este tipo de documento.
        </p>
      </div>
    );
  };

  if (docLoading) {
    return <Spinner className="flex-1 w-full h-full" />;
  }

  //TODO: IMPROVE CODE
  useEffect(() => {
    const generatePdfBlob = async () => {
      if (suggestion) {
        if (suggestion.type === "response" && isLegalResponseStructure(suggestion.content)) {
          const {
            header,
            court,
            response,
            request
          } = suggestion.content;
          const pdfInstance = pdf(
            <PDFLegalResponse
              header={header}
              court={court}
              response={response}
              request={request}
            />
          );
          const blob = await pdfInstance.toBlob();
          pdfDocument.current = blob;
        }

        if (suggestion.type === "exceptions_response" && isLegalExceptionResponseStructure(suggestion.content)) {
          const {
            summary,
            court,
            opening,
            exception_responses,
            main_request,
            additional_requests
          } = suggestion.content;
          const pdfInstance = pdf(
            <PDFLegalExceptionResponse
              summary={summary}
              court={court}
              opening={opening}
              exception_responses={exception_responses}
              main_request={main_request}
              additional_requests={additional_requests}
            />
          );
          const blob = await pdfInstance.toBlob();
          pdfDocument.current = blob;
        }

        if (suggestion.type === "compromise" && isLegalCompromiseStructure(suggestion.content)) {
          const {
            header,
            summary,
            court,
            opening,
            compromise_terms,
            main_request,
            additional_requests
          } = suggestion.content;
          const pdfInstance = pdf(
            <PDFLegalCompromise
              header={header}
              summary={summary}
              court={court}
              opening={opening}
              compromise_terms={compromise_terms}
              main_request={main_request}
              additional_requests={additional_requests}
            />
          );
          const blob = await pdfInstance.toBlob();
          pdfDocument.current = blob;
        }

        if (suggestion.type === "demand_text_correction" && isDemandTextCorrectionStructure(suggestion.content)) {
          const {
            summary,
            court = "",
            opening,
            corrections,
            main_request,
            additional_requests

          } = suggestion.content;
          const pdfInstance = pdf(
            <PDFDemandTextCorrection
              summary={summary}
              court={court}
              opening={opening}
              corrections={corrections}
              main_request={main_request}
              additional_requests={additional_requests}
            />
          );
          const blob = await pdfInstance.toBlob();
          pdfDocument.current = blob;
        }

        if (suggestion.type == "withdrawal" && isWithdrawalStructure(suggestion.content)) {
          const {
            header,
            summary,
            court,
            content,
            main_request,
          } = suggestion.content;
          const pdfInstance = pdf(
            <PDFWithdrawal
              header={header}
              summary={summary}
              court={court}
              content={content}
              main_request={main_request}
            />
          );
          const blob = await pdfInstance.toBlob();
          pdfDocument.current = blob;
        }
        
        setEventId(suggestion.case_event_id);
        setSuggestionId(suggestion.id);
        setSendSuggestion(true);
      }
    }

    generatePdfBlob();
  }, [suggestion]);

  useEffect(() => {
    if (suggestions.length > 0) {
      setSelectedDocument(suggestions[0]);
      setTimeout(() => setSelectedDocument(null), 1000);
    }
  },[]);

  const maxScore = suggestions.length > 0 ? Math.max(...suggestions.map(doc => doc.score)) : 0;
  const doNothingScore = 1.0 - maxScore;
  const suggestionsSum = suggestions.reduce((sum, doc) => sum + doc.score, 0);
  const totalScore = suggestionsSum + doNothingScore;

  const handleUpdateSuggestion = async () => {
    if (!selectedDocument || !suggestionId || !eventId) {
      console.log("Faltan datos para actualizar la sugerencia");
      return;
    }
    const suggestionUpdate: UpdateSuggestionResponse = {
      name: selectedDocument.name,
      content: editedContent as ResponseTextStructure,
      score: selectedDocument.score,
    };
    try {
      await updateSuggestionResponse(caseId, suggestionId, eventId, suggestionUpdate);
      setIsEditing(false);
      setEditedContent(null);
      setSelectedDocument(null);
      onReloadSuggestions()
    } catch (error) {
      console.error("Error al actualizar la sugerencia:", error);
    } finally {
    }
  };

  return (
    <>
      <Modal
        className={classNames("max-h-[90vh] overflow-hidden text-gray-900")}
        customWidthClassName={"w-[90vw] max-w-[950px]"}
        isVisible={isVisible}
        onClose={handleToClose}
        title={selectedDocument ? selectedDocument.name : title}
        footer={
          selectedDocument && !isEditing ? (
            <div className="flex justify-between space-x-2">
                <Button 
                  variant="secondary"
                  icon={<IconArrowLeft name="arrow-left" />}
                  onClick={handleBackToList}>
                  Volver a la lista
                </Button>
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="warning"
                    disabled={selectedDocument.content === null}
                    type="button"
                    icon={<IconEdit name="edit" />}
                    onClick={handleEdit}
                  >
                    Editar
                  </Button>
                  
                  <Button
                    variant="primary"
                    disabled={selectedDocument.content === null}
                    type="button"
                    onClick={() => fnSendSuggestion(selectedDocument)}
                    icon={<IconSend name="send" />}
                  >
                    Enviar alternativa
                  </Button>
       
                </div>
            </div>
          ) : isEditing ? (
            <div className="flex justify-end space-x-2">
              <Button 
                variant="danger" 
                onClick={handleExitEdit}
                icon={<IconX name="x" />}
                >
                Cancelar Edición
              </Button>
              <Button 
                variant="primary"
                onClick={handleUpdateSuggestion}
                icon={<IconCheck name="check" />}
              >
                Guardar
              </Button>
            </div>
          ) : (
            <div className="flex justify-end space-x-2">
                <Button variant="secondary" onClick={onClose}>
                  Cerrar
                </Button>
            </div>
          )
        }
      >
        {isEditing && editedContent && selectedDocument && (
          <div className="h-full max-h-[60vh] overflow-y-auto">
            <div className="h-full overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
              <ResponseTextAnalyzer
                input={editedContent}
                onContentChange={setEditedContent}
                className="h-auto min-h-full"
              />
            </div>
          </div>
        )} 
        
        {!selectedDocument && suggestions && suggestions.length > 0 && (
          <div className="overflow-y-auto max-h-[60vh] mb-4">
            {suggestions && suggestions.length > 0 && (
               <>
                <div className="flex items-center justify-between px-4 py-2 font-bold text-sm text-gray-700">
                  <span>Nombre</span>
                  <span>Recomendación relativa</span>
                </div>
                <ul className="divide-y divide-gray-200">
                  {suggestions.map((doc) => {
                    const normalizedScore = totalScore > 0 ? doc.score / totalScore : 0;
                    return (
                      <li key={doc.id} className="py-2 cursor-pointer" onClick={() => handleSelectDocument(doc)}>
                        <div className="flex items-center justify-between w-full px-4 py-2 hover:bg-gray-100 rounded-md">
                          {/* Div con el onClick para doc.name */}
                          <div
                            className="flex-1"
                            onClick={() => handleSelectDocument(doc)}
                          >
                            <span>{doc.name}</span>
                          </div>

                          {/* Div para doc.score y el botón guardar */}
                          <div
                            className="flex items-center space-x-2"
                          >
                            <span
                              className="text-right"
                            >
                              {new Intl.NumberFormat("es-ES", {
                                style: "percent",
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              }).format(normalizedScore)}
                            </span>
                          </div>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              </>
            )} 
            {suggestions && suggestions.length === 0 && (
              <div className="flex items-center justify-center h-48">
                <p className="text-center text-gray-500">
                  No hay sugerencias para este evento.
                </p>
              </div>
            )}
          </div>
        )}
        {selectedDocument && !isEditing && (
          renderDocumentContent(selectedDocument)
        )}
      </Modal>
      { sendSuggestion && (
        <ModalSendSuggestion
          caseId={caseId}
          eventId={eventId}
          alternativeId={suggestionId}
          file={pdfDocument.current as Blob}
          onClose={() => setSendSuggestion(false)}
          onSuccess={() => handleToReload()}
        />
      )}
      <FullPageOverlay isVisible={docLoading} toastMessage={toastMessage} />
    </>
  );
};

export default ModalSuggestions;
