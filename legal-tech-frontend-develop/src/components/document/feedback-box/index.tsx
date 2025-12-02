import classNames from "classnames";
import { IconAlertTriangleFilled, IconCircleCheckFilled, IconBellRingingFilled } from "@tabler/icons-react";
import { AnalysisStatus } from "@/types/analysis";

interface FeedbackBoxProps {
  feedback: string;
  status: AnalysisStatus;
  className?: string;
}

const FeedbackBox = ({ feedback, status, className }: FeedbackBoxProps) => {
  return (
    <div className={classNames(
      "p-2 text-white items-center flex gap-x-2 text-xs rounded-md shadow-lg",
      {
        "bg-cyan-950": status === "good",
        "bg-amber-950": status === "warning",
        "bg-red-950": status === "error",
      },
      className,
    )}>
      <div className={classNames({"group-hover:animate-shake": status !== "good"})}>
        {status === "good" ? (
          <IconCircleCheckFilled size={16}/>
        ) : (
          <>
            {status === "warning" ? (
              <IconBellRingingFilled size={16}/>
            ) : (
              <IconAlertTriangleFilled size={16}/>
            )}
          </>
        )}
      </div>
      <div className="flex-1 pr-4">{feedback}</div>
    </div>
  );
};

export default FeedbackBox;
