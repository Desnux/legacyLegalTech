import React, { useState, useEffect } from "react";
import classNames from "classnames";
import { ResponseTextStructure } from "@/types/response-text";
import { AlignedText, RequestText } from "@/components/document";

interface ResponseTextProps extends ResponseTextStructure {
  className?: string;
  onContentChange?: (updatedContent: ResponseTextStructure) => void;
  readOnly?: boolean;
}

const ResponseText = ({ 
  header,
  summary,
  court,
  opening,
  compromise_terms,
  main_request,
  additional_requests,
  exception_responses,
  content,
  className,
  onContentChange,
  readOnly = false
}: ResponseTextProps) => {
  const [editableContent, setEditableContent] = useState<ResponseTextStructure>({
    header,
    summary,
    court,
    opening,
    compromise_terms,
    exception_responses,
    main_request,
    additional_requests,
    content
  });

  useEffect(() => {
    setEditableContent({
      header,
      summary,
      court,
      opening,
      compromise_terms,
      exception_responses,
      main_request,
      additional_requests,
      content,
    });
  }, [header, summary, court, opening, compromise_terms, exception_responses, main_request, additional_requests, content]);

  const handleContentChange = (field: keyof ResponseTextStructure, value: string) => {
    const updatedContent = {
      ...editableContent,
      [field]: value
    };
    setEditableContent(updatedContent);
    onContentChange?.(updatedContent);
  };

  const DEFAULT_BOLD_WORDS = [
    "POR TANTO",
    "POR LO TANTO",
    "Ruego a US.",
    "RUEGO A US.",
    "SOLICITO A US.",
  ];

  const formatSummaryText = (text: string): string => {
    const lines = text.trim().split(';').filter(Boolean);
    return lines.map((line) => {
      const [boldText, regularText] = line.split(":");
      if (regularText) {
        return `<span class="font-bold">${boldText.trim()}:</span> ${regularText.trim()}`;
      }
      return line.trim();
    }).join('; ');
  };

  const formatParagraphText = (text: string, boldWords: string[] = DEFAULT_BOLD_WORDS): string => {
    const escapedBoldWords = boldWords.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const regex = new RegExp(`(${escapedBoldWords.join('|')})`, 'g');
    const paragraphs = text.split('\n\n');

    return paragraphs.map((paragraph) => {
      const parts = paragraph.split(regex);
      const formattedParts = parts.map((part) => {
        const isBoldWord = boldWords.some(boldWord => part === boldWord || part.trim() === boldWord.trim());
        
        if (isBoldWord) {
          return `<span class="font-bold">${part}</span>`;
        }
        return part;
      }).join('');
      
      return formattedParts;
    }).join('<br/><br/>');
  };

  const formatRequestText = (text: string, boldWords: string[] = DEFAULT_BOLD_WORDS): string => {
    const escapedBoldWords = boldWords.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const regex = new RegExp(`(${escapedBoldWords.join('|')})`, 'g');
    const paragraphs = text.split('\n\n');

    return paragraphs.map((paragraph) => {
      const hasColon = paragraph.includes('OTROSÍ:');
      let boldText = '';
      let regularText = paragraph;

      if (hasColon) {
        const splitResult = paragraph.split(/OTROSÍ:((.|\n)+)/);
        if (splitResult[0]) {
          boldText = splitResult[0];
        }
        if (splitResult[1]) {
          regularText = splitResult[1];
        }
      }

      const lines = regularText.trim().split('\n');
      const formattedLines = lines.map((line, lineIndex) => {
        const parts = line.split(regex);
        const formattedParts = parts.map((part) => {
          const isBoldWord = boldWords.some(boldWord => part === boldWord || part.trim() === boldWord.trim());
          if (isBoldWord) {
            return `<span class="font-bold">${part}</span>`;
          }
          return part;
        }).join('');
        return lineIndex !== lines.length - 1 ? formattedParts + '<br/>' : formattedParts;
      }).join('');

      let result = '';
      if (hasColon && boldText) {
        result += `<span class="font-bold">${boldText}OTROSÍ: </span>`;
      }
      result += formattedLines;
      
      return result;
    }).join('<br/><br/>');
  };

  return (
    <div className={
      classNames(
        "w-full bg-white text-gray-900 text-justify text-[12px] sm:text-sm md:text-base leading-6",
        "flex flex-col justify-start space-y-4",
        className,
      )
    }>
      <div className="flex flex-col gap-y-2 md:gap-y-4">
        {editableContent.header && (
          <div className="mb-8 md:mb-10">
            <AlignedText 
              text={editableContent.header}
              className="font-semibold"
              isEditable={!readOnly}
              onContentChange={(value) => handleContentChange('header', value)}
            />
          </div>
        )}
        {editableContent.summary && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "mb-6 rounded px-3 py-2",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('summary', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: formatSummaryText(editableContent.summary) }}
          />
        )}
        {editableContent.court && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "font-bold text-center rounded px-3 py-2 text-lg",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('court', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: editableContent.court }}
          />
        )}
        {editableContent.opening && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "mb-4 whitespace-pre-line",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('opening', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: editableContent.opening }}
          />
        )}
        {editableContent.exception_responses && editableContent.exception_responses.length > 0 && (
          <div className="mb-4 space-y-4">
            {editableContent.exception_responses.map((exceptionResponse, index) => (
              <div
                key={index}
                contentEditable={!readOnly}
                suppressContentEditableWarning
                className={classNames(
                  "whitespace-pre-line",
                  !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem] rounded px-1"
                )}
                onBlur={!readOnly ? (e) => {
                  const updatedExceptions = [...editableContent.exception_responses!];
                  updatedExceptions[index] = e.currentTarget.textContent || '';
                  const updatedContent = {
                    ...editableContent,
                    exception_responses: updatedExceptions
                  };
                  setEditableContent(updatedContent);
                  onContentChange?.(updatedContent);
                } : undefined}
                dangerouslySetInnerHTML={{ __html: exceptionResponse }}
              />
            ))}
          </div>
        )}
        {editableContent.compromise_terms && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "mb-4 whitespace-pre-line",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('compromise_terms', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: editableContent.compromise_terms }}
          />
        )}
        {editableContent.content && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "mb-4 whitespace-pre-line",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('content', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: editableContent.content }}
          />
        )}
        {editableContent.main_request && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "mb-4 whitespace-pre-line",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('main_request', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: formatParagraphText(editableContent.main_request) }}
          />
        )}
        {editableContent.additional_requests && (
          <div 
            contentEditable={!readOnly}
            suppressContentEditableWarning
            className={classNames(
              "mb-4 whitespace-pre-line",
              !readOnly && "outline-none focus:ring-2 focus:ring-blue-300 hover:bg-gray-50 transition-colors min-h-[2rem]"
            )}
            onBlur={!readOnly ? (e) => handleContentChange('additional_requests', e.currentTarget.textContent || '') : undefined}
            dangerouslySetInnerHTML={{ __html: formatRequestText(editableContent.additional_requests) }}
          />
        )}
      </div>
    </div>
  );
};

export default ResponseText;

