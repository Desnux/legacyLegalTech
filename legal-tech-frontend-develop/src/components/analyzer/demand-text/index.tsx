import classNames from "classnames";
import { useState, useEffect } from "react";
import { DemandText, DocumentViewport } from "@/components/document";
import { DemandTextAnalysis, DemandTextStructure } from "@/types/demand-text";

interface DemandTextAnalyzerProps {
  input: DemandTextStructure;
  analysis: DemandTextAnalysis;
  className?: string;
  onContentChange?: (updatedContent: DemandTextStructure) => void;
}

const DemandTextAnalyzer = ({ className, input, analysis, onContentChange }: DemandTextAnalyzerProps) => {
  const [currentInput, setCurrentInput] = useState<DemandTextStructure>(input);

  useEffect(() => {
    setCurrentInput(input);
  }, [input]);

  const handleContentChange = (updatedContent: DemandTextStructure) => {
    setCurrentInput(updatedContent);
    onContentChange?.(updatedContent);
  };

  return (
    <div className={classNames("flex flex-col gap-y-8", className)}>

      <div className="bg-red-200 rounded-lg p-4">
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
      </div>
      <div className="flex flex-col flex-1">
        <h2 className="px-1 font-semibold text-base md:text-lg mb-2">Texto de demanda modificable</h2>
        <DocumentViewport className="flex-1">
          <DemandText {...currentInput} analysis={analysis} onContentChange={handleContentChange}/>
        </DocumentViewport>
      </div>
    </div>
  );
};

export default DemandTextAnalyzer;
