import React, { useState } from "react";
import { toast } from "react-toastify";
import classNames from "classnames";
import { PDFViewer } from "@react-pdf/renderer";
import { ButtonPrimary } from "@/components/button";
import { Modal } from "@/components/modal";
import PDFLegalCompromise from "@/components/pdf/pdf-legal-compromise";
import { fetchAdvent } from "@/services/case";
import { LegalCompromiseStructure } from "@/types/legal-compromise-structure";

interface AdventProps {
  caseId: string;
  status: string;
  lastEvent: string;
  loading: boolean;
  winner: string | null;
  setLoading: (value: boolean) => void;
}

const Advent: React.FC<AdventProps> = ({ caseId, status, lastEvent, loading, setLoading, winner }) => {
  const [compromiseData, setCompromiseData] = useState<LegalCompromiseStructure | null>(null);
  const [showModal, setShowModal] = useState(false);

  const getCompromiseAmount = () => {
    switch (lastEvent) {
      case "demand_start":
        return 90;
      case "dispatch_resolution":
        return 90;
      case "demand_text_correction":
          return 90;
      case "exceptions":
        return 80;
      case "exceptions_response":
        return 75;
      case "resolution":
        return 75;
      default:
        return 75;
    }
  };

  const getDays = () => {
    switch (lastEvent) {
      case "demand_start":
        return 300;
      case "dispatch_resolution":
        return 180;
      case "demand_text_correction":
          return 180;
      case "exceptions":
        return 150;
      case "exceptions_response":
        return 120;
      case "resolution":
        return 120;
      default:
        return 120;
    }
  };

  const getPercentage = () => {
    switch (lastEvent) {
      case "demand_start":
        return 0;
      case "dispatch_resolution":
        return 20;
      case "demand_text_correction":
          return 20;
      case "exceptions":
        return 30;
      case "exceptions_response":
        return 35;
      case "resolution":
        return 35;
      default:
        return 35;
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const data = await fetchAdvent(caseId);
      
      if (data.structured_output) {
        setCompromiseData(data.structured_output);
        toast.success("Avenimiento generado correctamente");
        setShowModal(true);
      } else {
        toast.error("No se pudo generar el avenimiento");
      }
    } catch (error) {
      console.error("Error generando avenimiento:", error);
      toast.error("Error al generar el avenimiento");
    } finally {
      setLoading(false);
    }
  };

  if (status === "active" && getPercentage() !== 0 && winner === null) {
    return (
      <>
        <div className="p-4 border rounded-lg shadow-md">
          <h3 className="text-base md:text-lg font-bold">Alternativa general: Avenimiento</h3>
          <p className="mt-2 text-xs md:text-sm text-gray-600">
            Estadísticamente, dada la etapa en que se encuentra el caso, existe una posibilidad del
            <span className="text-gray-900"> {getPercentage()}%</span> de que se pueda llegar a un avenimiento por el
            <span className="text-gray-900"> {getCompromiseAmount()}%</span> del monto demandado.
          </p>
          <p className="mt-2 text-xs md:text-sm text-gray-600">
            Esta acción reduciría la duración del caso en aproximadamente <span className="text-gray-900">{getDays()}</span> días.
          </p>
          <div className="mt-4 text-center hidden">
            <ButtonPrimary
              label={compromiseData ? "Mostrar" : "Generar"}
              onClick={compromiseData ? () => setShowModal(true) : handleGenerate}
              disabled={loading}
            />
          </div>
        </div>

        {showModal && compromiseData && (
          <Modal
            className={classNames("max-h-[90vh] overflow-hidden text-gray-900")}
            customWidthClassName="w-[90vw] max-w-[950px]"
            isVisible={showModal}
            onClose={() => setShowModal(false)}
            title="Avenimiento Generado"
          >
            <PDFViewer className="h-[65vh] w-full">
              <PDFLegalCompromise {...compromiseData} />
            </PDFViewer>
          </Modal>
        )}
      </>
    );
  } else {
    return null;
  }
};

export default Advent;
