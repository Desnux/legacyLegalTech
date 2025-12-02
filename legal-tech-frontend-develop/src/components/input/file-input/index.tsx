import { useState, useRef } from "react";
import { UseFormRegister, UseFormSetValue } from "react-hook-form";
import { IconX, IconPlus, IconUpload } from "@tabler/icons-react";
import Button from "@/components/button";
import classNames from "classnames";

interface FileInputProps {
  name: string;
  label?: string;
  register: UseFormRegister<any>;
  errors?: Record<string, any>;
  className?: string;
  currentFiles: FileList | null;
  accept?: string;
  multiple?: boolean;
  setValue: UseFormSetValue<any>;
  required?: string | boolean;
}

const FileInput = ({
  name,
  label,
  register,
  errors,
  className,
  currentFiles,
  accept = "*/*",
  multiple = false,
  required = false,
  setValue,
}: FileInputProps) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const { ref, ...rest } = register(name, {
    validate: (value: FileList | null) => {
      if (value && value.length > 10) return "You can only upload up to 10 files.";
      return true;
    },
  });

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles && droppedFiles.length > 0) {
      if (multiple || droppedFiles.length == 1) {
        setValue(name, droppedFiles, { shouldValidate: true });
      } else {
        setValue(name, droppedFiles[0], { shouldValidate: true });
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget as Node)) {
      return;
    }
    setIsDragging(false);
  };

  const handleFileUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleRemoveFile = (_index: number) => {
    setValue(name, null);
  };

  return (
    <div className={className}>
      <div className="flex gap-x-1 justify-between items-end mb-2">
        {label && <label htmlFor={name} className="block cursor-pointer text-sm md:text-base">{label}</label>}
        <div 
          onClick={handleFileUploadClick}
          className="group flex items-center px-3 py-2 text-pure-white cursor-pointer bg-teal-green rounded-lg hover:bg-teal-green/90 transition-all duration-200 shadow-sm hover:shadow-md"
        >
          <div className="text-xs opacity-0 group-hover:opacity-100 w-0 h-0 overflow-hidden group-hover:mr-2 group-hover:w-auto group-hover:h-auto transition-all duration-300">Agregar</div>
          <IconPlus className="hidden md:block" size={18}/>
          <IconPlus className="md:hidden" size={16}/>
        </div>
        <input
          type="file"
          id={name}
          accept={accept}
          className="hidden"
          {...rest}
          ref={(e) => {
            ref(e);
            fileInputRef.current = e;
          }}
          multiple={multiple}
        />
      </div>
      <div
        className={classNames(
          `border rounded-lg outline-none w-full flex flex-col gap-y-2 min-h-10 md:min-h-12 p-1 ${(currentFiles === null || currentFiles instanceof FileList && currentFiles.length === 0) ? 'cursor-pointer' : ''}`,
          { "border-blue-600 bg-blue-100": isDragging },
          { "border-gray-300 bg-gray-50": !isDragging },
          errors?.[name] && "border-red-500",
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleFileDrop}
        onClick={(currentFiles === null || currentFiles instanceof FileList && currentFiles.length === 0) ? handleFileUploadClick : undefined}
      >
        {currentFiles && Array.from(currentFiles).map((file, index) => (
          <div key={index} className="flex justify-between rounded-lg items-center text-xs md:text-sm shadow-sm border select-none bg-white p-2">
            <div className="flex-1">{file.name}</div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleRemoveFile(index)}
              className="ml-1 p-1"
            >
              <IconX size={16} />
            </Button>
          </div>
        ))}
        {(currentFiles === null || currentFiles.length === 0) && (
          <div className={classNames(
            "items-center justify-center flex-1 flex",
            { "text-blue-400": isDragging },
            { "text-gray-400": !isDragging },
          )}>
            <IconUpload className="hidden md:block" size={24}/>
            <IconUpload className="md:hidden" size={20}/>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileInput;
