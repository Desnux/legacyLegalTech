"use client";

import { IChangeEvent } from "@rjsf/core";
import Form from "@rjsf/mui";
import { ErrorListProps, RJSFValidationError } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";
import { ButtonGenerate } from "@/components/button";
import { Message } from "@/components/information";
import { DemandTextInputInformation } from "@/types/demand-text";
import { inputSchema, uiSchema } from "./schema";

const transformErrors = (errors: RJSFValidationError[]) => {
  return errors.map((error) => {
    let message = error.message;

    switch (error.name) {
      case "required":
        message = "Este campo es obligatorio.";
        break;
      case "pattern":
        message = "El formato ingresado no es válido.";
        break;
      case "minimum":
        message = "El valor es demasiado bajo.";
        break;
      case "maximum":
        message = "El valor es demasiado alto.";
        break;
      case "minLength":
        message = `Debe tener al menos ${error.params?.limit} caracteres.`;
        break;
      case "maxLength":
        message = `Debe tener como máximo ${error.params?.limit} caracteres.`;
        break;
      case "enum":
        message = "Debe seleccionar una de las opciones disponibles.";
        break;
      default:
        message = error.message;
    }

    return { ...error, message };
  });
};

const CustomErrorList = ({ errors }: ErrorListProps) => (
  <Message 
    type="error"
    message={errors.length === 1 ? "Hay un error en la información" : `Hay ${errors.length} errores en la información`}
    className="mt-4"
  />
);

interface DemandTextGeneratorProps {
  className?: string;
  loading: boolean;
  information?: DemandTextInputInformation;
  onChange: (data: DemandTextInputInformation) => void;
  onGeneratorSubmit: (data: DemandTextInputInformation | null) => Promise<void>;
}

const DemandTextGenerator = ({ className, loading, information, onChange, onGeneratorSubmit }: DemandTextGeneratorProps) => {
  const onSubmit = async (data: IChangeEvent) => {
    await onGeneratorSubmit(data.formData);
  }

  return (
    <div className={className}>
      <Message
        type="info"
        message="Datos que se usarán para ajustar el texto de demanda."
        className="mb-1"
      />
      <Form
        autoComplete="off"
        formData={information}
        onChange={(data) => onChange(data.formData)}
        onError={() => {}}
        onSubmit={onSubmit}
        readonly={loading}
        schema={inputSchema}
        templates={{ ErrorListTemplate: CustomErrorList }}
        transformErrors={transformErrors}
        uiSchema={uiSchema}
        validator={validator}
      >
        <div>
          <ButtonGenerate className="w-full mt-8" disabled={loading} label="Ajustar y generar"/>
        </div>
      </Form>
    </div>
  );
};

export default DemandTextGenerator;
