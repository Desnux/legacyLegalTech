import classNames from "classnames";
import { Analysis } from "@/types/analysis";
import { FeedbackBox } from "@/components/document";

const SummaryText = ({ text, className, analysis }: { text: string, className?: string, analysis?: Analysis }) => {
  const status = analysis?.status;
  const lines = text.trim().split(';').filter(Boolean);
  const feedback = analysis?.status === "good" ? analysis?.feedback : analysis?.improvement_suggestions;

  return (
    <div className={classNames(
      "group space-y-2",
      {
        "bg-green-100 hover:bg-green-200": status === "good",
        "bg-yellow-100 hover:bg-yellow-200": status === "warning",
        "bg-red-100 hover:bg-red-200": status === "error",
      },
      className,
    )}>
      {lines.map((line, index) => {
        const [boldText, regularText] = line.split(":");
        return (
          <span key={index}>
            <span className="font-bold">{boldText.trim()}:</span>{" "}
            <span>{regularText?.trim()}</span>{index !== lines.length - 1 && "; "}
          </span>
        );
      })}
      {feedback && status && <FeedbackBox feedback={feedback} status={status} className="m-2"/>}
    </div>
  );
};

export default SummaryText;
