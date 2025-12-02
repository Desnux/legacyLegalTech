import React, { useState, useEffect } from "react";
import classNames from "classnames";
import { DemandTextAnalysis, DemandTextStructure, MissingPaymentArgument } from "@/types/demand-text";
import { AlignedText, RequestText } from "@/components/document";

interface DemandTextProps extends DemandTextStructure {
  analysis?: DemandTextAnalysis;
  className?: string;
  onContentChange?: (updatedContent: DemandTextStructure) => void;
}

const DemandText = ({ 
  header, 
  summary, 
  court, 
  opening, 
  missing_payment_arguments, 
  main_request, 
  additional_requests, 
  analysis, 
  className,
  onContentChange 
}: DemandTextProps) => {
  const [editableContent, setEditableContent] = useState<DemandTextStructure>({
    header,
    summary,
    court,
    opening,
    missing_payment_arguments,
    main_request,
    additional_requests
  });

  useEffect(() => {
    setEditableContent({
      header,
      summary,
      court,
      opening,
      missing_payment_arguments,
      main_request,
      additional_requests
    });
  }, [header, summary, court, opening, missing_payment_arguments, main_request, additional_requests]);

  const handleContentChange = (field: keyof DemandTextStructure, value: string | MissingPaymentArgument[]) => {
    const updatedContent = {
      ...editableContent,
      [field]: value
    };
    setEditableContent(updatedContent);
    onContentChange?.(updatedContent);
  };

  const zippedArguments = (editableContent.missing_payment_arguments || []).map((item, index) => {
    return {argument: item.argument, analysis: (analysis?.missing_payment_arguments || [])[index]}
  });

  return (
    <div className={
      classNames(
        "w-full bg-white text-gray-900 text-justify text-[12px] sm:text-sm md:text-base leading-6",
        "flex flex-col justify-start space-y-4",
        className,
      )
    }>
      <div className="flex flex-col gap-y-4 md:gap-y-6">
        {editableContent.header && (
          <div className="mb-8 md:mb-10">
            <AlignedText 
              text={editableContent.header}
              className="font-semibold"
              isEditable={true}
              onContentChange={(value) => handleContentChange('header', value)}
            />
          </div>
        )}
        {editableContent.summary && (
          <div 
            contentEditable
            suppressContentEditableWarning
            className="mb-8 md:mb-10 text-center italic whitespace-pre-line outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            onBlur={(e) => handleContentChange('summary', e.currentTarget.textContent || '')}
            dangerouslySetInnerHTML={{ __html: editableContent.summary }}
          />
        )}
        {editableContent.court && (
          <div 
            contentEditable
            suppressContentEditableWarning
            className="font-bold mb-8 md:mb-10 text-center text-lg whitespace-pre-line outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            onBlur={(e) => handleContentChange('court', e.currentTarget.textContent || '')}
            dangerouslySetInnerHTML={{ __html: editableContent.court }}
          />
        )}
        {editableContent.opening && (
          <div 
            contentEditable
            suppressContentEditableWarning
            className="mb-4 whitespace-pre-line outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            onBlur={(e) => handleContentChange('opening', e.currentTarget.textContent || '')}
            dangerouslySetInnerHTML={{ __html: editableContent.opening }}
          />
        )}
        {zippedArguments && zippedArguments.map(({ argument, analysis }, index) => (
          <div 
            key={index}
            contentEditable
            suppressContentEditableWarning
            className="mb-4 whitespace-pre-line outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            onBlur={(e) => {
              const updatedArguments = [...(editableContent.missing_payment_arguments || [])];
              updatedArguments[index] = { ...updatedArguments[index], argument: e.currentTarget.textContent || '' };
              handleContentChange('missing_payment_arguments', updatedArguments);
            }}
            dangerouslySetInnerHTML={{ __html: argument }}
          />
        ))}
        {editableContent.main_request && (
          <div 
            contentEditable
            suppressContentEditableWarning
            className="mb-4 whitespace-pre-line outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            onBlur={(e) => handleContentChange('main_request', e.currentTarget.textContent || '')}
            dangerouslySetInnerHTML={{ __html: editableContent.main_request }}
          />
        )}
        {editableContent.additional_requests && (
          <RequestText 
            text={editableContent.additional_requests}
            isEditable={true}
            onContentChange={(value) => handleContentChange('additional_requests', value)}
          />
        )}
      </div>
    </div>
  );
};

export default DemandText;
