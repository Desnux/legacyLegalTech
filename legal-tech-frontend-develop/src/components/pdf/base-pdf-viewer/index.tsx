"use client";

import classNames from "classnames";
import { LocalizationMap, Viewer, Worker } from "@react-pdf-viewer/core";
import es_ES from "@react-pdf-viewer/locales/lib/es_ES.json";
import "@react-pdf-viewer/core/lib/styles/index.css";
import { defaultLayoutPlugin } from "@react-pdf-viewer/default-layout";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";

interface BasePDFViewerProps {
  className?: string;
  filename?: string;
  url: string;
}

const BasePDFViewer = ({ className, filename = "Document", url }: BasePDFViewerProps) => {
  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    toolbarPlugin: {
      getFilePlugin: {
        fileNameGenerator: () => filename || "Document",
      }
    }
  });

  return (
    <div className={className ? className : classNames("h-[65vh] overflow-y-auto p-4")}>
      <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
        <Viewer
          renderError={(e) => (
            <div className="flex flex-col items-center justify-center h-full">
              <p className="text-center text-gray-500">No fue posible cargar el documento PDF.</p>
              {e.name}
              {e.message}
            </div>
          )}
          fileUrl={url}
          plugins={[defaultLayoutPluginInstance]}
          localization={es_ES as LocalizationMap}
        />
      </Worker>
    </div>
  );  
};

export default BasePDFViewer;
