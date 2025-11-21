import { useState } from "react";
import classNames from "classnames";
import { Tooltip } from "react-tooltip";
import { UseFormRegister } from "react-hook-form";
import { IconInfoCircleFilled, IconEye, IconEyeOff } from "@tabler/icons-react";

interface PasswordInputProps {
  name: string;
  label?: string;
  register?: UseFormRegister<any>;
  errors?: any;
  help?: string;
  placeholder?: string;
  className?: string;
  value?: string;
  onChange?: (value: string) => void;
};

const PasswordInput = ({ name, label, register, errors, placeholder = "Contraseña", help, value, onChange, className }: PasswordInputProps) => {
  const [showPassword, setShowPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className={className}>
      {help && <Tooltip id={`password-input-${name}`}/>}
      {label && (
        <div className="flex items-baseline text-sm md:text-base gap-x-2 mb-2">
          <label htmlFor={name}>{label}</label>
          {help && (
            <IconInfoCircleFilled
              data-tooltip-id={`password-input-${name}`}
              data-tooltip-content={help}
              className={classNames("text-blue-600 hidden md:block translate-y-[3px] w-4 h-4 flex-shrink-0", help && "cursor-help hover:text-blue-500")}
            />
          )}
        </div>
      )}
      <div className="flex rounded-lg text-xs md:text-sm">
        {register !== undefined ? (
            <input
            type={showPassword ? "text" : "password"}
            id={name}
            placeholder={placeholder}
            className={classNames("p-2 border rounded-l-lg outline-none bg-gray-50 w-full border-gray-300", errors?.[name] && "border-red-500")}
            {...register(name, { required: "Debe ingresar su contraseña." })}
          />
        ) : (
          <input
            type={showPassword ? "text" : "password"}
            id={name}
            placeholder={placeholder}
            className={classNames("p-2 border rounded-l-lg outline-none bg-gray-50 w-full border-gray-300", errors?.[name] && "border-red-500")}
            value={value}
            onChange={onChange ? (e) => onChange(e.target.value) : undefined}
          />
        )}
        <button
          type="button"
          onClick={togglePasswordVisibility}
          className="px-2 md:px-3 py-1.5 md:py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-500 focus:outline-none"
        >
          {showPassword ? (
            <>
              <IconEyeOff className="hidden md:block" size={20}/>
              <IconEyeOff className="md:hidden" size={18}/>
            </>
          ) : (
            <>
              <IconEye className="hidden md:block" size={20}/>
              <IconEye className="md:hidden" size={18}/>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default PasswordInput;
