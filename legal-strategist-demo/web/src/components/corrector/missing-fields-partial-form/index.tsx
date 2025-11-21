"use client";

import React, { useState } from "react";
import classNames from "classnames";
import { Control, Controller } from "react-hook-form";
import { IconCaretDownFilled } from "@tabler/icons-react";
import { MissingField } from "@/types/field";

const CaretIcon = ({ isOpen }: { isOpen: boolean }) => {
  return (
    <>
      <IconCaretDownFilled 
        size={24}
        className={classNames(
          "hidden md:block transition-all mr-1 group-hover:text-blue-500",
          { "rotate-180": isOpen, "rotate-0": !isOpen },
        )}
      />
      <IconCaretDownFilled
        size={20}
        className={classNames(
          "md:hidden transition-all mr-1 group-hover:text-blue-500",
          { "rotate-180": isOpen, "rotate-0": !isOpen },
        )}
      />
    </>
  );
};

interface MissingFieldsPartialFormProps {
  label?: string;
  missingFields: MissingField[];
  className?: string;
  disabled?: boolean;
  control: Control<Record<string, any>, any>;
  rootName?: string;
}

const MissingFieldsPartialForm: React.FC<MissingFieldsPartialFormProps> = ({ label, control, missingFields, className, rootName = "", disabled = false }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const Body = (
    <div className={classNames("flex flex-col gap-y-4", className)}>
      {missingFields.map((field, index) => {
        const fieldName = rootName ? `${rootName}.${field.name}` : field.name;
        if (field.type === "list" && Array.isArray(field.initial_value)) {
          return (
            <MissingFieldsPartialForm
              label={field.label}
              key={index}
              missingFields={field.initial_value}
              control={control}
              rootName={fieldName}
              disabled={disabled}
            />
          );
        }
        return (
          <div key={index} className="flex flex-col">
            <label htmlFor={fieldName} className="text-sm md:text-base mb-2">
              {field.label}
            </label>
            <Controller
              name={fieldName}
              control={control}
              defaultValue={field.initial_value || ""}
              render={({ field: controllerField }) => {
                if (field.type === "select") {
                  return (
                    <select
                      disabled={disabled}
                      {...controllerField}
                      className="p-2 border rounded-l-lg outline-none bg-gray-50 w-full border-gray-300 text-xs md:text-sm"
                    >
                      <option value="" disabled className="bg-white">
                        Seleccione una opción
                      </option>
                      {field.options?.map((option, idx) => (
                        <option key={idx} value={option.value} className="bg-white">
                          {option.label}
                        </option>
                      ))}
                    </select>
                  );
                } else if (field.type === "number") {
                  return (
                    <input
                      autoComplete="off"
                      type="number"
                      disabled={disabled}
                      {...controllerField}
                      className="p-2 border rounded-l-lg outline-none bg-gray-50 w-full border-gray-300 text-xs md:text-sm"
                    />
                  );
                } else {
                  return (
                    <input
                      autoComplete="off"
                      type="text"
                      disabled={disabled}
                      {...controllerField}
                      className="p-2 border rounded-l-lg outline-none bg-gray-50 w-full border-gray-300 text-xs md:text-sm"
                    />
                  );
                }
              }}
            />
          </div>
        )
      })}
    </div>
  );

  if (label) {
    return (
      <div className="flex flex-col border border-gray-200 p-2 rounded-lg md:rounded-xl">
        <div className="flex justify-between items-center cursor-pointer group" onClick={() => setIsOpen(!isOpen)}>
          <h3 className="font-semibold text-sm md:text-base select-none">{label}</h3>
          <CaretIcon isOpen={isOpen}/>
        </div>
        <div className={classNames("border-t border-gray-200 mt-2 pt-2", { "block": isOpen, "hidden": !isOpen })}>
          {Body}
        </div>
      </div>
    );
  }

  return Body;
};

export default MissingFieldsPartialForm;
