import classNames from "classnames";

const DocumentViewport = ({ children, className }: { children: React.ReactNode, className?: string }) => {
  return (
    <div className={classNames("flex flex-col items-center justify-center min-h-full bg-gradient-to-br from-gray-100 to-gray-200 p-4", className)}>
      <div className="relative w-full max-w-[8.5in] bg-white shadow-2xl border border-gray-300 rounded-sm overflow-hidden">
        <div className="relative bg-white">
          
          <div className="relative p-8 md:p-12 overflow-x-auto bg-white">
            {children}
          </div>
          
        </div>
        
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-b from-gray-300 to-transparent opacity-30"></div>
          <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-t from-gray-300 to-transparent opacity-30"></div>
          <div className="absolute top-0 left-0 bottom-0 w-1 bg-gradient-to-r from-gray-300 to-transparent opacity-20"></div>
          <div className="absolute top-0 right-0 bottom-0 w-1 bg-gradient-to-l from-gray-300 to-transparent opacity-20"></div>
        </div>
        
        <div className="absolute top-0 right-0 w-0 h-0 border-l-[20px] border-l-transparent border-b-[20px] border-b-gray-400 opacity-20"></div>
      </div>
    </div>
  );
};

export default DocumentViewport;
