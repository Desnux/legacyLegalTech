import classNames from "classnames";

const DocumentViewport = ({ children, className }: { children: React. ReactNode, className?: string }) => {
  return (
    <div className={classNames("bg-gray-300 border border-gray-400 rounded-md flex flex-col", className)}>
      <div className="relative flex-1 p-4 md:p-8 overflow-x-auto">
        {children}
      </div>
    </div>
  );
};

export default DocumentViewport;
