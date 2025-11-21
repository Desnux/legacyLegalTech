import React from "react";
import classNames from "classnames";
import { Analysis } from "@/types/analysis";
import { FeedbackBox } from "@/components/document";

const DEFAULT_BOLD_WORDS = [
  "POR LO TANTO",
  "RUEGO A US.",
  "SOLICITO A US.",
]

interface ParagraphTextProps {
  text: string;
  boldWords?: string[];
  className?: string;
  analysis?: Analysis;
}

const ParagraphText = ({ text, boldWords = DEFAULT_BOLD_WORDS, className, analysis }: ParagraphTextProps) => {
  const regex = new RegExp(`(${boldWords.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, "g");
  const paragraphs = text.split("\n\n");
  const status = analysis?.status;
  const feedback = analysis?.status === "good" ? analysis?.feedback : analysis?.improvement_suggestions;

  return (
    <div className={classNames(
      "group flex flex-col gap-y-2",
      {
        "bg-green-100 hover:bg-green-200": status === "good",
        "bg-yellow-100 hover:bg-yellow-200": status === "warning",
        "bg-red-100 hover:bg-red-200": status === "error",
      },
      className,
    )}>
      {paragraphs.map((paragraph, index) => {
        const parts = paragraph.split(regex);
        return (
          <p key={index} className="mb-1">
            {parts.map((part, i) => {
              if (regex.test(part)) {
                return (
                  <strong key={i}>{part}</strong>
                );
              }
              return <span key={i}>{part}</span>;
            })}
          </p>
        );
      })}
      {feedback && status && <FeedbackBox feedback={feedback} status={status} className="m-2"/>}
    </div>
  );
};

export default ParagraphText;
