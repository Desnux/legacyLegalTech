"use client";

import { useState } from "react";
import { useForm, FieldErrors, SubmitHandler } from "react-hook-form";
import Button from "@/components/button";
import { FileGroup, Dropdown } from "@/components/input";
import { Message } from "@/components/information";
import { FileWithContext } from "@/types/file";
import { IconAlertTriangleFilled } from '@tabler/icons-react';
import SubtleLoader from "@/components/loading/subtle-loader";
import { EVENT_TYPE_OPTIONS, ResponseTextInputInformation } from "@/types/response-text";

interface ResponseTextInputExtractorProps {
  className?: string;
  loading: boolean;
  extractionLoading?: boolean;
  onExtractorPDFSubmit: (data: ResponseTextInputInformation) => Promise<void>;
  extractedPdfInformation?: ResponseTextInputInformation;  
  selectedEventType: string;
  setSelectedEventType: (eventType: string) => void;
}

const ResponseTextInputExtractor = ({ className, loading, extractionLoading = false, onExtractorPDFSubmit, selectedEventType, setSelectedEventType }: ResponseTextInputExtractorProps) => {
    
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const { handleSubmit, setValue, watch } = useForm<ResponseTextInputInformation>({
      defaultValues: {
          files: [],
      },
      mode: 'onChange'
  });


  const onError = (errors: FieldErrors<ResponseTextInputInformation>) => {
    if (errors.files) {
      const invalids = Object.entries(errors.files).map(([id, fields]) => {
        const failedFields = Object.keys(fields || {}).join(', ');
        return `Archivo ${id}: ${failedFields}`;
      });
  
      console.warn("Errores de validación:", invalids.join('\n'));
    }
  };

  const onSubmitPDF: SubmitHandler<ResponseTextInputInformation> = async (data) => {
    if (data.files.length < 1) {
      setExtractionError("Debes adjuntar al menos un archivo para extraer información.");
      return;
    }
    
    setExtractionError(null);
    try {
      await onExtractorPDFSubmit(data);
    } catch (error) {
      setExtractionError(error instanceof Error ? error.message : "Error al extraer información del PDF");
    }
  };

return (
    <div className={className}>
      <form onSubmit={handleSubmit(onSubmitPDF, onError)} encType="multipart/form-data" className="flex flex-col h-full">
        <div className="flex flex-col gap-y-6 flex-1">

          <Message
            type="info"
            message="Para comenzar seleccione el tipo de respuesta, luego ingrese el archivo de respuesta."
            className="mb-6"
          />

          {/* Selector de Tipo de Evento */}
          <div className="mb-4">
            <Dropdown
              label="Tipo de Respuesta"
              options={EVENT_TYPE_OPTIONS}
              value={selectedEventType}
              onChange={setSelectedEventType}
              placeholder="Selecciona el tipo de respuesta"
              required
            />
          </div>

          <FileGroup
            label="Archivo de respuesta"
            filesWithContext={watch("files") as FileWithContext[]}
            setFilesWithContext={(f) => setValue("files", f)}
            accept="application/pdf"
            type="response"
          />
          
          {/* Botón de extracción */}
          <Button
            variant="primary"
            size="md"
            disabled={!watch("files") || watch("files").length === 0 || extractionLoading}
            onClick={handleSubmit(onSubmitPDF)}
          >
            {extractionLoading ? "Extrayendo información..." : "Extraer información de PDF"}
          </Button>

          {/* Loader sutil durante la extracción */}
          {extractionLoading && (
            <div className="bg-light-gray/50 rounded-lg border border-medium-gray">
              <SubtleLoader message="Extrayendo información del PDF..." />
            </div>
          )}

          {/* Mensaje de error */}
          {extractionError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <IconAlertTriangleFilled size={16} className="text-red-500" />
                <p className="text-red-700 text-sm font-medium">{extractionError}</p>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default ResponseTextInputExtractor;
