import React from "react";
import classNames from "classnames";
import { useForm } from "react-hook-form";
import { MissingFieldsPartialForm } from "@/components/corrector";
import { MissingField } from "@/types/field";

const getNestedValue = (obj: any, path: string): any => {
  return path.split(".").reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), obj);
};

interface MissingFieldsFormProps {
  missingFields: MissingField[];
  onSubmit: (data: MissingField[]) => void;
  className?: string;
  disabled?: boolean;
}

const MissingFieldsForm: React.FC<MissingFieldsFormProps> = ({ missingFields, onSubmit, className, disabled = false }) => {
  const { control, handleSubmit } = useForm<Record<string, any>>();

  const submitHandler = (data: Record<string, any>) => {
    const correctedFields: MissingField[] = missingFields.map((missingField) => {
      if (missingField.type === "list" && Array.isArray(missingField.initial_value)) {
        const rootName = missingField.name;
        return {
          ...missingField, 
          corrected_value: missingField.initial_value.map((subField) => { 
            let correctedValue = getNestedValue(data, `${rootName}.${subField.name}`);
            if (correctedValue === "") {
              correctedValue = null
            };
            return {...subField, corrected_value: correctedValue ?? subField.initial_value };
          }),
        };
      }
      let correctedValue = data[missingField.name];
      if (correctedValue === "") {
        correctedValue = null
      };
      return {...missingField, corrected_value: correctedValue ?? missingField.initial_value};
    });
    onSubmit(correctedFields);
  };

  return (
    <div className={classNames(className)}>
      <form
        className="flex flex-col gap-y-4 text-gray-900"
        onSubmit={handleSubmit(submitHandler)}
      >
        <MissingFieldsPartialForm missingFields={missingFields} control={control} disabled={disabled}/>
        <button
          type="submit"
          className={classNames(
            "bg-blue-600 hover:bg-blue-500 text-white py-1.5 mt-4 md:py-2 px-2.5 md:px-4 rounded-lg text-sm md:text-base",
            {
              "bg-blue-600 hover:bg-blue-500": !disabled,
              "bg-gray-500 cursor-not-allowed": disabled,
            },
          )}
        >
          Ajustar
        </button>
      </form>
    </div>
  );
};

export default MissingFieldsForm;
