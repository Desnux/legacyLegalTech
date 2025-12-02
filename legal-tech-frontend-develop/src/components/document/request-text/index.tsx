import React from "react";
import classNames from "classnames";
import { Analysis } from "@/types/analysis";
import { FeedbackBox } from "@/components/document";

const DEFAULT_BOLD_WORDS = [
  "POR TANTO",
  "POR LO TANTO",
  "Ruego a US.",
  "RUEGO A US.",
  "SOLICITO A US.",
]

interface RequestTextProps {
  text: string;
  boldWords?: string[];
  className?: string;
  analysis?: Analysis;
  isEditable?: boolean;
  onContentChange?: (value: string) => void;
}
 
const RequestText =({ text, boldWords = DEFAULT_BOLD_WORDS, className, analysis, isEditable = false, onContentChange }: RequestTextProps) => {
  const regex = new RegExp(`(${boldWords.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, "g");
  const paragraphs = text.split("\n\n");
  const status = analysis?.status;
  const feedback = analysis?.status === "good" ? analysis?.feedback : analysis?.improvement_suggestions;

  if (isEditable) {
    return (
      <div className={classNames(className)}>
        {paragraphs.map((paragraph, index) => {
          const hasColon = paragraph.includes("OTROSÍ:");
          const [boldText, regularText] = hasColon ? paragraph.split(/OTROSÍ:((.|\n)+)/) : [null, paragraph];

          return (
            <div 
              key={index}
              contentEditable
              suppressContentEditableWarning
              className="outline-none rounded px-3 py-2 hover:bg-gray-50 transition-colors whitespace-pre-line focus:ring-2 focus:ring-blue-300 min-h-[2rem] mb-4"
              onBlur={(e) => {
                const allDivs = e.currentTarget.parentElement?.querySelectorAll('[contenteditable]');
                if (allDivs) {
                  const updatedParts = Array.from(allDivs).map(div => div.textContent || '').filter(text => text.trim());
                  onContentChange?.(updatedParts.join('\n\n'));
                }
              }}
            >
              {hasColon && boldText && (
                <span className="font-bold">
                  {boldText}OTROSÍ:{" "}
                </span>
              )}
              <span>
                {regularText && regularText.trim().split("\n").map((line, i) => (
                  <React.Fragment key={i}>
                    {line.split(regex).map((part, j) => {
                      return regex.test(part) ? (
                        <span key={j} className="font-bold">{part}</span>
                      ) : (
                        <span key={j}>{part}</span>
                      );
                    })}
                    {i !== regularText.trim().split("\n").length - 1 && <span>{"\n"}</span>}
                  </React.Fragment>
                ))}
              </span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className={classNames(
      "group",
      {
        "bg-green-100 hover:bg-green-200": status === "good",
        "bg-yellow-100 hover:bg-yellow-200": status === "warning",
        "bg-red-100 hover:bg-red-200": status === "error",
      },
      className,
    )}>
      {paragraphs.map((paragraph, index) => {
        const hasColon = paragraph.includes("OTROSÍ:");
        const [boldText, regularText] = hasColon ? paragraph.split(/OTROSÍ:((.|\n)+)/) : [null, paragraph];

        return (
          <div key={index} style={{ lineHeight: 1, marginBottom: 9 }}>
            <div style={{ marginBottom: 3 }}>
              {hasColon && boldText && (
                <span style={{ fontWeight: "bold" }}>
                  {boldText}OTROSÍ:{" "}
                </span>
              )}
              <span style={{ marginBottom: 3 }}>
                {regularText && regularText.trim().split("\n").map((line, i) => (
                  <React.Fragment key={i}>
                    {line.split(regex).map((part, j) => {
                      return regex.test(part) ? (
                        <span key={j} style={{ fontWeight: "bold" }}>{part}</span>
                      ) : (
                        <span key={j}>{part}</span>
                      );
                    })}
                    {i !== regularText.trim().split("\n").length - 1 && <span style={{ marginBottom: 3 }}>{"\n"}</span>}
                  </React.Fragment>
                ))}
              </span>
            </div>
          </div>
        );
      })}
      {feedback && status && <FeedbackBox feedback={feedback} status={status} className="m-2"/>}
    </div>
  );
};

export default RequestText;