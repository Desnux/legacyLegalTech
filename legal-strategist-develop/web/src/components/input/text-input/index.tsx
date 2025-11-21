import classNames from "classnames";
import { Tooltip } from "react-tooltip";
import { UseFormRegister, UseFormSetValue } from "react-hook-form";
import { IconInfoCircleFilled } from "@tabler/icons-react";

interface TextInputProps {
  name: string;
  label?: string;
  register: UseFormRegister<any>;
  setValue: UseFormSetValue<any>;
  formatValue?: (value: string) => string;
  validateValue?: (value: string) => boolean | string;
  placeholder?: string;
  errors?: any;
  help?: string;
  className?: string;
  required?: string | boolean;
  maxLength?: number;
};

const TextInput = ({ name, label, register, setValue, placeholder, formatValue, validateValue, required = false, errors, help, className, maxLength }: TextInputProps) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (formatValue !== undefined) {
      setValue(name, formatValue(value));
    } else {
      setValue(name, value);
    }
  };

  return (
    <div className={className}>
      {help && <Tooltip id={`text-input-${name}`}/>}
      {label && (
        <div className="flex items-baseline gap-x-2 mb-2">
          <label className="text-sm md:text-base" htmlFor={name}>{label}</label>
          {help && (
            <IconInfoCircleFilled
              data-tooltip-id={`text-input-${name}`}
              data-tooltip-content={help}
              className={classNames("text-blue-600 hidden md:block translate-y-[3px] w-4 h-4 flex-shrink-0", help && "cursor-help hover:text-blue-500")}
            />
          )}
        </div>
      )}
      <div className="flex rounded-lg text-xs md:text-sm">
        <input
          autoComplete="off"
          type="text"
          id={name}
          maxLength={maxLength}
          placeholder={placeholder}
          className={classNames("p-2 border rounded-lg outline-none bg-gray-50 w-full border-gray-300", errors?.[name] && "border-red-500")}
          {...register(name, { required: required, validate: validateValue ? (value: string) => validateValue(value) : undefined })}
          onChange={handleChange}
        />
      </div>
    </div>
  );
};

export default TextInput;
