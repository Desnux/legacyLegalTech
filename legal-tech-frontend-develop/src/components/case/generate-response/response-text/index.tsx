import classNames from "classnames";
import { useState, useEffect } from "react";
import { DocumentViewport, ResponseText } from "@/components/document";
import { ResponseTextStructure } from "@/types/response-text";

interface ResponseTextAnalyzerProps {
  input: ResponseTextStructure;
  className?: string;
  onContentChange?: (updatedContent: ResponseTextStructure) => void;
  readOnly?: boolean;
}

const ResponseTextAnalyzer = ({ className, input, onContentChange, readOnly = false }: ResponseTextAnalyzerProps) => {
  const [currentInput, setCurrentInput] = useState<ResponseTextStructure>(input);

  useEffect(() => {
    setCurrentInput(input);
  }, [input]);

  const handleContentChange = (updatedContent: ResponseTextStructure) => {
    setCurrentInput(updatedContent);
    onContentChange?.(updatedContent);
  };

  return (
    <div className={classNames("flex flex-col h-full min-h-0", className)}>
      <div className="flex flex-col flex-1 min-h-0 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        <DocumentViewport className="min-h-full">
          <ResponseText {...currentInput} onContentChange={handleContentChange} readOnly={readOnly}/>
        </DocumentViewport>
      </div>
    </div>
  );
};

export default ResponseTextAnalyzer;
