import { useState } from "react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import classNames from "classnames";
import { IconClipboard, IconClipboardCheck } from "@tabler/icons-react";

interface ButtonCopyProps {
  textToCopy: string;
  className?: string;
  size?: number;
}

const ButtonCopy = ({ textToCopy, className, size = 24 }: ButtonCopyProps) => {
  const [copied, setCopied] = useState<boolean>(false);

  return (
    <CopyToClipboard text={textToCopy} onCopy={() => setCopied(true)} options={{format: "text/plain"}}>
      <div className={classNames(
        "shadow-md rounded-lg bg-white opacity-50 hover:opacity-100 text-blue-500 hover:text-blue-700 p-2 cursor-pointer",
        className,
      )}>
        {copied ? <IconClipboardCheck size={size}/> : <IconClipboard size={size}/>}
      </div>
    </CopyToClipboard>
  );
};

export default ButtonCopy;
