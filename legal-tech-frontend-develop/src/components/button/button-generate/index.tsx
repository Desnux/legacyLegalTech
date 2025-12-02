import classNames from "classnames";

interface ButtonGenerateProps {
  className?: string;
  disabled?: boolean;
  label?: string;
}

const ButtonGenerate = ({ className, disabled = false, label = "Generar" }: ButtonGenerateProps) => {
  return (
    <button 
      className={classNames(
        "text-pure-white font-semibold py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg text-button transition-colors duration-200",
        {
          "bg-teal-green hover:bg-teal-green/90": !disabled,
          "bg-medium-gray cursor-not-allowed": disabled,
        },
        className,
      )}
      disabled={disabled}
      type="submit"
    >
      { label }
    </button>
  );
};

export default ButtonGenerate;
