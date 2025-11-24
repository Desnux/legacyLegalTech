"use client";

import { UseFormRegister, UseFormSetValue } from "react-hook-form";
import { TextInput } from "@/components/input";
import { checkRut, checkRutForDemand, prettifyRut, prettifyRutForDemand } from "@/utils/rut";

interface RutInputProps {
  name: string;
  label?: string;
  register: UseFormRegister<any>;
  setValue: UseFormSetValue<any>;
  placeholder?: string;
  errors?: any;
  required?: string | boolean;
  help?: string;
  forDemand?: boolean;
}

const RutInput = ({ name, label = "RUT", register, setValue, placeholder, help, required, errors, forDemand = false }: RutInputProps) => {
  const defaultPlaceholder = forDemand ? "12345678" : "1.234.567-8";
  
  return (
    <TextInput
      name={name}
      register={register}
      setValue={setValue}
      errors={errors}
      label={label}
      help={help}
      placeholder={placeholder || defaultPlaceholder}
      required={required}
      formatValue={forDemand ? prettifyRutForDemand : prettifyRut}
      validateValue={(value: string) => (forDemand ? checkRutForDemand(value) : checkRut(value)) || "RUT inválido"}
      maxLength={12}
    />
  );
};

export default RutInput;
