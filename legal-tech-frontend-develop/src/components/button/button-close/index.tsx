import classNames from "classnames";
import { IconX } from "@tabler/icons-react";

interface ButtonCloseProps {
  onClick: () => void;
  className?: string;
  size?: number;
}

const ButtonClose = ({ onClick, className, size = 24 }: ButtonCloseProps) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={classNames("text-gray-500 hover:text-gray-700 focus:outline-none", className)}
    >
      <IconX size={size}/>
    </button>
  );
};

export default ButtonClose;