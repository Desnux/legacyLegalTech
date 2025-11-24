import React, { useRef, useState } from "react";
import classNames from "classnames";
import { IconPlus, IconX } from "@tabler/icons-react";

interface DollarCertificateProps {
  label?: string;
  setValue: any;
  watch: any;
}

const DollarCertificate = ({ label = "Certificado de dólar", setValue, watch }: DollarCertificateProps) => {
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const currentFile = watch("dollarCertificate");

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file) {
      if (file.type !== "application/pdf") {
        setError("Solo se permiten archivos en formato PDF.");
        return;
      }
      setValue("dollarCertificate", file);
      setError(null);
    } else {
      setValue("dollarCertificate", null);
    }

    event.target.value = ""; // Restablece el valor del input para evitar problemas al volver a agregar el mismo archivo
  };

  const handleRemoveFile = () => {
    setValue("dollarCertificate", null);
  };

  const handleFileUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex justify-between items-center">
        <label htmlFor="file-upload" className="block cursor-pointer text-sm md:text-base">
          { label }
        </label>
        <div
          onClick={handleFileUploadClick}
          className="group flex items-center px-3 py-2 text-pure-white cursor-pointer bg-teal-green rounded-lg hover:bg-teal-green/90 transition-all duration-200 shadow-sm hover:shadow-md"
        >
          <div className="text-xs opacity-0 group-hover:opacity-100 w-0 h-0 overflow-hidden group-hover:mr-2 group-hover:w-auto group-hover:h-auto transition-all duration-300">
            Agregar
          </div>
          <IconPlus size={18} />
        </div>
        <input
          id="dollarCertificate"
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept="application/pdf"
          onChange={handleFileUpload}
        />
      </div>

      <div
        className={classNames(
          `flex items-center gap-2 p-2 border rounded-lg bg-gray-50 cursor-pointer ${!currentFile ? 'cursor-pointer' : ''}`,
          { "border-red-500": error },
          { "border-gray-300": !error }
        )}
        onClick={!currentFile ? handleFileUploadClick : undefined}
      >
        {currentFile ? (
          <>
            <span className="flex-grow text-xs md:text-sm">{currentFile.name}</span>
            <button
              onClick={handleRemoveFile}
              className="text-gray-500 hover:text-gray-700"
            >
              <IconX size={16} />
            </button>
          </>
        ) : (
          <span className="text-gray-400 text-xs md:text-sm">
            No se ha seleccionado ningún archivo
          </span>
        )}
      </div>

      {error && <p className="text-xs md:text-sm text-red-600">{error}</p>}
      <p className="mt-1 text-xs md:text-sm text-gray-500">
        Adjunte un archivo PDF que respalde los cálculos si hay montos en USD.
      </p>
    </div>
  );
};

export default DollarCertificate;
