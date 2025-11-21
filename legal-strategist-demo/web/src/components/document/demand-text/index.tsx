import React from "react";
import classNames from "classnames";
import { AlignedText, CenteredText, ParagraphText, RequestText, SummaryText } from "@/components/document";
import { DemandTextAnalysis, DemandTextStructure } from "@/types/demand-text";

interface DemandTextProps extends DemandTextStructure {
  analysis?: DemandTextAnalysis;
  className?: string;
}

const DemandText = ({ header, summary, court, opening, missing_payment_arguments, main_request, additional_requests, analysis, className }: DemandTextProps) => {
  const zippedArguments = (missing_payment_arguments || []).map((item, index) => {
    return {argument: item.argument, analysis: (analysis?.missing_payment_arguments || [])[index]}
  });

  return (
    <div className={
      classNames(
        "w-full max-w-[8.5in] p-4 sm:p-8 md:p-[1in] md:w-[8.5in] mx-auto bg-white shadow-lg border border-gray-300 overflow-hidden flex flex-col justify-start",
        "font-arial font-medium text-gray-900 text-justify text-[10px] sm:text-xs md:text-sm",
        className,
      )
    }>
      <div className="flex flex-col gap-y-1 md:gap-y-2">
        {header && <AlignedText text={header} className="mb-4 md:mb-8" analysis={analysis?.header ?? undefined}/>}
        {summary && <SummaryText text={summary} className="mb-4 md:mb-8" analysis={analysis?.summary ?? undefined}/>}
        {court && <CenteredText text={court} className="font-bold mb-4 md:mb-8" analysis={analysis?.court ?? undefined}/>}
        {opening && <ParagraphText text={opening} analysis={analysis?.opening ?? undefined}/>}
        {zippedArguments && zippedArguments.map(({ argument, analysis }, index) => <ParagraphText key={index} text={argument} analysis={analysis ?? undefined}/>)}
        {main_request && <ParagraphText text={main_request} analysis={analysis?.main_request ?? undefined}/>}
        {additional_requests && <RequestText text={additional_requests} analysis={analysis?.additional_requests ?? undefined}/>}
      </div>
    </div>
  );
};

export default DemandText;
