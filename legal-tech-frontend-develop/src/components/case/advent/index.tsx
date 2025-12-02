import React, { useState } from "react";
import { toast } from "react-toastify";
import classNames from "classnames";
import { PDFViewer } from "@react-pdf/renderer";
import Button from "@/components/button";
import { Modal } from "@/components/modal";
import PDFLegalCompromise from "@/components/pdf/pdf-legal-compromise";
import { fetchAdvent } from "@/services/case";
import { CaseProbableStats } from "@/types/case";
import { LegalCompromiseStructure } from "@/types/legal-compromise-structure";

interface AdventProps {
  caseId: string;
  status: string;
  lastEvent: string;
  loading: boolean;
  winner: string | null;
  stats?: CaseProbableStats | null;
  setLoading: (value: boolean) => void;
}

const Advent: React.FC<AdventProps> = ({ caseId, status, lastEvent, loading, setLoading, winner, stats }) => {
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
    if (stats?.days_to_resolve) {
      return stats.days_to_resolve;
    }
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
    if (stats?.compromise_chance) {
      return stats.compromise_chance * 100;
    }
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
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden min-h-[230px] h-full">
          <div className="bg-teal-700 text-white px-6 py-3 min-h-[60px]">
            <h3 className="text-xl font-semibold text-white">Alternativa general: Avenimiento</h3>
          </div>
          <div className="px-7 pt-3 pb-6">
            <p className="text-sm text-gray-600">
              Estadísticamente, dada la forma en que se ha desenvuelto el proceso y la etapa en que éste se encuentra, el
              <span className="text-gray-900"> {getPercentage().toFixed(2)}%</span> de casos similares ha llegado a un avenimiento por
              al menos el <span className="text-gray-900"> {getCompromiseAmount().toFixed(2)}%</span> del monto demandado.
            </p>
            <p className="mt-2 text-sm text-gray-600">
              Esta acción reduciría la duración del caso actual en aproximadamente <span className="text-gray-900">{getDays()}</span> días,
              en comparación con casos que han continuado su tramitación en un juzgado.
            </p>
            <div className="mt-4 text-center hidden">
              <Button
                variant="primary"
                onClick={compromiseData ? () => setShowModal(true) : handleGenerate}
                disabled={loading}
                loading={loading}
              >
                {compromiseData ? "Mostrar" : "Generar"}
              </Button>
            </div>
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
