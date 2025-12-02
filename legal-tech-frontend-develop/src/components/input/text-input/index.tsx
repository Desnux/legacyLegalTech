import classNames from "classnames";
import { Tooltip } from "react-tooltip";
import { UseFormRegister, UseFormSetValue } from "react-hook-form";
import { IconInfoCircleFilled } from "@tabler/icons-react";

interface TextInputProps {
  name: string;
  label?: string;
  register?: UseFormRegister<any>;
  setValue?: UseFormSetValue<any>;
  formatValue?: (value: string) => string;
  validateValue?: (value: string) => boolean | string;
  placeholder?: string;
  errors?: any;
  help?: string;
  className?: string;
  required?: string | boolean;
  maxLength?: number;
  value?: string;
  onChange?: (value: string) => void;
};

const TextInput = ({ name, label, register, setValue, placeholder, formatValue, validateValue, required = false, errors, help, className, maxLength, value, onChange }: TextInputProps) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    if (onChange) {
      // Controlled mode
      onChange(inputValue);
    } else if (setValue && formatValue !== undefined) {
      // React-hook-form mode with format
      setValue(name, formatValue(inputValue));
    } else if (setValue) {
      // React-hook-form mode without format
      setValue(name, inputValue);
    }
  };

  return (
    <div className={className}>
      {help && <Tooltip id={`text-input-${name}`}/>}
      {label && (
        <div className="flex items-baseline gap-x-2 mb-2">
          <label className="text-body-sm font-medium text-petroleum-blue" htmlFor={name}>{label}</label>
          {help && (
            <IconInfoCircleFilled
              data-tooltip-id={`text-input-${name}`}
              data-tooltip-content={help}
              className={classNames("text-teal-green hidden md:block translate-y-[3px] w-4 h-4 flex-shrink-0", help && "cursor-help hover:text-teal-green/80 transition-colors duration-200")}
            />
          )}
        </div>
      )}
      <div className="flex rounded-lg">
        {register !== undefined ? (
          <input
            autoComplete="off"
            type="text"
            id={name}
            maxLength={maxLength}
            placeholder={placeholder}
            className={classNames("p-3 border rounded-lg outline-none bg-pure-white w-full border-medium-gray focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200 text-body-sm", errors?.[name] && "border-red-500 focus:border-red-500 focus:ring-red-500/20")}
            {...register(name, { required: required, validate: validateValue ? (value: string) => validateValue(value) : undefined })}
            onChange={handleChange}
          />
        ) : (
          <input
            autoComplete="off"
            type="text"
            id={name}
            maxLength={maxLength}
            placeholder={placeholder}
            className={classNames("p-3 border rounded-lg outline-none bg-pure-white w-full border-medium-gray focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200 text-body-sm", errors?.[name] && "border-red-500 focus:border-red-500 focus:ring-red-500/20")}
            value={value}
            onChange={handleChange}
          />
        )}
      </div>
      {errors?.[name] && (
        <p className="text-red-600 text-small mt-2">{errors[name].message}</p>
      )}
    </div>
  );
};

export default TextInput;
