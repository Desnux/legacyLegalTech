import classNames from "classnames";
import { IconAlertTriangleFilled, IconBellRingingFilled, IconInfoCircleFilled } from "@tabler/icons-react";

type MessageType = "error" | "warning" | "info" | "success";

interface MessageProps {
  className?: string;
  message: string;
  type: MessageType;
}

const Message = ({ className, message, type }: MessageProps) => {
  const getClassNames = () => {
    switch (type) {
      case "error":
        return "border text-body-sm rounded-lg bg-red-50 border-red-200 p-3 text-red-800";
      case "warning":
        return "border text-body-sm rounded-lg bg-soft-gold/10 border-soft-gold/30 p-3 text-charcoal-gray";
      case "info":
        return "border text-body-sm rounded-lg bg-teal-green/10 border-teal-green/30 p-3 text-petroleum-blue";
      case "success":
        return "border text-body-sm rounded-lg bg-teal-green/10 border-teal-green/30 p-3 text-teal-green";
      default:
        return "";
    }
  };

  const getIcon = () => {
    switch (type) {
      case "error":
        return <IconAlertTriangleFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-red-600"/>;
      case "warning":
        return <IconBellRingingFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-soft-gold"/>;
      case "info":
        return <IconInfoCircleFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-teal-green"/>;
      case "success":
        return <IconAlertTriangleFilled className="translate-y-[1px] w-4 h-4 md:w-5 md:h-5 flex-shrink-0 text-teal-green"/>;
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
