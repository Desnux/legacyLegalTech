import { useState } from "react";
import Button from "@/components/button";

interface ModalAddItemProps<T = string> {
  title: string;
  isVisible: boolean;
  onClose: () => void;
  options: { value: T; label: string }[];
  onAddItem: (item: T, additionalText?: string) => void;
  selectionLabel?: string;
  additionalLabel?: string;
  additionalPlaceholder?: string;
  className?: string;
}

const ModalAddItem = <T = string>({ 
  title, 
  isVisible, 
  onClose, 
  options, 
  onAddItem, 
  selectionLabel = "Seleccionar", 
  additionalLabel, 
  additionalPlaceholder, 
  className 
}: ModalAddItemProps<T>) => {
  const [selectedOption, setSelectedOption] = useState<T | null>(null);
  const [additionalText, setAdditionalText] = useState("");

  const handleConfirm = () => {
    if (selectedOption !== null) {
      onAddItem(selectedOption, additionalText);
      setSelectedOption(null);
      setAdditionalText("");
      onClose();
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`bg-pure-white rounded-2xl shadow-xl border border-medium-gray p-6 max-w-md w-full mx-4 ${className || ""}`}>
        <h2 className="text-h3 font-semibold text-petroleum-blue mb-4">{title}</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-small font-semibold text-charcoal-gray mb-2">
              {selectionLabel}
            </label>
            <select
              value={selectedOption as string || ""}
              onChange={(e) => setSelectedOption(e.target.value as T)}
              className="w-full p-3 border border-medium-gray rounded-lg bg-pure-white focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200"
            >
              <option value="">Seleccionar opción</option>
              {options.map((option) => (
                <option key={option.value as string} value={option.value as string}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {additionalLabel && (
            <div>
              <label className="block text-small font-semibold text-charcoal-gray mb-2">
                {additionalLabel}
              </label>
              <input
                type="text"
                value={additionalText}
                onChange={(e) => setAdditionalText(e.target.value)}
                placeholder={additionalPlaceholder}
                className="w-full p-3 border border-medium-gray rounded-lg bg-pure-white focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200"
              />
            </div>
          )}
        </div>
        
        <div className="flex gap-3 justify-end mt-6">
          <Button
            variant="secondary"
            onClick={onClose}
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            disabled={selectedOption === null}
          >
            Confirmar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModalAddItem;
