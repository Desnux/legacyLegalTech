"use client";

import { useState } from "react";
import { toast } from "react-toastify";
import { useForm, FieldErrors, SubmitHandler } from "react-hook-form";
import classNames from "classnames";
import { IconChevronDown } from "@tabler/icons-react";
import { ButtonGenerate } from "@/components/button";
import { DateInput, FileInput, NumberInput } from "@/components/input";
import { Message } from "@/components/information";

interface Inputs {
  local_police_number: number | null;
  communication_date: string;
  file: FileList | null;
  coopeuch_registry_image: FileList | null;
  transaction_to_self_image: FileList | null;
  payment_to_account_image: FileList | null;
  user_report_image: FileList | null;
  safesigner_report_image: FileList | null;
  mastercard_connect_report_image: FileList | null;
  celmedia_report_image: FileList | null;
}

const getTodayDateString = () => {
  const today = new Date();
  return today.toISOString().split("T")[0];
};

interface PreliminaryMeasureInputExtractorProps {
  className?: string;
  loading: boolean;
  onExtractorSubmit: (data: Inputs) => Promise<void>;
}

const PreliminaryMeasureInputExtractor = ({ className, loading, onExtractorSubmit }: PreliminaryMeasureInputExtractorProps) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(true);
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<Inputs>({
    defaultValues: {
      local_police_number: null,
      communication_date: getTodayDateString(),
      file: null,
      coopeuch_registry_image: null,
      transaction_to_self_image: null,
      payment_to_account_image: null,
      user_report_image: null,
      safesigner_report_image: null,
      mastercard_connect_report_image: null,
      celmedia_report_image: null,
    },
  });

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const formatNumber = (value: string) => {
    const numeric = parseInt(value.replace(/\D/g, ""), 10);
    if (isNaN(numeric)) {
      return null;
    }
    if (numeric < 1) {
      return null;
    }
    return Math.max(Math.min(numeric, 999), 1).toString();
  }

  const onError = (errors: FieldErrors<Inputs>) => {
    if (errors.communication_date) {
      toast.error("Debe indicar una fecha de comunicación.");
    }
    if (errors.file) {
      toast.error("Debe adjuntar un reporte COOPEUCH.");
    }
  };

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    if (data.file === null) {
      toast.error("Debe adjuntar un reporte COOPEUCH.");
      return;
    }
    if (data.file.length !== 1) {
      toast.error("Debe adjuntar solo un reporte COOPEUCH.");
      return;
    }
    await onExtractorSubmit(data);
  };

  return (
    <div className={className}>
      <Message
        type="info"
        message="Ingrese datos y documentos relevantes, el sistema extraerá la información necesaria para generar una medida prejudicial."
        className="mb-6"
      />
      <form onSubmit={handleSubmit(onSubmit, onError)} encType="multipart/form-data" className="flex flex-col gap-y-8 flex-1">
        <div className="flex flex-col gap-y-8 flex-1">
          <NumberInput
            name="local_police_number"
            label="Nº juzgado de policía local"
            register={register}
            formatValue={formatNumber}
            setValue={setValue}
            placeholder="Nº juzgado de policía local"
            errors={errors}
            min={1}
            max={999}
          />
          <DateInput
            name="communication_date"
            label="Fecha de comunicación *"
            register={register}
            setValue={setValue}
            placeholder="Fecha de comunicación al cliente"
            errors={errors}
          />
          <FileInput
            name="file"
            label="Reporte COOPEUCH *"
            register={register}
            errors={errors}
            currentFiles={watch("file")}
            accept="application/pdf"
            required
            setValue={setValue}
          />
          <div className="border border-gray-300 rounded-md md:rounded-lg p-4">
            <div
              className="flex justify-between items-center cursor-pointer"
              onClick={toggleCollapse}
            >
              <h3 className="text-sm flex gap-x-2 items-center md:text-base">Imágenes</h3>
              <IconChevronDown
                size={20}
                className={classNames("transition-transform", {
                  "rotate-180": !isCollapsed,
                })}
              />
            </div>
            {!isCollapsed && (
              <div className="border-t border-gray-300 mt-4 pt-4 flex flex-col gap-2">
                <FileInput
                  name="coopeuch_registry_image"
                  label="Registro COOPEUCH"
                  register={register}
                  errors={errors}
                  currentFiles={watch("coopeuch_registry_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
                <FileInput
                  name="transaction_to_self_image"
                  label="Extracto transacción entre cuentas de su titularidad (fundamento letra b)"
                  register={register}
                  errors={errors}
                  currentFiles={watch("transaction_to_self_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
                <FileInput
                  name="payment_to_account_image"
                  label="Extracto abonos al usuario (fundamento letra c)"
                  register={register}
                  errors={errors}
                  currentFiles={watch("payment_to_account_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
                <FileInput
                  name="user_report_image"
                  label="Extracto relato del usuario"
                  register={register}
                  errors={errors}
                  currentFiles={watch("user_report_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
                <FileInput
                  name="safesigner_report_image"
                  label="Extracto reporte Safesigner"
                  register={register}
                  errors={errors}
                  currentFiles={watch("safesigner_report_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
                <FileInput
                  name="mastercard_connect_report_image"
                  label="Extracto reporte Mastercard Connect"
                  register={register}
                  errors={errors}
                  currentFiles={watch("mastercard_connect_report_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
                <FileInput
                  name="celmedia_report_image"
                  label="Extracto reporte CELMEDIA"
                  register={register}
                  errors={errors}
                  currentFiles={watch("celmedia_report_image")}
                  accept="image/png, image/jpeg"
                  setValue={setValue}
                />
              </div>
            )}
          </div>
        </div>
        <ButtonGenerate className="w-full" disabled={loading} label="Extraer y generar"/>
      </form>
    </div>
  );
};

export default PreliminaryMeasureInputExtractor;
export type { Inputs };
