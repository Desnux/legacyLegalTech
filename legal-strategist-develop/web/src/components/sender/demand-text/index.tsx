"use client";

import { useState } from "react";
import { toast } from "react-toastify";
import { useForm, FieldErrors, SubmitHandler } from "react-hook-form";
import { ButtonSend } from "@/components/button";
import { LockedInput, FileExtra, FileInput, FileItem, PasswordInput, RutInput } from "@/components/input";
import { ModalConfirm } from "@/components/modal";

interface Inputs {
  contract: FileList | null;
  mandate: FileList | null;
  password: string;
  rut: string;
}

interface DemandTextSenderProps {
  className?: string;
  filled?: boolean;
  loading: boolean;
  onSenderSubmit: (data: Inputs, files: FileItem[]) => Promise<boolean>;
}

const DemandTextSender = ({ className, filled = false, loading, onSenderSubmit }: DemandTextSenderProps) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isModalConfirmOpen, setIsModalConfirmOpen] = useState(false);
  const { register, reset, handleSubmit, setValue, watch, formState: { errors } } = useForm<Inputs>({
    defaultValues: { contract: null, mandate: null, password: "", rut: "" },
  });

  const onError = (errors: FieldErrors<Inputs>) => {
    if (errors.mandate) {
      toast.error("Debe adjuntar un mandato.");
    }
    if (errors.password) {
      toast.error("Debe ingresar una contraseña.");
    }
    if (errors.rut) {
      toast.error("Debe ingresar un RUT válido.");
    }
  };

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    if (!data.mandate) {
      toast.error("Debe adjuntar un mandato.");
      return;
    }
    setIsModalConfirmOpen(false);
    const valid = await onSenderSubmit(data, files);
    if (valid) {
      reset();
    }
  };

  return (
    <div className={className}>
      <form onSubmit={() => {}} encType="multipart/form-data" className="flex flex-col gap-y-8 h-full">
        <div className="flex flex-col gap-y-8 flex-1">
          <LockedInput 
            label="Texto de demanda"
            placeholder="Debe generar un texto de demanda"
            value={filled ? "Texto de demanda generado" : undefined}
          />
          <FileInput
            name="contract"
            label="Contrato causal"
            register={register}
            errors={errors}
            currentFiles={watch("contract")}
            accept="application/pdf"
            setValue={setValue}
          />
          <FileInput
            name="mandate"
            label="Mandato"
            register={register}
            errors={errors}
            currentFiles={watch("mandate")}
            accept="application/pdf"
            setValue={setValue}
          />
          <FileExtra
            name="extraFiles"
            label="Archivos adicionales"
            filesWithContext={files}
            setFilesWithContext={setFiles}
            accept="application/pdf"
          />
        </div>
        <div className="border-t border-gray-300 h-[1px]"/>
        <RutInput
          name="rut"
          register={register}
          setValue={setValue}
          errors={errors}
          required="Debe ingresar su RUT"
          help="Necesario para automatizar el envío via PJUD"
        />
        <PasswordInput
          name="password"
          label="Clave Poder Judicial"
          register={register}
          errors={errors}
          help="Necesaria para automatizar el envío via PJUD"
        />
        <ButtonSend onClick={() => setIsModalConfirmOpen(true)} className="w-full" disabled={loading || !filled}/>
      </form>
      <ModalConfirm
        isVisible={isModalConfirmOpen}
        title="Confirmar"
        onCancel={() => setIsModalConfirmOpen(false)}
        onConfirm={handleSubmit(onSubmit, onError)}
        message="¿Confirma que desea enviar el texto de demanda y todos los documentos asociados a PJUD?"
      />
    </div>
  );
};

export default DemandTextSender;
