import Button from "@/components/button";

interface ModalConfirmProps {
  isVisible: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}

const ModalConfirm = ({ 
  isVisible, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  confirmText = "Confirmar",
  cancelText = "Cancelar"
}: ModalConfirmProps) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-pure-white rounded-2xl shadow-xl border border-medium-gray p-6 max-w-md w-full mx-4">
        <h2 className="text-h3 font-semibold text-petroleum-blue mb-4">{title}</h2>
        <p className="text-body text-charcoal-gray mb-6">{message}</p>
        
        <div className="flex gap-3 justify-end">
          <Button
            variant="secondary"
            onClick={onClose}
          >
            {cancelText}
          </Button>
          <Button
            variant="primary"
            onClick={onConfirm}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModalConfirm;
