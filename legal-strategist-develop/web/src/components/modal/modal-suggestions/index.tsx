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
import { isWithdrawalStructure } from "@/types/withdrawal-structure";
import { 
  PDFLegalCompromise,
  PDFLegalExceptionResponse,
  PDFLegalResponse,
  PDFDemandTextCorrection,
  PDFWithdrawal,
} from "@/components/pdf";
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
    (typeof content.header === "string" || content.header === null) &&
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
              <button
                disabled={selectedDocument.content === null}
                type="button"
                onClick={() => fnSendSuggestion(selectedDocument)}
                className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Enviar alternativa
              </button>
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
            {suggestions && suggestions.length > 0 ? (
               <>
                <div className="flex items-center justify-between px-4 py-2 font-bold text-sm text-gray-700">
                  <span>Nombre</span>
                  <span>Recomendación relativa</span>
                </div>
                <ul className="divide-y divide-gray-200">
                  {suggestions.map((doc) => {
                    const normalizedScore = totalScore > 0 ? doc.score / totalScore : 0;
                    return (
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
                              className="text-right cursor-pointer"
                              onClick={() => setSelectedDocument(doc)}
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
            ) : (
              <div className="flex items-center justify-center h-48">
                <p className="text-center text-gray-500">
                  No hay sugerencias para este evento.
                </p>
              </div>
            )}
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
