import classNames from "classnames";

const SubtleLoader = ({ message, className = "py-8 px-4" }: { message: string, className?: string }) => (
    <div className={classNames("flex items-center justify-center", className)}>
      <div className="flex items-center gap-3">
        {/* Spinner sutil con pulso */}
        <div className="relative">
          <div className="w-5 h-5 border-2 border-light-gray/60 rounded-full animate-pulse"></div>
          <div className="absolute top-0 left-0 w-5 h-5 border-2 border-teal-green border-t-transparent rounded-full animate-spin"></div>
        </div>
        {/* Mensaje */}
        <div>
          <p className="text-body-sm text-charcoal-gray font-medium">{message}</p>
          <p className="text-xs text-medium-gray">Esto puede tomar unos segundos...</p>
        </div>
      </div>
    </div>
  );

export default SubtleLoader;