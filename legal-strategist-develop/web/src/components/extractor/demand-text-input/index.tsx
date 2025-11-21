"use client";

import { useState } from "react";
import { toast } from "react-toastify";
import { v4 as uuidv4 } from "uuid";
import { useForm, FieldErrors, SubmitHandler } from "react-hook-form";
import { ButtonGenerate } from "@/components/button";
import { AdditionalRequestGroup, DollarCertificate, FileGroup, OptionalInfo, TextAreaInput } from "@/components/input";
import { Message } from "@/components/information";
import { ModalDemandTextRequests, MODAL_DEMAND_TEXT_REQUESTS_OPTIONS } from "@/components/modal";
import { FileWithContext } from "@/types/file";
import { DemandTextRequestNature, Request } from "@/types/request";

interface Inputs {
  dollarCertificate?: any;
  bankContent: string;
  reasonContent: string;
  requests: Request[];
  files: FileWithContext[];
}

interface DemandTextInputExtractorProps {
  className?: string;
  loading: boolean;
  onExtractorSubmit: (data: Inputs) => Promise<void>;
}

const DemandTextInputExtractor = ({ className, loading, onExtractorSubmit }: DemandTextInputExtractorProps) => {
  const [isModalDemandTextRequestsOpen, setIsModalDemandTextRequestsOpen] = useState(false);
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<Inputs>({
    defaultValues: {
      requests: MODAL_DEMAND_TEXT_REQUESTS_OPTIONS.filter((_, index) => { return index < 3; }).map(({ label, value }) => { 
        return { label, value, text: "", id: uuidv4() }; 
      }),
      files: [],
    },
  });

  const onAddRequest = (label: string, value: DemandTextRequestNature, text: string, id: string) => {
    setValue("requests", [...watch("requests"), { label, value, text, id }]);
  };

  const onError = (errors: FieldErrors<Inputs>) => {
    if (errors.bankContent || errors.reasonContent) {
      toast.error("Debe completar ambos campos del texto de demanda.");
    }
  };

  const onIncorporate = (content: string) => {
    const requests = watch("requests");
    const originalDocumentRequestIndex = requests.findIndex(({ value }) => value === "indicate_asset_seizure_goods_for_lockdown");
    if (originalDocumentRequestIndex !== -1) {
      const updatedRequests = [...requests];
      const existingRequest = updatedRequests[originalDocumentRequestIndex];
      if (!existingRequest.text?.includes(content)) {
        if (existingRequest.text.length > content.length) {
          updatedRequests[originalDocumentRequestIndex] = {
            ...existingRequest,
            text: existingRequest.text
              ? content + "\n" + existingRequest.text
              : content,
          };
        } else {
          updatedRequests[originalDocumentRequestIndex] = {
            ...existingRequest,
            text: existingRequest.text
              ? existingRequest.text + "\n" + content
              : content,
          };
        }
        setValue("requests", updatedRequests);
      }
    } else {
      setValue("requests", requests.concat({
        value: "indicate_asset_seizure_goods_for_lockdown",
        label: "Señala bienes para la traba del embargo",
        text: content,
        id: uuidv4(),
      }));
    }
  }

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    if (data.files.length > 10) {
      toast.error("No se permite adjuntar más de 10 archivos de deuda.");
      return;
    }
    if (data.files.length < 1) {
      toast.error("Debe adjuntar al menos un archivo de deuda.");
      return;
    }
    await onExtractorSubmit(data);
  };

  return (
    <div className={className}>
      <Message
        type="info"
        message="Ingrese datos y documentos relevantes, el sistema extraerá los datos necesarios para generar un texto de demanda."
        className="mb-6"
      />
      <form onSubmit={handleSubmit(onSubmit, onError)} encType="multipart/form-data" className="flex flex-col gap-y-8 h-full">
        <div className="flex flex-col gap-y-8 flex-1">
          <TextAreaInput
            name="bankContent"
            label="Información del ejecutante"
            placeholder="Representante legales de ejecutante, abogados patrocinantes, etc."
            register={register}
            errors={errors}
            required
          />
          <TextAreaInput
            name="reasonContent"
            label="Motivos de demanda"
            placeholder="Ruega, etc."
            register={register}
            errors={errors}
            required
          />
          <AdditionalRequestGroup 
            label="Otrosíes"
            requests={watch("requests")}
            setRequests={(r) => setValue("requests", r)}
            onAdd={() => setIsModalDemandTextRequestsOpen(true)}
          />
          <FileGroup
            label="Archivos de deuda"
            filesWithContext={watch("files")}
            setFilesWithContext={(f) => setValue("files", f)}
            accept="application/pdf"
          />
          <OptionalInfo
            setValue={setValue}
            watch={watch}
            onIncorporate={onIncorporate}
          />
        </div>
        <ButtonGenerate className="w-full" disabled={loading} label="Extraer y generar"/>
      </form>
      <ModalDemandTextRequests
        isVisible={isModalDemandTextRequestsOpen}
        onClose={() => setIsModalDemandTextRequestsOpen(false)}
        onAddItem={onAddRequest}
        exclude={watch("requests").map(({ value }) => value)}
      />
    </div>
  );
};

export default DemandTextInputExtractor;
export type { Inputs };
