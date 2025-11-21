import { useState } from "react";
import classNames from "classnames";
import { IconCaretDownFilled } from "@tabler/icons-react";
import { MissingFieldsForm } from "@/components/corrector";
import { DemandTextAnalysis, DemandTextCorrectionForm } from "@/types/demand-text";
import { MissingField } from "@/types/field";

const CaretIcon = ({ isOpen }: { isOpen: boolean }) => {
  return (
    <>
      <IconCaretDownFilled 
        size={24}
        className={classNames("hidden md:block transition-all mr-1 group-hover:text-blue-500", { "rotate-180": isOpen, "rotate-0": !isOpen })}
      />
      <IconCaretDownFilled
        size={20}
        className={classNames("md:hidden transition-all mr-1 group-hover:text-blue-500", { "rotate-180": isOpen, "rotate-0": !isOpen })}
      />
    </>
  )
};

interface MissingFieldFormWrapperProps {
  fields: MissingField[];
  index: number;
  onSubmit: (data: MissingField[]) => void;
  label: string;
}

const MissingFieldFormWrapper = ({ label, fields, index, onSubmit }: MissingFieldFormWrapperProps) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <div className="bg-white flex flex-col border border-gray-200 p-2 rounded-lg md:rounded-xl">
      <div className="flex justify-between items-center cursor-pointer group" onClick={() => setIsOpen(!isOpen)}>
        <h3 className="font-semibold text-sm md:text-base select-none">{label} {index + 1}</h3>
        <CaretIcon isOpen={isOpen}/>
      </div>
      <div className={classNames("border-t border-gray-200 mt-2 pt-2", { "block": isOpen, "hidden": !isOpen })}>
        <MissingFieldsForm missingFields={fields} onSubmit={onSubmit}/>
      </div>
    </div>
  );
};

interface DemandTextCorrectorProps {
  analysis?: DemandTextAnalysis;
  correctionForm: DemandTextCorrectionForm;
  className?: string;
  onSubmit: (data: DemandTextCorrectionForm) => void;
}

const DemandTextCorrector = ({ correctionForm, className, onSubmit }: DemandTextCorrectorProps) => {
  const createCorrectedValue = (field: MissingField) => {
    if (field.type === "list" && Array.isArray(field.initial_value)) {
      return {...field, corrected_value: field.initial_value.map((item) => ({
          ...item, corrected_value: item.initial_value,
        })),
      };
    }
    return { ...field, corrected_value: field.initial_value };
  };

  const createUpdatedSection = (section: MissingField[][], index: number | null, data: MissingField[] | null) => {
    return section.map((item, i) => i === index && data ? data : item.map((field) => createCorrectedValue(field)));
  };

  const submitHandler = (type: "bills" | "defendants" | "promissory_notes", data: MissingField[], index: number) => {
    const newData: DemandTextCorrectionForm = {
      defendants:
        type === "defendants"
          ? createUpdatedSection(correctionForm.defendants, index, data)
          : createUpdatedSection(correctionForm.defendants, null, null),
      plaintiffs: createUpdatedSection(correctionForm.plaintiffs, null, null),
      bills:
        type === "bills"
        ? createUpdatedSection(correctionForm.bills, index, data)
        : createUpdatedSection(correctionForm.bills, null, null),
      promissory_notes:
        type === "promissory_notes"
          ? createUpdatedSection(correctionForm.promissory_notes, index, data)
          : createUpdatedSection(correctionForm.promissory_notes, null, null),
      sponsoring_attorneys: createUpdatedSection(
        correctionForm.sponsoring_attorneys,
        null,
        null
      ),
    };
    onSubmit(newData);
  };

  return (
    <div className={classNames("flex flex-col gap-y-8", className)}>
      <div className="text-sm md:text-base">
        Puede hacer uso de los siguientes formularios para ajustar información particular y volver a generar el texto de demanda.
      </div>
      <div className="flex flex-col">
        <h2 className="font-semibold text-base md:text-lg pb-2 relative inline-block self-start">
          <span className="flex items-center justify-start gap-x-3 md:gap-x-4">
            Ejecutados
          </span>
        </h2>
        <div className="flex flex-col gap-y-2">
          {correctionForm.defendants.map((fields, index) => {
            return (
              <MissingFieldFormWrapper
                key={index}
                label="Ejecutado"
                index={index}
                fields={fields}
                onSubmit={(data) => submitHandler("defendants", data, index)}
              />
            );
          })}
        </div>
      </div>
      <div className="flex flex-col">
        <h2 className="font-semibold text-base md:text-lg pb-2 relative inline-block self-start">
          <span className="flex items-center justify-start gap-x-3 md:gap-x-4">
            Archivos de deuda
          </span>
        </h2>
        <div className="flex flex-col gap-y-2">
          {correctionForm.promissory_notes.map((fields, index) => {
            return (
              <MissingFieldFormWrapper
                key={index}
                label="Pagaré"
                index={index}
                fields={fields}
                onSubmit={(data) => submitHandler("promissory_notes", data, index)}
              />
            );
          })}
           {correctionForm.bills.map((fields, index) => {
            return (
              <MissingFieldFormWrapper
                key={index}
                label="Factura"
                index={index}
                fields={fields}
                onSubmit={(data) => submitHandler("bills", data, index)}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default DemandTextCorrector;
