import classNames from "classnames";
import { DemandText, DocumentViewport } from "@/components/document";
import { DemandTextAnalysis, DemandTextStructure } from "@/types/demand-text";

interface DemandTextAnalyzerProps {
  input: DemandTextStructure;
  analysis: DemandTextAnalysis;
  className?: string;
}

const DemandTextAnalyzer = ({ className, input, analysis }: DemandTextAnalyzerProps) => {
  return (
    <div className={classNames("flex flex-col gap-y-8", className)}>
      {analysis?.overall?.feedback && (
        <div className="px-1">
          <h2 className="font-semibold text-base md:text-lg mb-2">Retroalimentación</h2>
          <div className="text-sm md:text-base">{analysis.overall.feedback}</div>
        </div>
      )}
      {analysis?.overall?.improvement_suggestions && (
        <div className="px-1">
          <h2 className="font-semibold text-base md:text-lg mb-2">Posibilidades de mejora</h2>
          <div className="text-sm md:text-base">{analysis.overall.improvement_suggestions}</div>
        </div>
      )}
      <div className="flex flex-col flex-1">
        <h2 className="px-1 font-semibold text-base md:text-lg mb-2">Detalle</h2>
        <DocumentViewport className="flex-1">
          <DemandText {...input} analysis={analysis}/>
        </DocumentViewport>
      </div>
    </div>
  );
};

export default DemandTextAnalyzer;
