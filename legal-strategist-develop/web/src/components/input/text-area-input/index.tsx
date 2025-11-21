import React, { useRef, useEffect } from "react";
import classNames from "classnames";
import { UseFormRegister } from "react-hook-form";

interface TextAreaInputProps {
  name: string;
  label?: string;
  register: UseFormRegister<any>;
  errors?: any;
  className?: string;
  required?: boolean;
  height?: string;
  onHeightChange?: (height: string) => void;
  scrollPosition?: number;
  onScrollChange?: (position: number) => void;
  placeholder?: string;
};

const TextAreaInput = ({
  name,
  label,
  register,
  errors,
  className,
  required = false,
  height,
  onHeightChange,
  scrollPosition,
  onScrollChange,
  placeholder,
}: TextAreaInputProps) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const { ref, ...rest } = register(name, { required: required });

  const handleResize = () => {
    if (textareaRef.current && onHeightChange && height !== undefined) {
      onHeightChange(`${textareaRef.current.style.height}`);
    }
  };

  const handleScroll = () => {
    if (textareaRef.current && onScrollChange && scrollPosition !== undefined) {
      onScrollChange(textareaRef.current.scrollTop);
    }
  };

  useEffect(() => {
    if (textareaRef.current && onHeightChange && height !== undefined) {
      textareaRef.current.style.height = height;
    }
    if (textareaRef.current && onScrollChange && scrollPosition !== undefined) {
      textareaRef.current.scrollTop = scrollPosition;
    }
  }, [height, scrollPosition]);

  return (
    <div className={className}>
      {label && <label htmlFor={name} className="block text-sm md:text-base mb-2">{label}</label>}
      <div className="flex rounded-lg">
        <textarea
          id={name}
          placeholder={placeholder}
          className={classNames(
            "p-2 border text-xs md:text-sm rounded-lg outline-none bg-gray-50 w-full border-gray-300 resize-y",
            "min-h-24 max-h-80 h-24",
            errors?.[name] && "border-red-500",
          )}
          {...rest}
          ref={(e) => {
            ref(e);
            textareaRef.current = e;
          }}
          style={onHeightChange && height !== undefined ? { height } : undefined}
          onMouseUp={handleResize}
          onTouchEnd={handleResize}
          onScroll={handleScroll}
        />
      </div>
    </div>
  );
};

export default TextAreaInput;
