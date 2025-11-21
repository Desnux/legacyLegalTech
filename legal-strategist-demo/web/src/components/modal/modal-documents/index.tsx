import { useState, useEffect } from "react";
import classNames from "classnames";
import { Modal } from "@/components/modal";
import { ButtonSecondary } from "@/components/button";
import { format } from "date-fns";
import { PDFViewer } from "@react-pdf/renderer";
import { 
  PDFLegalCompromise,
  PDFLegalExceptionResponse, 
  PDFLegalResponse, 
  PDFLegalResolution,
  PDFDemandException,
  PDFDemandText,
  PDFDemandTextCorrection,
  PDFDispatchResolution,
} from "@/components/pdf";
import { MissingPaymentArgument } from "@/types/demand-text";
import { LegalExceptionResponseStructure } from "@/types/legal-exception-response-structure";
import { LegalResponseStructure } from "@/types/legal-response-structure";
import { LegalResolutionStructure } from "@/types/legal-resolution-structure";
import { LegalCompromiseStructure } from "@/types/legal-compromise-structure";
import { DemandTextCorrectionStructure } from "@/types/demand-text-correction-structure";
import { Spinner } from "@/components/state";
import { FullPageOverlay } from "@/components/loading";

interface Document {
  id: string;
  name: string;
  created_at: string;
  type: string;
  content: Record<string, any> | null;
}

interface DemandTextStructure {
  header: string | null;
  summary: string | null;
  court: string | null;
  opening: string | null;
  missing_payment_arguments: MissingPaymentArgument[] | null;
  main_request: string | null;
  additional_requests: string | null;
}

interface DispatchResolutionStructure {
  header: string | null;
  date_line: string | null;
  resolution: string | null;
  footer: string | null;
}

interface DemandExceptionStructure {
  header: string | null;
  court: string | null | undefined;
  opening: string | null;
  summary: string | null;
  exceptions: string | null;
  main_request: string | null;
  additional_requests: string | null;
}

function isDemandTextStructure(content: any): content is DemandTextStructure {
  return (
    typeof
      content.header === "string" ||
      content.header === null &&
    typeof
      content.summary === "string" ||
      content.summary === null &&
    typeof
      content.court === "string" ||
      content.court === null &&
    typeof
      content.opening === "string" ||
      content.opening === null &&
    Array.isArray(content.missing_payment_arguments) &&
    typeof
      content.main_request === "string" ||
      content.main_request === null &&
    typeof
      content.additional_requests === "string" ||
      content.additional_requests === null
  );
}

function isDispatchResolutionStructure(content: any): content is DispatchResolutionStructure {
  return (
    typeof
      content.header === "string" ||
      content.header === null &&
    typeof
      content.date_line === "string" ||
      content.date_line === null &&
    typeof
      content.resolution === "string" ||
      content.resolution === null &&
    typeof
      content.footer === "string" ||
      content.footer === null
  );
}

function isLegalResolutionStructure(content: any): content is LegalResolutionStructure {
  return (
    typeof
      content.header === "string" ||
      content.header === null &&
    typeof
      content.date_line === "string" ||
      content.date_line === null &&
    typeof
      content.resolution === "string" ||
      content.resolution === null &&
    typeof
      content.footer === "string" ||
      content.footer === null
  );
}

function isDemandExceptionStructure(content: any): content is DemandExceptionStructure {
  return (
    typeof
      content.header === "string" ||
      content.header === null &&
    typeof
      content.court === "string" ||
      content.court === null &&
    typeof
      content.opening === "string" ||
      content.opening === null &&
    typeof
      content.summary === "string" ||
      content.summary === null &&
    typeof
      content.exceptions === "string" ||
      content.exceptions === null &&
    typeof
      content.main_request === "string" ||
      content.main_request === null &&
    typeof
      content.additional_requests === "string" ||
      content.additional_requests === null
  );
}

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

interface ModalDocumentsProps {
  title: string;
  isVisible: boolean;
  onClose: () => void;
  documents: Document[];
}

const ModalDocuments = ({ title, isVisible, onClose, documents }: ModalDocumentsProps) => {
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [docLoading, setDocLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");

  const handleBackToList = () => {
    setSelectedDocument(null);
  };
  
  const handleToClose = () => {
    setSelectedDocument(null);
    onClose();
  };

  const renderDocumentContent = (document: Document) => {
    if (!document.content) {
      return (
        <div className="flex items-center justify-center h-48">
          <p className="text-center text-gray-500">Documento no disponible.</p>
        </div>
      );
    }
  
    switch (document.type) {
      case "demand_text":
        if (isDemandTextStructure(document.content)) {
          const {
            header,
            summary,
            court,
            opening,
            missing_payment_arguments,
            main_request,
            additional_requests,
          } = document.content;
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFDemandText
                header={header}
                summary={summary}
                court={court}
                opening={opening}
                missing_payment_arguments={missing_payment_arguments}
                main_request={main_request}
                additional_requests={additional_requests}
              />
            </PDFViewer>
          );
        }
        break;
      case "dispatch_resolution":
        if (isDispatchResolutionStructure(document.content)) {
          const {
            header,
            date_line,
            resolution,
            footer
          } = document.content;
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFDispatchResolution
                header={header}
                date_line={date_line}
                resolution={resolution}
                footer={footer}
              />
            </PDFViewer>
          );
        }
        break;
      case "resolution":
          if (isLegalResolutionStructure(document.content)) {
            const {
              header,
              date_line,
              resolution,
              footer
            } = document.content;
            return (
              <PDFViewer className="h-[65vh] w-full">
                <PDFLegalResolution
                  header={header}
                  date_line={date_line}
                  resolution={resolution}
                  footer={footer}
                />
              </PDFViewer>
            );
          }
          break;
      case "exceptions":
        if (isDemandExceptionStructure(document.content)) {
          const {
            header,
            court = "S.J.L.",
            opening,
            summary,
            exceptions,
            main_request,
            additional_requests,
          } = document.content;
          return (
            <PDFViewer className="h-[65vh] w-full">
              <PDFDemandException
                header={header}
                court={court}
                opening={opening}
                summary={summary}
                exceptions={exceptions}
                main_request={main_request}
                additional_requests={additional_requests}
              />
            </PDFViewer>
          );
        }
        break;
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
    if (documents.length > 0) {
      setSelectedDocument(documents[0]);
      setTimeout(() => setSelectedDocument(null), 1000);
    }
  },[]);

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
              {/* <ButtonPrimary label="Descargar PDF" onClick={handleDownload} /> */}
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
              {documents.map((doc) => (
                <li key={doc.id} className="py-2">
                  <button
                    type="button"
                    onClick={() => setSelectedDocument(doc)}
                    className="flex justify-between items-center w-full text-left px-4 py-2 hover:bg-gray-100 rounded-md"
                    >
                    <span>{doc.name}</span>
                    <span className="text-sm text-gray-500">
                      {format(new Date(doc.created_at), "yyyy-MM-dd")}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          renderDocumentContent(selectedDocument)
        )}
      </Modal>
      <FullPageOverlay isVisible={docLoading} toastMessage={toastMessage} />
    </>
  );
};

export default ModalDocuments;
