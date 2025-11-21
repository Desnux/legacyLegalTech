import classNames from "classnames";

interface ButtonSecondaryProps {
  label: string;
  onClick: () => void;
  className?: string;
}

const ButtonSecondary = ({ label, onClick, className }: ButtonSecondaryProps) => {
  return (
    <button 
      onClick={onClick}
      className={classNames("bg-gray-600 hover:bg-gray-500 text-sm md:text-base text-white py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg", className)}
      type="button"
    >
      { label }
    </button>
  );
};

export default ButtonSecondary;