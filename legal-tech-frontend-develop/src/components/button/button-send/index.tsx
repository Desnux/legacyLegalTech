import classNames from "classnames";

interface ButtonSendProps {
  className?: string;
  disabled?: boolean;
  onClick: () => void;
}

const ButtonSend = ({ onClick, className, disabled = false }: ButtonSendProps) => {
  return (
    <button
      onClick={onClick}
      className={classNames(
        "text-white py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg text-sm md:text-base",
        {
          "bg-blue-600 hover:bg-blue-500": !disabled,
          "bg-gray-500 cursor-not-allowed": disabled,
        },
        className,
      )}
      disabled={disabled}
      type="button"
    >
      Enviar
    </button>
  );
};

export default ButtonSend;