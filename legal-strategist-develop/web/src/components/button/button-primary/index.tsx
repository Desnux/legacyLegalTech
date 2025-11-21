import classNames from "classnames";

interface ButtonPrimaryProps {
  label: string;
  onClick: () => void;
  className?: string;
  disabled?: boolean;
}

const ButtonPrimary = ({ label, onClick, className, disabled = false }: ButtonPrimaryProps) => {
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
      type="button"
      disabled={disabled}
    >
      { label }
    </button>
  );
};

export default ButtonPrimary;