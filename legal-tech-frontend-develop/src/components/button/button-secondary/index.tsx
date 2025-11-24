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
      className={classNames("bg-petroleum-blue hover:bg-petroleum-blue/90 text-button text-pure-white py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg transition-colors duration-200", className)}
      type="button"
    >
      { label }
    </button>
  );
};

export default ButtonSecondary;