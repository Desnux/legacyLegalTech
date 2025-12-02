import { Milestone } from "@/types/milestone";
import { Event } from "@/types/event";
import GenerateResponse from "../generate-response";
import { useState } from "react";
import { Case } from "@/types/case";

interface LastMilestoneProps {
  lastMilestone: Milestone | null;
  eventsData: Event[];
  handleDocumentClick: (documents: string[]) => void;
  handleAnnexClick: (annexes: string[]) => void;
  caseId: string;
  caseData: Case;
  onReload?: () => void;
}

const LastMilestone: React.FC<LastMilestoneProps> = ({
  lastMilestone,
  eventsData,
  handleDocumentClick,
  handleAnnexClick,
  caseId,
  caseData,
  onReload,
}) => {
  const [isVisibleGenerateResponse, setIsVisibleGenerateResponse] = useState(false);

  const handleCloseGenerateResponse = () => {
    setIsVisibleGenerateResponse(false);
  };

  const actualStage = lastMilestone ? lastMilestone.procedure : '';
  const actualEvent = eventsData.length > 0 ? eventsData[eventsData.length - 1] : null;
  return (
    <div style={{ gridArea: "milestone" }}>
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden min-h-[310px]">
        <div className="bg-teal-700 text-white px-4 py-3 min-h-[60px]">
          <h3 className="text-lg font-semibold">
            Etapa Actual: {actualEvent?.title || actualStage || 'Sin información'}
          </h3>
        </div>
        <div className="p-4">
          <div className="text-black mb-2 text-lg font-semibold">
          {actualStage}
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-semibold text-black">
                FECHA DE TRÁMITE:
              </span>
              <p className="text-gray-700 mt-1">
                {lastMilestone?.procedureDate || '-'}
              </p>
            </div>
            <div>
              <span className="font-semibold text-black">FOLIO:</span>
              <p className="text-gray-700 mt-1">{lastMilestone?.folio || '-'}</p>
            </div>
            <div>
              <span className="font-semibold text-black">DOCUMENTOS:</span>
              <div className="mt-1">
                {lastMilestone && lastMilestone?.document && lastMilestone.document.length > 0 ? (
                  <button
                    onClick={() => handleDocumentClick(lastMilestone.document!)}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Ver documentos ({lastMilestone?.document.length || 0})
                  </button>
                )  : (
                  <span className="text-red-500 text-sm">Sin definir</span>
                )}
              </div>
            </div>
            <div>
              <span className="font-semibold text-black">ANEXOS:</span>
              <div className="mt-1">
                {lastMilestone?.annex && lastMilestone.annex.length > 0 ? (
                  <button
                    onClick={() => handleAnnexClick(lastMilestone.annex!)}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Ver anexos ({lastMilestone?.annex.length || 0})
                  </button>
                ) : (
                  <span className="text-gray-500 text-sm">Sin definir</span>
                )}
              </div>
            </div>
          </div>

          {/* Descripción completa al final */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <span className="font-semibold text-black">
              DESCRIPCIÓN DEL TRÁMITE:
            </span>
            <p className="text-gray-700 mt-2 text-sm leading-relaxed">
              {lastMilestone?.procedureDescription || '-'}
            </p>
            {/* {caseData.details && (
            <div className="mt-4 text-right">
              <button className="bg-teal-green text-white px-4 py-2 rounded-md" onClick={() => {
                setIsVisibleGenerateResponse(true);
              }}>
                Generar Respuesta
              </button>
            </div>
            )} */}
          </div>
        </div>
      </div>
      {/* <GenerateResponse
        isVisible={isVisibleGenerateResponse}
        onClose={handleCloseGenerateResponse}
        onReload={onReload}
        caseId={caseId}
      /> */}
    </div>
  );
};

export default LastMilestone;
