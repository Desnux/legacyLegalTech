import { useState } from "react";
import classNames from "classnames";
import { v4 as uuidv4 } from "uuid";
import { ButtonPrimary, ButtonSecondary } from "@/components/button";
import { Modal } from "@/components/modal";

interface ModalAddItemProps<T = string> {
  title: string;
  isVisible: boolean;
  onClose: () => void;
  options: { label: string, value: T, help?: string }[];
  onAddItem: (label: string, value: T, text: string, id: string) => void;
  selectionLabel?: string;
  additionalLabel: string;
  additionalPlaceholder: string;
  className?: string;
}

const ModalAddItem = <T = string>({ title, isVisible, onClose, options, onAddItem, selectionLabel, additionalLabel, additionalPlaceholder, className }: ModalAddItemProps<T>) => {
  const [selectedOption, setSelectedOption] = useState<{ label: string, value: T, help?: string } | null>(null);
  const [inputText, setInputText] = useState<string>("");

  const handleOptionChange = (option: { label: string, value: T, help?: string }) => {
    setSelectedOption(option);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
  };

  const handleConfirm = () => {
    if (selectedOption) {
      onAddItem(selectedOption.label, selectedOption.value, inputText, uuidv4());
      setInputText("");
      setSelectedOption(null);
      onClose();
    }
  };

  return (
    <Modal
      className={classNames("max-h-[90vh] overflow-hidden text-gray-900", className)}
      isVisible={isVisible}
      onClose={onClose}
      title={title}
      footer={
        <div className="flex justify-end space-x-2">
          <ButtonSecondary label="Cancelar" onClick={onClose}/>
          <ButtonPrimary label="Confirmar" disabled={selectedOption === null} onClick={handleConfirm}/>
        </div>
      }
    >
      <div className="overflow-y-auto max-h-[60vh] mb-4">
        <div className="mb-4">
          {selectionLabel && <p>{selectionLabel}</p>}
          <div className="flex flex-col items-stretch overflow-y-auto py-0.5 gap-y-2">
            {options.map((option, index) => (
              <div key={String(option.value) || index} className="flex flex-col items-stretch px-0.5">
                <button
                  type="button"
                  onClick={() => handleOptionChange(option)}
                  className={classNames(
                    "px-3 py-1 rounded-lg border text-sm md:text-base",
                    selectedOption?.value === option.value && "bg-blue-600 hover:bg-blue-500 text-white border-blue-600 hover:hover:bg-blue-500 font-semibold",
                    selectedOption?.value !== option.value && "border-gray-300 text-gray-700 hover:bg-gray-100",
                    selectedOption?.value === option.value && option.help && "rounded-b-none",
                  )}
                >
                  {option.label}
                </button>
                {option.help && (
                  <div
                    className={classNames(
                      "overflow-hidden transition-all duration-500 ease-in-out rounded-b-md bg-gray-100 text-xs md:text-sm text-gray-600",
                      selectedOption?.value === option.value && "max-h-32 opacity-100",
                      selectedOption?.value !== option.value && "max-h-0 opacity-0",
                    )}>
                      <div className={classNames(
                        "p-2 border-b border-x rounded-b-md",
                        selectedOption?.value === option.value && "border-blue-600",
                        selectedOption?.value !== option.value && "border-transparent",
                      )}>
                        {option.help}
                      </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="mb-4 px-0.5">
          <label className="block mb-2 text-sm md:text-base font-semibold" htmlFor="inputText">
            {additionalLabel}
          </label>
          <textarea
            value={inputText}
            onChange={handleInputChange}
            className="w-full p-2 text-xs md:text-sm border rounded-lg bg-gray-50 outline-none resize-y min-h-16 max-h-48 h-16"
            placeholder={additionalPlaceholder}
            maxLength={1024}
          />
        </div>
      </div>
    </Modal>
  );
};

export default ModalAddItem;
