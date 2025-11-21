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
        "text-white font-semibold py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg text-sm md:text-base",
        {
          "bg-blue-600 hover:bg-blue-500": !disabled,
          "bg-gray-500 cursor-not-allowed": disabled,
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
