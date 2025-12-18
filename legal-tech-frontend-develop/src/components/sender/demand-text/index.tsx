"use client";

import { useState } from "react";
import { toast } from "react-toastify";
import { useForm, FieldErrors, SubmitHandler } from "react-hook-form";
import Button from "@/components/button";
import { LockedInput, FileExtra, FileInput, FileItem, PasswordInput, RutInput } from "@/components/input";
import { ModalConfirm } from "@/components/modal";
import { IconSend, IconCheck, IconArrowRight } from "@tabler/icons-react";

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
  debug: boolean;
  setDebug: (debug: boolean) => void;
  onSenderSubmit: (data: Inputs, files: FileItem[]) => Promise<boolean>;
}

const DemandTextSender = ({ className, filled = false, loading, debug, setDebug, onSenderSubmit }: DemandTextSenderProps) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isModalConfirmOpen, setIsModalConfirmOpen] = useState(false);
  const { register, reset, handleSubmit, setValue, watch, formState: { errors } } = useForm<Inputs>({
    defaultValues: { contract: null, mandate: null, password: "", rut: "" },
    mode: 'onChange'
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

  const isFormValid = () => {
    const formData = watch();
    // Si debug es true, solo requiere el mandato
    if (debug) {
      return formData.mandate;
    }
    // Si debug es false (enviar a PJUD), requiere mandato, contraseña y RUT
    return formData.mandate && formData.password && formData.rut && formData.rut.trim() !== '';
  };

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    if (!data.mandate) {
      toast.error("Debe adjuntar un mandato.");
      return;
    }
    
    // Solo validar RUT y contraseña si NO está en modo debug (enviar a PJUD)
    if (!debug) {
      if (!data.password || data.password.trim() === '') {
        toast.error("Debe ingresar una contraseña.");
        return;
      }
      if (!data.rut || data.rut.trim() === '') {
        toast.error("Debe ingresar un RUT válido.");
        return;
      }
    }
    
    setIsModalConfirmOpen(false);
    const valid = await onSenderSubmit(data, files);
    if (valid) {
      reset();
    }
  };

  return (
    <div className={className}>
      <form onSubmit={() => {}} encType="multipart/form-data" className="flex flex-col space-y-8">
        {/* Status Indicator */}
        <div className="bg-teal-green/10 border border-teal-green/20 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-teal-green rounded-full p-1">
              <IconCheck size={16} className="text-pure-white" />
            </div>
            <div>
              <h3 className="text-body-sm font-semibold text-teal-green">
                Texto de demanda generado
              </h3>
              <p className="text-small text-charcoal-gray">
                El documento está listo para ser enviado
              </p>
            </div>
          </div>
        </div>

        {/* File Upload Sections */}
        <div className="space-y-6">
          <div className="bg-light-gray rounded-xl p-6">
            <h3 className="text-h3 font-semibold text-charcoal-gray mb-4">
              Documentos Requeridos
            </h3>
            <div className="space-y-6">
              <FileInput
                name="contract"
                label="Contrato causal"
                register={register}
                errors={errors}
                currentFiles={watch("contract")}
                accept="application/pdf"
                setValue={setValue}
                required="Debe adjuntar un contrato causal"
              />
              <FileInput
                name="mandate"
                label="Mandato *"
                register={register}
                errors={errors}
                currentFiles={watch("mandate")}
                accept="application/pdf"
                setValue={setValue}
                required="Debe adjuntar un mandato"
              />
              <FileExtra
                name="extraFiles"
                label="Archivos adicionales"
                filesWithContext={files}
                setFilesWithContext={setFiles}
                accept="application/pdf"
              />
            </div>
          </div>
        </div>

        <div className="bg-light-gray rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h3 className="text-h3 font-semibold text-charcoal-gray mb-1">
                ¿Quieres enviar al PJUD?
              </h3>
              <p className="text-small text-medium-gray">
                Activa esta opción para enviar directamente al sistema del Poder Judicial
              </p>
            </div>
            <button
              type="button"
              onClick={() => setDebug(!debug)}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors duration-200  ${
                !debug ? 'bg-teal-green' : 'bg-medium-gray'
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-pure-white transition-transform duration-200 ${
                  !debug ? 'translate-x-7' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Credentials Section */}
        {!debug && (
        <div className="bg-light-gray rounded-xl p-6">
          <h3 className="text-h3 font-semibold text-charcoal-gray mb-4">
            Credenciales PJUD
          </h3>
          <div className="space-y-4">
            <RutInput
              name="rut"
              label="Ingresa RUT (sin guión ni dígito verificador)"
              register={register}
              setValue={setValue}
              errors={errors}
              required="Debe ingresar su RUT"
              help="Necesario para automatizar el envío via PJUD"
              forDemand={true}
            />
            <PasswordInput
              name="password"
              label="Clave Poder Judicial"
              register={register}
              errors={errors}
              help="Necesaria para automatizar el envío via PJUD"
            />
          </div>
        </div>
        )}

        {/* Submit Button - Oculto, reemplazado por botón fijo */}
        <div className="pt-4 pb-24 hidden">
          <Button
            onClick={() => setIsModalConfirmOpen(true)}
            variant="primary"
            size="lg"
            fullWidth
            disabled={loading || !filled || !isFormValid()}
            loading={loading}
            icon={<IconSend size={20} />}
            iconPosition="left"
          >
            {loading 
              ? (debug ? "Procesando..." : "Enviando...") 
              : (debug ? "Procesar Texto de Demanda" : "Enviar a PJUD")}
          </Button>
        </div>
        
        {/* Botón fijo para enviar */}
        <div className="fixed bottom-12 left-1/2 transform -translate-x-1/2 z-20">
          <Button
            onClick={() => setIsModalConfirmOpen(true)}
            variant="primary"
            disabled={loading || !filled || !isFormValid()}
            loading={loading}
            className="flex items-center gap-2"
          >
            <span>
              {loading 
                ? (debug ? "Procesando..." : "Enviando...") 
                : (debug ? "Procesar Texto de Demanda" : "Enviar a PJUD")}
            </span>
            <IconArrowRight size={16} />
          </Button>
        </div>
      </form>

      <ModalConfirm
        isVisible={isModalConfirmOpen}
        title="Confirmar Envío"
        onClose={() => setIsModalConfirmOpen(false)}
        onConfirm={handleSubmit(onSubmit, onError)}
        message={
          debug
            ? "¿Confirma que desea procesar el texto de demanda en modo debug (sin envío a PJUD)?"
            : "¿Confirma que desea enviar el texto de demanda y todos los documentos asociados a PJUD?"
        }
      />
    </div>
  );
};

export default DemandTextSender;
