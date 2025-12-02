"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import classNames from "classnames";
import { Modal } from "@/components/modal";
import Button from "@/components/button";
import { format } from "date-fns";
import { PDFViewer } from "@react-pdf/renderer";
import { Document } from "react-pdf";
import {
  PDFLegalCompromise,
  PDFLegalExceptionResponse, 
  PDFLegalResponse, 
  PDFLegalResolution,
  PDFDemandException,
  PDFDemandText,
  PDFDemandTextCorrection,
  PDFDispatchResolution,
  PDFWithdrawal,
} from "@/components/pdf";
import { isWithdrawalStructure } from "@/types/withdrawal-structure";
import { Spinner } from "@/components/state";
import { FullPageOverlay } from "@/components/loading";
import { isDemandTextCorrectionStructure, isLegalCompromiseStructure, isLegalExceptionResponseStructure, isLegalResponseStructure } from "@/utils/response-text-structure";
import { isDemandExceptionStructure, isDemandTextStructure, isDispatchResolutionStructure, isLegalResolutionStructure } from "@/utils/document-text-structure";

interface Document {
  id: string;
  name: string;
  created_at: string;
  type: string;
  content: Record<string, any> | null;
  generated?: boolean;
  storage_key?: string | null;
}

const PDFURLViewer = dynamic(() => import("@/components/pdf/pdf-url-viewer"), {
  ssr: false,
});

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
    const useURL = !document.generated && document.storage_key !== null;

    if (!document.content && !useURL) {
      return (
        <div className="flex items-center justify-center h-48">
          <p className="text-center text-gray-500">Documento no disponible.</p>
        </div>
      );
    }
  
    if (useURL) {
      return (
        <PDFURLViewer url={document.storage_key!} />
      );
    } else {
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
                              <Button variant="secondary" onClick={handleBackToList}>
                  Volver a la lista
                </Button>
              {/* <ButtonPrimary label="Descargar PDF" onClick={handleDownload} /> */}
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
        {!selectedDocument ? (
          <div className="overflow-y-auto max-h-[60vh] mb-4">
            <div className="flex items-center justify-between px-4 py-2 font-bold text-sm text-gray-700">
              <span>Nombre</span>
              <span>Fecha</span>
            </div>
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