import classNames from "classnames";
import { ButtonPrimary, ButtonSecondary } from "@/components/button";
import { Modal } from "@/components/modal";

interface ModalConfirmProps {
  isVisible: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title?: string;
  message?: string;
  className?: string;
}

const ModalConfirm = ({ isVisible, onConfirm, onCancel, title, message, className }: ModalConfirmProps) => {
  return (
    <Modal isVisible={isVisible} onClose={onCancel} title={title} className={classNames("text-gray-900", className)}>
      {message && <p className="mb-4 text-sm md:text-base">{message}</p>}
      <div className="flex justify-end space-x-2 mt-4">
        <ButtonSecondary label="Cancelar" onClick={onCancel}/>
        <ButtonPrimary label="Confirmar" onClick={onConfirm}/>
      </div>
    </Modal>
  );
};

export default ModalConfirm;
