import React from "react";
import classNames from "classnames";
import { Analysis } from "@/types/analysis";
import { FeedbackBox } from "@/components/document";

interface AlignedTextProps {
  text: string;
  className?: string;
  onContentChange?: (value: string) => void;
  isEditable?: boolean;
  analysis?: Analysis;
}

const AlignedText = ({ text, className, onContentChange, isEditable = false, analysis }: AlignedTextProps) => {
  const status = analysis?.status;
  const feedback = analysis?.status === "good" ? analysis?.feedback : analysis?.improvement_suggestions;
  const lines = text.trim().split("\n").map(line => {
    const [label, value] = line.split(" : ");
    return { label, value };
  });

  if (isEditable) {
    return (
      <div className={`flex flex-col gap-1 ${className || ''}`}>
        {lines.map((line, index) => (
          <div key={index} className="flex">
            <span className="font-bold flex-1 pr-2 text-left">{line.label}</span>
            <span className="text-left">: </span>
            <input
              type="text"
              value={line.value || ''}
              onChange={(e) => {
                const newLines = [...lines];
                newLines[index] = { ...newLines[index], value: e.target.value };
                const newText = newLines.map(l => `${l.label} : ${l.value}`).join('\n');
                onContentChange?.(newText);
              }}
              className="flex-1 border-none outline-none bg-transparent text-left"
            />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={classNames(
      "group max-w-full",
      {
        "bg-green-100 hover:bg-green-200": status === "good",
        "bg-yellow-100 hover:bg-yellow-200": status === "warning",
        "bg-red-100 hover:bg-red-200": status === "error",
      },
      className,
    )}>
      <div className="grid gap-x-1 gap-y-1 grid-cols-7 max-w-full">
        {lines.map((line, index) => (
          <div className="contents" key={index}>
            <span className="text-left pr-5 font-bold col-span-3">{line.label}</span>
            <span className="text-left col-span-4">: {line.value}</span>
          </div>
        ))}
      </div>
      {feedback && status && <FeedbackBox feedback={feedback} status={status} className="m-2"/>}
    </div>
  );
};

export default AlignedText;
