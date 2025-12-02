"use client";

import React, { useState, useRef, useEffect } from "react";
import { IconChevronDown, IconChevronUp } from "@tabler/icons-react";
import classNames from "classnames";

export interface DropdownOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface DropdownProps {
  options: DropdownOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  name?: string;
  register?: any;
  setValue?: any;
  watch?: any;
}

const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onChange,
  placeholder = "Seleccionar opción",
  label,
  error,
  disabled = false,
  required = false,
  className = "",
  name,
  register,
  setValue,
  watch
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || "");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Si se usa con react-hook-form
  const formValue = watch ? watch(name) : null;
  const currentValue = formValue || selectedValue;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (value !== undefined) {
      setSelectedValue(value);
    }
  }, [value]);

  const handleSelect = (optionValue: string) => {
    setSelectedValue(optionValue);
    setIsOpen(false);
    
    if (onChange) {
      onChange(optionValue);
    }
    
    if (setValue && name) {
      setValue(name, optionValue, { shouldValidate: true });
    }
  };

  const selectedOption = options.find(option => option.value === currentValue);

  return (
    <div className={classNames("relative", className)}>
      {label && (
        <label className="block text-small font-semibold text-charcoal-gray mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div ref={dropdownRef} className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          className={classNames(
            "w-full flex items-center justify-between px-3 py-2.5 text-left bg-pure-white border rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
            {
              "border-red-500": error,
              "border-medium-gray": !error,
              "bg-light-gray text-medium-gray cursor-not-allowed": disabled,
              "hover:border-teal-green cursor-pointer": !disabled,
              "border-teal-green": isOpen && !disabled
            }
          )}
          disabled={disabled}
        >
          <span className={classNames(
            "text-sm",
            {
              "text-medium-gray": !selectedOption,
              "text-charcoal-gray": selectedOption
            }
          )}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          
          <div className="flex items-center">
            {isOpen ? (
              <IconChevronUp size={16} className="text-medium-gray" />
            ) : (
              <IconChevronDown size={16} className="text-medium-gray" />
            )}
          </div>
        </button>

        {isOpen && (
          <div className="absolute z-[9999] w-full mt-1 bg-pure-white border border-medium-gray rounded-lg shadow-lg max-h-60 overflow-auto">
            {options.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => !option.disabled && handleSelect(option.value)}
                className={classNames(
                  "w-full px-3 py-2.5 text-left text-sm transition-colors duration-200 hover:bg-light-gray",
                  {
                    "bg-teal-green/10 text-teal-green": option.value === currentValue,
                    "text-charcoal-gray": option.value !== currentValue && !option.disabled,
                    "text-medium-gray cursor-not-allowed": option.disabled,
                    "hover:bg-light-gray": !option.disabled
                  }
                )}
                disabled={option.disabled}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && (
        <p className="text-small text-red-500 mt-1">{error}</p>
      )}

      {/* Hidden input for react-hook-form */}
      {register && name && (
        <input
          type="hidden"
          {...register(name)}
          value={currentValue}
        />
      )}
    </div>
  );
};

export default Dropdown; 