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
        <div className="flex items-baseline text-body-sm font-medium text-petroleum-blue gap-x-2 mb-2">
          <label htmlFor={name}>{label} *</label>
          {help && (
            <IconInfoCircleFilled
              data-tooltip-id={`password-input-${name}`}
              data-tooltip-content={help}
              className={classNames("text-teal-green hidden md:block translate-y-[3px] w-4 h-4 flex-shrink-0", help && "cursor-help hover:text-teal-green/80 transition-colors duration-200")}
            />
          )}
        </div>
      )}
      <div className="flex rounded-lg">
        {register !== undefined ? (
            <input
            type={showPassword ? "text" : "password"}
            id={name}
            placeholder={placeholder}
            className={classNames("p-3 border rounded-l-lg outline-none bg-pure-white w-full border-medium-gray focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200 text-body-sm", errors?.[name] && "border-red-500 focus:border-red-500 focus:ring-red-500/20")}
            {...register(name, { required: "Debe ingresar su contraseña." })}
          />
        ) : (
          <input
            type={showPassword ? "text" : "password"}
            id={name}
            placeholder={placeholder}
            className={classNames("p-3 border rounded-l-lg outline-none bg-pure-white w-full border-medium-gray focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200 text-body-sm", errors?.[name] && "border-red-500 focus:border-red-500 focus:ring-red-500/20")}
            value={value}
            onChange={onChange ? (e) => onChange(e.target.value) : undefined}
          />
        )}
        <button
          type="button"
          onClick={togglePasswordVisibility}
          className="px-3 py-3 bg-teal-green text-pure-white rounded-r-lg hover:bg-teal-green/90 focus:outline-none focus:ring-2 focus:ring-teal-green/20 transition-all duration-200 flex items-center justify-center"
        >
          {showPassword ? (
            <IconEyeOff size={20} className="transition-transform duration-200" />
          ) : (
            <IconEye size={20} className="transition-transform duration-200" />
          )}
        </button>
      </div>
      {errors?.[name] && (
        <p className="text-red-600 text-small mt-2">{errors[name].message}</p>
      )}
    </div>
  );
};

export default PasswordInput;
