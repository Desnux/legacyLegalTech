import classNames from "classnames";
import { Analysis } from "@/types/analysis";

const CenteredText = ({ text, className, analysis }: { text: string, className?: string, analysis?: Analysis }) => {
  const status = analysis?.status;

  return (
    <div className={classNames(
      "text-center",
      {
        "bg-green-100 hover:bg-green-200": status === "good",
        "bg-yellow-100 hover:bg-yellow-200": status === "warning",
        "bg-red-100 hover:bg-red-200": status === "error",
      },
      className
    )}>
      {text}
    </div>
  );
};

export default CenteredText;
