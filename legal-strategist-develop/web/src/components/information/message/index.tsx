import classNames from "classnames";
import { IconAlertTriangleFilled, IconBellRingingFilled, IconInfoCircleFilled } from "@tabler/icons-react";

type MessageType = "error" | "warning" | "info";

interface MessageProps {
  className?: string;
  message: string;
  type: MessageType;
}

const Message = ({ className, message, type }: MessageProps) => {
  const getClassNames = () => {
    switch (type) {
      case "error":
        return "border text-xs md:text-sm rounded-lg bg-red-100 border-red-200 p-2 text-red-900";
      case "warning":
        return "border text-xs md:text-sm rounded-lg bg-yellow-100 border-yellow-200 p-2 text-yellow-900";
      case "info":
        return "border text-xs md:text-sm rounded-lg bg-blue-100 border-blue-200 p-2 text-blue-900";
      default:
        return "";
    }
  };

  const getIcon = () => {
    switch (type) {
      case "error":
        return <IconAlertTriangleFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-red-500"/>;
      case "warning":
        return <IconBellRingingFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-yellow-500"/>;
      case "info":
        return <IconInfoCircleFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-blue-500"/>;
      default:
        return null;
    }
  };

  return (
    <div className={classNames(getClassNames(), className, "flex items-center gap-x-2")}>
      {getIcon()}
      {message}
    </div>
  );
};

export default Message;
