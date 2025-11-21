import React from "react";
import classNames from "classnames";
import { ParagraphText } from "@/components/document";

const LegalDocument = ({ content, className }: { content: string, className?: string }) => {
  return (
    <div className={
      classNames(
        "w-[8.5in] p-[1in] mx-auto bg-white shadow-lg border border-gray-300 overflow-hidden flex flex-col justify-start",
        "font-arial font-medium text-gray-900 text-justify",
        className,
      )
    }>
      <ParagraphText text={content} className="mb-4"/>
    </div>
  );
};

export default LegalDocument;
