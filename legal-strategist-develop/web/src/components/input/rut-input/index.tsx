"use client";

import { UseFormRegister, UseFormSetValue } from "react-hook-form";
import { TextInput } from "@/components/input";
import { checkRut, prettifyRut } from "@/utils/rut";

interface RutInputProps {
  name: string;
  label?: string;
  register: UseFormRegister<any>;
  setValue: UseFormSetValue<any>;
  placeholder?: string;
  errors?: any;
  required?: string | boolean;
  help?: string;
}

const RutInput = ({ name, label = "RUT", register, setValue, placeholder = "1.234.567-8", help, required, errors }: RutInputProps) => {
  return (
    <TextInput
      name={name}
      register={register}
      setValue={setValue}
      errors={errors}
      label={label}
      help={help}
      placeholder={placeholder}
      required={required}
      formatValue={prettifyRut}
      validateValue={(value: string) => checkRut(value) || "RUT inválido"}
      maxLength={12}
    />
  );
};

export default RutInput;
