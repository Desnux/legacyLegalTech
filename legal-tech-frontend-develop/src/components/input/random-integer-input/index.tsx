import classNames from "classnames";
import { Tooltip } from "react-tooltip";
import { UseFormRegister, UseFormSetValue } from "react-hook-form";
import { IconRefresh, TablerIcon } from "@tabler/icons-react";

interface RandomIntegerInputProps {
  name: string;
  label?: string;
  register: UseFormRegister<any>;
  setValue: UseFormSetValue<any>;
  errors?: any;
  Icon?: TablerIcon;
  help?: string;
  className?: string;
};

const RandomIntegerInput = ({ name, label, register, setValue, errors, Icon, help, className }: RandomIntegerInputProps) => {
  const randomizeValue = () => {
    const randomValue = Math.floor(Math.random() * 999999);
    setValue(name, randomValue);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const intValue = parseInt(value, 10);

    if (!isNaN(intValue)) {
      setValue(name, intValue);
    }
  };

  return (
    <div className={className}>
      {help && <Tooltip id={`random-integer-input-${name}`}/>}
      {label && (
        Icon 
          ? (
            <div className="flex items-baseline gap-x-2 mb-2">
              <label htmlFor={name}>{label}</label>
              <Icon
                data-tooltip-id={`random-integer-input-${name}`}
                data-tooltip-content={help}
                className={classNames("text-blue-600 translate-y-[2px]", help && "cursor-help hover:text-blue-500")}
                size={14}
              />
            </div>
          ) : (
            <label htmlFor={name} className="block mb-2">{label}</label>
          )
      )}
      <div className="flex rounded-lg text-sm">
        <input
          type="text"
          id={name}
          placeholder="Valor aleatorio"
          className={classNames("p-2 border rounded-l-lg outline-none bg-gray-50 w-full border-gray-300", errors?.[name] && "border-red-500")}
          {...register(name, {
            validate: (value: string) => {
              return value === "" || (Number.isInteger(Number(value)) && !isNaN(Number(value))) || "Value must be an integer";
            },
          })}
          onChange={handleChange}
        />
        <button
          type="button"
          onClick={randomizeValue}
          className="px-3 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-500 focus:outline-none"
        >
          <IconRefresh size={20}/>
        </button>
      </div>
    </div>
  );
};

export default RandomIntegerInput;
