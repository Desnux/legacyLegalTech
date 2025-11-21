import React from "react";
import classNames from "classnames";
import { Analysis } from "@/types/analysis";
import { FeedbackBox } from "@/components/document";

const DEFAULT_BOLD_WORDS = [
  "POR LO TANTO",
  "RUEGO A US.",
  "SOLICITO A US.",
]

interface RequestTextProps {
  text: string;
  boldWords?: string[];
  className?: string;
  analysis?: Analysis;
}

const RequestText =({ text, boldWords = DEFAULT_BOLD_WORDS, className, analysis }: RequestTextProps) => {
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
        if (paragraph.includes(":")) {
          const [boldText, regularText] = paragraph.split(/:((.|\n)+)/);
          return (
            <div key={index} className="mb-1">
              <strong>{boldText}: </strong>
              <span>
                {regularText && regularText.trim().split("\n").map((line, i) => (
                  <React.Fragment key={i}>
                    {line.split(regex).map((part, j) => {
                      return regex.test(part) ? (
                        <strong key={j}>{part}</strong>
                      ) : (
                        <span key={j}>{part}</span>
                      );
                    })}
                    <br />
                  </React.Fragment>
                ))}
              </span>
            </div>
          );
        } else {
          return (
            <div key={index} className={classNames(className)}>
              {paragraph.split("\n").map((line, i) => (
                <React.Fragment key={i}>
                  {line.split(regex).map((part, j) => {
                    return regex.test(part) ? (
                      <strong key={j}>{part}</strong>
                    ) : (
                      <span key={j}>{part}</span>
                    );
                  })}
                  <br />
                </React.Fragment>
              ))}
            </div>
          );
        }
      })}
      {feedback && status && <FeedbackBox feedback={feedback} status={status} className="m-2"/>}
    </div>
  );
};

export default RequestText;