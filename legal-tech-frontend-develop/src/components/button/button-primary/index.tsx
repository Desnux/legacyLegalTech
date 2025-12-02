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
        "text-pure-white py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg text-button transition-colors duration-200",
        {
          "bg-teal-green hover:bg-teal-green/90": !disabled,
          "bg-medium-gray cursor-not-allowed": disabled,
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