import classNames from "classnames";

const Spinner = ({ className }: { className?: string }) => {
  return (
    <div className={classNames("flex justify-center items-center", className)}>
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"/>
    </div>
  );
};

export default Spinner;
