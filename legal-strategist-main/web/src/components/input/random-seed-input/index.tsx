import { IconSeedingFilled } from "@tabler/icons-react";
import { UseFormSetValue, UseFormRegister } from "react-hook-form";
import { RandomIntegerInput } from "@/components/input";

interface RandomSeedInputProps {
  name: string;
  className?: string;
  register: UseFormRegister<any>;
  setValue: UseFormSetValue<any>;
  errors?: any;
};

const RandomSeedInput = ({ name, className, register, setValue, errors }: RandomSeedInputProps) => {
  return (
    <RandomIntegerInput
      name={name}
      label="Semilla"
      register={register}
      setValue={setValue}
      errors={errors}
      Icon={IconSeedingFilled}
      help="Fijar este número permite replicar los valores aleatorios empleados por la inteligencia artificial"
      className={className}
    />
  );
};

export default RandomSeedInput;
