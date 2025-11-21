import { useState, useEffect, useRef } from "react";
import classNames from "classnames";
import { Modal } from "@/components/modal";
import { ButtonSecondary } from "@/components/button";
import { PDFViewer, pdf } from "@react-pdf/renderer";
import { CaseEventSuggestion } from "@/types/case";
import { Spinner } from "@/components/state";
import { FullPageOverlay } from "@/components/loading";
import { LegalExceptionResponseStructure } from "@/types/legal-exception-response-structure";
import { LegalResponseStructure } from "@/types/legal-response-structure";
import { LegalCompromiseStructure } from "@/types/legal-compromise-structure";
import { DemandTextCorrectionStructure } from "@/types/demand-text-correction-structure";
import { PDFLegalCompromise, PDFLegalExceptionResponse, PDFLegalResponse, PDFDemandTextCorrection } from "@/components/pdf";
import ModalSendSuggestion from "@/components/modal/modal-send-suggestion";

function isLegalResponseStructure(content: any): content is LegalResponseStructure {
  return (
    (typeof content.header === "string" || content.header === null) &&
    (typeof content.court === "string" || content.court === null) &&
    (typeof content.response === "string" || content.response === null) &&
    (typeof content.request === "string" || content.request === null)
  );
}

function isLegalExceptionResponseStructure(content: any): content is LegalExceptionResponseStructure {
  return (
    (typeof content.summary === "string" || content.summary === null) &&
    (typeof content.court === "string" || content.court === null) &&
    (typeof content.opening === "string" || content.opening === null) &&
    (Array.isArray(content.exception_responses) || content.exception_responses === null) &&
    (typeof content.main_request === "string" || content.main_request === null) &&
    (typeof content.additional_requests === "string" || content.additional_requests === null)
  );
}

function isLegalCompromiseStructure(content: any): content is LegalCompromiseStructure {
  return (
    (typeof content.summary === "string" || content.summary === null) &&
    (typeof content.court === "string" || content.court === null) &&
    (typeof content.opening === "string" || content.opening === null) &&
    (typeof content.compromise_terms === "string" || content.compromise_terms === null) &&
    (typeof content.main_request === "string" || content.main_request === null) &&
    (typeof content.additional_requests === "string" || content.additional_requests === null)
  );
}

function isDemandTextCorrectionStructure(content: any): content is DemandTextCorrectionStructure {
  return (
    (typeof content.summary === "string" || content.summary === null) &&
    (typeof content.court === "string" || content.court === null) &&
    (typeof content.opening === "string" || content.opening === null) &&
    (typeof content.corrections === "string" || content.corrections === null) &&
    (typeof content.main_request === "string" || content.main_request === null) &&
    (typeof content.additional_requests === "string" || content.additional_requests === null)
  );
}

interface ModalSuggestionsProps {
  title: string;
  isVisible: boolean;
  caseId: string;
  onClose: () => void;
  onReload: () => void;
  suggestions: CaseEventSuggestion[];
}

const ModalSuggestions: React.FC<ModalSuggestionsProps> = ({ title, isVisible, caseId, onClose, onReload, suggestions }) => {
  const [selectedDocument, setSelectedDocument] = useState<CaseEventSuggestion | null>(null);
  const [docLoading, setDocLoading] = useState(false);
  const [sendSuggestion, setSendSuggestion] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");
  const [eventId, setEventId] = useState<string>("");
  const [suggestionId, setSuggestionId] = useState<string>("");
  const [suggestion, setSuggestion] = useState<CaseEventSuggestion | null>(null);
  const pdfDocument = useRef<Blob | null>(null);

  const handleBackToList = () => {
    setSelectedDocument(null);
  };
  
  const handleToClose = () => {
    setSelectedDocument(null);
    onClose();
  };

  const handleToReload = () => {
    setSelectedDocument(null);
    onReload();
  }

  const fnSendSuggestion = async (index: number) => {
    const suggestion = suggestions[index];
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
            summary,
            court,
            opening,
            compromise_terms,
            main_request,
            additional_requests
          } = suggestion.content;
          const pdfInstance = pdf(
            <PDFLegalCompromise
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

  // TODO: Remove artificial suggestions
  const finalSuggestions: CaseEventSuggestion[] = [
    ...suggestions,
    {
      id: "e5792562-00c5-44c6-acaa-8b84019c200d",
      case_event_id: "adcbe00f-49f7-4cd6-9e9e-84ea13846313",
      name: "Avenimiento",
      type: "compromise",
      content: null,
      storage_key: null,
      score: 0.2,
    },
    {
      id: "6e1d4e01-53b4-4039-ba50-b159f1679e3e",
      case_event_id: "adcbe00f-49f7-4cd6-9e9e-84ea13846313",
      name: "Desistimiento",
      type: "other",
      content: null,
      storage_key: null,
      score: 0.1,
    }
  ]


  return (
    <>
      <Modal
        className={classNames("max-h-[90vh] overflow-hidden text-gray-900")}
        customWidthClassName={"w-[90vw] max-w-[950px]"}
        isVisible={isVisible}
        onClose={handleToClose}
        title={selectedDocument ? selectedDocument.name : title}
        footer={
          selectedDocument ? (
            <div className="flex justify-end space-x-2">
              <ButtonSecondary label="Volver a la lista" onClick={handleBackToList} />
            </div>
          ) : (
            <div className="flex justify-end space-x-2">
              <ButtonSecondary label="Cerrar" onClick={onClose} />
            </div>
          )
        }
      >
        {!selectedDocument ? (
          <div className="overflow-y-auto max-h-[60vh] mb-4">
            <ul className="divide-y divide-gray-200">
              {finalSuggestions.map((doc, index) => (
                <li key={doc.id} className="py-2">
                  <div className="flex items-center justify-between w-full px-4 py-2 hover:bg-gray-100 rounded-md">
                    {/* Div con el onClick para doc.name */}
                    <div
                      className="flex-1 cursor-pointer"
                      onClick={() => setSelectedDocument(doc)}
                    >
                      <span>{doc.name}</span>
                    </div>

                    {/* Div para doc.score y el botón guardar */}
                    <div
                      className="flex items-center space-x-2"
                    >
                      <span
                        className="text-right mr-6 cursor-pointer"
                        onClick={() => setSelectedDocument(doc)}
                      >
                        {new Intl.NumberFormat('es-ES', {
                          style: 'percent',
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 2,
                        }).format(doc.score)}
                      </span>
                      <button
                        disabled={doc.content === null}
                        type="button"
                        onClick={() => fnSendSuggestion(index)}
                        className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        Enviar alternativa
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
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
