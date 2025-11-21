import classNames from "classnames";
import { Analysis } from "@/types/analysis";
import { FeedbackBox } from "@/components/document";

const AlignedText = ({ text, className, analysis }: { text: string, className?: string, analysis?: Analysis }) => {
  const status = analysis?.status;
  const feedback = analysis?.status === "good" ? analysis?.feedback : analysis?.improvement_suggestions;
  const lines = text.trim().split("\n").map(line => {
    const [label, value] = line.split(" : ");
    return { label, value };
  });

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
