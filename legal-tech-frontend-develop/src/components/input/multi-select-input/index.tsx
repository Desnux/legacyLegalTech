import { useState, useEffect } from "react";
import { UseFormSetValue, UseFormRegister } from "react-hook-form";

interface MultiSelectInputProps {
  name: string;
  options: { label: string, value: string }[];
  label?: string;
  register: UseFormRegister<any>;
  setValue: UseFormSetValue<any>;
  selectedValues?: string[];
  errors?: any;
}

const MultiSelectInput = ({
  name,
  options,
  label,
  register,
  setValue,
  selectedValues = [],
  errors
}: MultiSelectInputProps) => {
  const [selectedItems, setSelectedItems] = useState<string[]>(selectedValues);

  useEffect(() => {
    register(name);
    setValue(name, selectedItems);
  }, [register, name, selectedItems, setValue]);

  const toggleItemSelection = (item: string) => {
    setSelectedItems((prevSelectedItems) => {
      let updatedItems: string[];
      if (prevSelectedItems.includes(item)) {
        updatedItems = prevSelectedItems.filter((i) => i !== item);
      } else {
        updatedItems = [...prevSelectedItems, item];
      }
      setValue(name, updatedItems);
      return updatedItems;
    });
  };

  return (
    <div>
      {label && <label htmlFor={name} className="block mb-2">{label}</label>}
      <div className="border border-gray-300 rounded-lg p-4">
        <p className="mb-2">Select items:</p>
        <div className="flex flex-wrap">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`m-1 px-3 py-1 rounded-full border ${
                selectedItems.includes(option.value)
                  ? "bg-blue-500 text-white border-blue-500"
                  : "border-gray-300 text-gray-700 hover:bg-gray-100"
              }`}
              onClick={() => toggleItemSelection(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MultiSelectInput;
